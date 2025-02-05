import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
import ollama

app = FastAPI()

# CORS middleware to allow frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for chat input
class ChatRequest(BaseModel):
    query: str

# Function to scrape website content
def scrape_website():
    url = "https://www.NavotiAnalytics.com"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text from paragraphs and headings
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3'])
            content = " ".join([elem.get_text(strip=True) for elem in text_elements])
            return content[:10000]  # Limit content to avoid context overflow
        return "Could not retrieve website content."
    except Exception as e:
        return f"Error scraping website: {str(e)}"

# Store website content
WEBSITE_CONTENT = scrape_website()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare prompt with website context
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant specialized in Navoti Analytics' content."},
            {"role": "system", "content": f"Context: {WEBSITE_CONTENT}"},
            {"role": "user", "content": request.query}
        ]
        
        # Generate response using Ollama
        response = ollama.chat(
            model="llama3.2",  # You can change model as needed
            messages=messages
        )
        
        return {"answer": response['message']['content']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload