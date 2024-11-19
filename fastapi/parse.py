from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests

def scrape_website(website):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # run without a graphical user interface (GUI).
    options.add_argument("--no-sandbox") # run in containerized environment like Docker.
    options.add_argument("--disable-dev-shm-usage") # Ensures stability when running Chrome in limited environments, such as containers or virtual machines.

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(website)
        time.sleep(10)
        html = driver.page_source
        return html
    finally:
        driver.quit()

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # remove script and style
    for script_or_style in soup(['script','style']):
        script_or_style.extract()

    clean_content = soup.get_text(separator = "\n")
    clean_content = "\n".join(
        line.strip() for line in clean_content.splitlines() if line.strip()
    )

    return clean_content

def split_dom_content(clean_content, max_length = 6000):
    # split into document with length = max_length
    return [
        clean_content[i:i+max_length] for i in range(0,len(clean_content), max_length)
    ]

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "Translate to English only"
)

def parse_with_ollama(dom_chunks):
    parsed_results = []
    parse_description = "condense information into a table"
    for i, chunk in enumerate(dom_chunks, start = 1):
        prompt = template.format(dom_content = chunk, parse_description = parse_description)
        #print(prompt)
        response = requests.post('http://ollama:11434/api/generate', json={
            "prompt": prompt,
            "stream": False,
            "model": "llama3.2"
        })

        print(f"Parsed Batch {i} of {len(dom_chunks)}")

        parsed_results.append({"response": response.json().get("response", "")})  # Extract content from the API response
    return parsed_results
    #return parsed_results
