from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from lib.utils import delete_website, save_website

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World changed"}


# Define a model for the request body
class SaveWebsiteBody(BaseModel):
    url: str


@app.post("/save_website")
async def save_website_endpoint(body: SaveWebsiteBody):
    save_website(body.url)


@app.post("/delete_website")
def delete_website_endpoint(body: SaveWebsiteBody):
    delete_website(body.url)
