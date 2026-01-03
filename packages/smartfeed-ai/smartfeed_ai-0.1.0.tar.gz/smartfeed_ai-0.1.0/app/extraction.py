import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import json
from markitdown import MarkItDown
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

load_dotenv()
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

firecrawl_base_url = os.getenv("FIRECRAWL_URL")
if not firecrawl_base_url:
    raise ValueError("Firecrawl base url key not found. Make sure FIRECRAWL_URL is set in your .env file.")


firecrawl = FirecrawlApp(api_key=firecrawl_api_key, api_url=firecrawl_base_url)


def extract_links(start_url: str):
    crawled_web = firecrawl.crawl(
        start_url,
        limit=100,
        scrape_options={"formats": ["html"]},
        poll_interval=30,
    )

    links_dict = {}

    for page in crawled_web.data:
        html = page.html
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            if href.startswith(("#", "javascript:", "mailto:")):
                continue

            full_url = urljoin(start_url, href)

            if urlparse(full_url).netloc != urlparse(start_url).netloc:
                continue

            links_dict.setdefault(full_url, None)

    #print(links_dict)
    return links_dict


def scrape_website(url: str):
    scraped_web = firecrawl.scrape(url= url,formats=["markdown"],)
    # with open("scraped_data.md", "w", encoding="utf-8") as f:
    #     f.write(scraped_web.markdown)
    return scraped_web.markdown

def convert_files_to_text(file_names, converted_files):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    md = MarkItDown(enable_plugins=False)

    for file_name in file_names:
        file_path = os.path.join(base_dir, file_name)
        converted_file = md.convert(file_path)
        converted_files[file_name] = converted_file.markdown

    return converted_files

def anonymize_output(data: list) -> list:
    if not data:
        return data
    
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    
    anonymized_data = []
    
    for item in data:
        anonymized_item = {}
        
        for key, value in item.items():
            if not value or key == "page_source":
                anonymized_item[key] = value
                continue
            
            text = str(value)
            
            try:
                results = analyzer.analyze(text=text, language='en')
                
                if results:
                    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
                    anonymized_item[key] = anonymized_result.text
                    #print(f"Anonymized {key}: {text} - {anonymized_result.text}")
                else:
                    anonymized_item[key] = value
            except Exception as e:
                anonymized_item[key] = value
        
        anonymized_data.append(anonymized_item)
    
    #print(f"\nAnonymized {len(anonymized_data)} items")
    return anonymized_data

def save_output_file(final_output: str):
    if final_output:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Saved {len(final_output)} items to output.json")
    else:
        print("\n⚠️ No items were extracted, JSON file not created.")