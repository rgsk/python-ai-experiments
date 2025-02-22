from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from lib.db import execute_db_query
from lib.utils import delete_website, get_vector_store, save_website

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


class SaveTextBody(BaseModel):
    content: str
    source: str


@app.post("/save_text")
async def save_text_endpoint(body: SaveTextBody):
    vector_store = get_vector_store("rahul portfolio website")
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(
        [Document(page_content=body.content, metadata={'source': body.source})])
    ids = vector_store.add_documents(doc_splits)
    return ids


class DeleteTextBody(BaseModel):
    source: str


@app.post("/delete_text")
async def delete_text_endpoint(body: DeleteTextBody):
    delete_query = """
    DELETE FROM langchain_pg_embedding
    WHERE cmetadata->>'source' = %s;
    """
    execute_db_query(delete_query, (body.source,))

    return {
        'message': 'deletion successful'
    }
