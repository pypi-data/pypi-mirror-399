from . import cli, extraction
import os
import dspy
from dotenv import load_dotenv
from chonkie import SentenceChunker
import random
from .signature_generator import SignatureGenerator

MAX_LINKS_TO_ANALYZE = 1000
COMPLETION_TOKENS = 0
PROMPT_TOKENS = 0

load_dotenv(override=True)
ai_api_key = os.getenv("LLM_API_KEY")

ai_api_base = os.getenv("LLM_API_BASE")
if not ai_api_base:
    raise ValueError("API base not found. Make sure LLM_API_BASE is set in your .env file.")

model = os.getenv("LLM_MODEL_NAME")
if not model:
    raise ValueError("LLM model not found. Make sure LLM_MODEL_NAME is set in your .env file.")

chunks = int(os.getenv("CHUNK_SIZE", 10000))

lm = dspy.LM(
    model=model,
    api_key=ai_api_key,
    api_base=ai_api_base,
)

dspy.configure(lm=lm)
dspy.settings.configure(track_usage=True, enable_disk_cache=False, enable_memory_cache=False)

chunker = SentenceChunker(
    chunk_size=chunks,
    chunk_overlap=128,
    min_sentences_per_chunk=1
)

class SelectRelevantLinks(dspy.Signature):
    """Determines if a single link is relevant for further scraping based on the user's intent."""
    user_intent = dspy.InputField(desc="A short description of what the user is trying to find or extract.")
    link = dspy.InputField(desc="The full URL of the page to check for relevance.")
    response = dspy.OutputField(desc="A simple 'YES' if the link is relevant, 'NO' if it is not.")

class RecommendFields(dspy.Signature):
    """
    Recommend the most relevant fields to extract based on the user's goal and example scraped content.
    
    Returns two parallel lists:
      - field_names: concise names for each suggested field
      - descriptions: corresponding short explanations of what each field captures
    Each list must have the same length and order.
    """
    user_prompt = dspy.InputField(
        desc="Short description of what the user wants to extract or analyze."
    )
    scraped_data = dspy.InputField(
        desc="Representative sample of scraped text or page content."
    )
    field_names = dspy.OutputField(
        desc=(
            "List of concise, lowercase field names suitable as JSON keys.\n"
        )
    )
    descriptions = dspy.OutputField(
        desc=(
            "List of short descriptions corresponding to each field_name.\n"
            "Each description explains what information that field captures."
        )
    )

recommend_fields = dspy.Predict(RecommendFields)
select_relevant_links = dspy.Predict(SelectRelevantLinks)

def from_prompt(prompt: str, return_type: str = "signature") -> type | str:
    """
    Generate a DSPy signature dynamically from a natural language prompt.
    """
    if return_type not in {"signature", "string"}:
        raise ValueError("return_type must be either 'signature' or 'string'")

    generator = SignatureGenerator()
    result = generator(prompt=prompt)

    signature_string = generator.generate_code(result)
    signature = generator.create_signature_class(result)

    return signature if return_type == "signature" else signature_string

def calculate_tokens(prompt_result):
    global COMPLETION_TOKENS, PROMPT_TOKENS
    usage = prompt_result.get_lm_usage()
    # print("Usage  ", usage)
    if usage:
        COMPLETION_TOKENS += usage[model]['completion_tokens']
        # print("Completion tokens ", COMPLETION_TOKENS)
        PROMPT_TOKENS += usage[model]['prompt_tokens']
        # print("Prompt tokens ", PROMPT_TOKENS)

def get_relevant_links(user_intent, feeds):
    relevant_links = []
    #print(feeds.items())
    for link, _ in feeds.items():
        result = select_relevant_links(user_intent=user_intent, link=link)
        calculate_tokens(result)
        if result.response == "YES":
            relevant_links.append(link)
            if feeds[link] is None:
                feeds[link] = extraction.scrape_website(link)
    return feeds, relevant_links

def get_recommended_fields(user_prompt, feeds, links=None):
    fields = []  
    field_names = []  
    sample_size = 1

    available_content = (
        [l for l, content in feeds.items() if content]
        if not links else [l for l in links if feeds.get(l)]
    )

    for content_idx in available_content:
        page_content = feeds[content_idx]
        chunks = chunker.chunk(page_content)
        sampled_chunks = random.sample(chunks, min(sample_size, len(chunks)))

        for chunk in sampled_chunks:
            result = recommend_fields(
                user_prompt=user_prompt,
                scraped_data=chunk
            )

            if not result.field_names or not result.descriptions:
                continue

            names_from_result = [n.strip() for n in result.field_names.split(",")]
            descriptions = [d.strip() for d in result.descriptions.split(",")]
            new_fields = list(zip(names_from_result, descriptions))

            for name, desc in new_fields:
                if name not in field_names:
                    field_names.append(name)
                    fields.append({"field": name, "description": desc})

            calculate_tokens(result)

    cli.display_suggested_fields(fields)
    return

def get_output_data(user_prompt, fields, data, links=None):
    aggregated = []

    signature_prompt = (
        f"Create a DSPy signature for structured data extraction.\n"
        f"User context: {user_prompt}\n"
        f"Fields to extract: {', '.join(f['name'] for f in fields)}\n"
        f"DSpy output fields must strictly match the fields to extract"
        f"The signature should include input fields for user context and scraped text, "
        f"Each output field should be a list where each element corresponds to one extracted item."
        f"Missing values must be empty strings."
    )

    DynamicExtractSignature = from_prompt(signature_prompt, return_type="signature")

    extract_output_data = dspy.Predict(DynamicExtractSignature)

    # print("Signature Object")
    # print(DynamicExtractSignature)

    items = [(link, data.get(link)) for link in links if link in data] if links else list(data.items())
    for link, content in items:
        if not content:
            continue

        chunks = chunker.chunk(content)
        for chunk_idx, chunk in enumerate(chunks):
            try:
                result = extract_output_data(
                    user_context=f"User context: {user_prompt}",
                    scraped_text=chunk
                )
                #print(result)
                calculate_tokens(result)

                product_lists = {}
                for f in fields:
                   key = f.get("name") 
                   value = getattr(result, key, None) 

                   if value is not None:
                     product_lists[key] = value
                   else:
                    product_lists[key] = []

                max_len = max(len(v) for v in product_lists.values()) if product_lists else 0

                product_lists["page_source"] = [link] * max(1, max_len)

                for k, v in product_lists.items():
                    if len(v) < max_len:
                        product_lists[k] = v + [""] * (max_len - len(v))

                for i in range(max_len):
                    item = {k: v[i] for k, v in product_lists.items()}
                    aggregated.append(item)

            except Exception as e:
                continue

   # print(f"\nTotal items extracted: {len(aggregated)}")
    
    deduplicated = deduplicate_items(aggregated)
   # print(f"\nTotal items after deduplication: {len(deduplicated)}")
    
    return deduplicated


def deduplicate_items(items):
    if not items:
        return items
    
    seen = []
    unique_items = []
    
    for item in items:
        signature = tuple(
            (k, str(v).strip().lower()) 
            for k, v in sorted(item.items()) 
            if k != "page_source" and v and str(v).strip()
        )
        
        if signature not in seen:
            seen.append(signature)
            unique_items.append(item)
    
    return unique_items