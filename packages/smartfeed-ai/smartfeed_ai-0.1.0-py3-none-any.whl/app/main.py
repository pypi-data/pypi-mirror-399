import spacy
from . import cli, prompting, extraction
#spacy.load("en_core_web_lg")

def main():
    feeds = {}
    files = {}
    web_url = None
    relevant_links = []

    input_format = cli.get_input_source()

    # get links / markdown files
    if input_format == "url":
        web_url = cli.get_input_url()
        feeds = cli.get_crawled_links(web_url)
    else:
        files = cli.get_input_converted_files()

    while True:
        user_prompt = cli.get_extraction_prompt()

        # end session
        if user_prompt.lower() == "exit" or user_prompt.lower() == "quit":
            cli.display_cost(prompting.COMPLETION_TOKENS, prompting.PROMPT_TOKENS)
            cli.display_goodbye()
            break

        # display recommended fields (and get scraped data)
        if input_format == "url":
            feeds, relevant_links = prompting.get_relevant_links(user_prompt, feeds)
            prompting.get_recommended_fields(user_prompt, feeds, relevant_links)

        else:
            prompting.get_recommended_fields(user_prompt, files)

        # get fields, anonym choice, output format
        output_fields = cli.get_extraction_fields()
        anonymize = cli.get_anonymization_choice()

        # get final output data
        if input_format == "url":
            final_output = cli.get_final_output(user_prompt, output_fields, 
                                                feeds, relevant_links)
        else: 
            final_output = cli.get_final_output(user_prompt, output_fields, 
                                                files)

        # anonymize
        if anonymize:
            final_output = extraction.anonymize_output(final_output)


        # save file 
        extraction.save_output_file(final_output)


if __name__ == "__main__":
    main()
