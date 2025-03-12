from typing import List

import requests  # type:ignore
from bs4 import BeautifulSoup
from fastapi import APIRouter, Query
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from lib.db import execute_db_query
from lib.utils import get_vector_store

router = APIRouter()


@router.get("/")
async def hello_server():
    return {
        'message': 'Server is running'
    }


class SaveTextBody(BaseModel):
    collection_name: str
    content: str
    source: str


@router.post("/save_text")
async def save_text(body: SaveTextBody):
    vector_store = get_vector_store(body.collection_name)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    cleaned_content = body.content.replace("\x00", "\uFFFD")
    doc_splits = text_splitter.split_documents(
        [Document(page_content=cleaned_content, metadata={'source': body.source})])
    ids = vector_store.add_documents(doc_splits)
    return ids


class DeleteCollectionBody(BaseModel):
    collection_name: str


@router.post("/delete_collection")
async def delete_collection(body: DeleteCollectionBody):
    delete_embeddings_query = """
        DELETE FROM langchain_pg_embedding
WHERE collection_id IN (
      SELECT uuid
      FROM langchain_pg_collection
      WHERE name = %s
  );
    """
    execute_db_query(delete_embeddings_query, (body.collection_name,))

    delete_collection_query = """
        DELETE FROM langchain_pg_collection
        WHERE name = %s
    """
    execute_db_query(delete_collection_query, (body.collection_name, ))

    return {
        'message': 'deletion successful'
    }


class DeleteTextBody(BaseModel):
    collection_name: str
    source: str


@router.post("/delete_text")
async def delete_text(body: DeleteTextBody):
    delete_query = """
        DELETE FROM langchain_pg_embedding
WHERE cmetadata->>'source' = %s
  AND collection_id IN (
      SELECT uuid
      FROM langchain_pg_collection
      WHERE name = %s
  );
    """
    execute_db_query(delete_query, (body.source, body.collection_name))

    return {
        'message': 'deletion successful'
    }


@router.get("/relevant_docs")
async def get_relevant_docs(collection_name: str, query: str, sources: List[str] = Query([]), num_docs=5):
    vector_store = get_vector_store(collection_name)
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={
            "k": num_docs,
            'filter': {'source': {'$in': sources}} if len(sources) > 0 else {},
        }
    )
    retrieved_docs = retriever.invoke(query, )
    return retrieved_docs


def load_website(url: str) -> str:
    """
    Fetches the content of a website and returns its text content.

    :param url: The URL of the website to load.
    :return: Extracted text content from the webpage.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except requests.exceptions.RequestException as e:
        return f"Error loading website: {e}"


@router.get('/webpage-content')
async def get_webpage_content(url: str):
    content = load_website(url)
    return content
