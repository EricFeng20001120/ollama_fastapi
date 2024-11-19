from fastapi import FastAPI, Response, HTTPException
import requests
from pydantic import BaseModel
from parse import scrape_website, extract_body_content, split_dom_content, parse_with_ollama


app = FastAPI()

@app.get('/')
def home():
    return {"hello":"world"}

@app.get('/ask')
def ask(prompt:str):
    res = requests.post('http://ollama:11434/api/generate', json = {
        "prompt": prompt,
        "stream": False,
        "model": "llama3.2"
    })
    return Response(content = res.text, media_type = "application/json")

class WebsiteInput(BaseModel): # Defines the input data for your /scrape/ endpoint.
    url: str


@app.post("/scrape/")
async def scrape_and_extract(website_input: WebsiteInput):
    try: 
        html_content = scrape_website(website_input.url)
        body_content = extract_body_content(html_content)
        dom_chunks = split_dom_content(body_content)
        result = parse_with_ollama(dom_chunks)
        return {"result":result}
    except Exception as e:
        raise HTTPException(status_code=500, detail = str(e))