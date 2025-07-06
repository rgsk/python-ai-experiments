from typing import Any, List

import cv2
import numpy as np
import requests  # type:ignore
from bs4 import BeautifulSoup
from fastapi import APIRouter, Query
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PIL import Image
from pydantic import BaseModel

from examples.predict import predict_image
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


def load_website(url: str) -> dict:
    """
    Fetches the content of a website and returns its title, description, content, and all Open Graph (OG) tags.

    :param url: The URL of the website to load.
    :return: A dictionary with 'title', 'description', 'content', and an 'og' object containing all OG tags.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        soup: Any = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "No Title Found"

        # Extract description from meta tag
        description = soup.find("meta", attrs={"name": "description"})
        description = description["content"].strip(
        ) if description and "content" in description.attrs else "No Description Found"

        # Extract all Open Graph tags
        og_tags = {}
        for meta in soup.find_all("meta"):
            if meta.get("property", "").startswith("og:"):
                og_tags[meta["property"].replace("og:", "")] = meta["content"].strip(
                ) if "content" in meta.attrs else ""

        # Extract text content
        content = soup.get_text(separator=' ', strip=True)

        return {
            "title": title,
            "description": description,
            "og": og_tags,
            "content": content,
        }
    except requests.exceptions.RequestException as e:
        return {
            "title": "Error",
            "description": "Error loading description",
            "og": None,
            "content": f"Error loading website: {e}",
        }


@router.get('/webpage-content')
async def get_webpage_content(url: str):
    result = load_website(url)
    return result


def read_image_from_url(url):
    response = requests.get(url)
    img_array = np.frombuffer(response.content, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


@router.get('/clash-royale-cards')
async def get_clash_royale_cards(url: str):
    # Load the image
    img = read_image_from_url(url)

    # Crop parameters
    start_x = 41
    width = 238
    height = 450
    x_gap = 40

    # List to hold resized cropped images
    resized_cards = []

    # Extract and resize each card
    for y in [620, 1050]:
        x = start_x
        for i in range(4):
            cropped = img[y:y + height, x:x + width]
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cropped_rgb)

            resized_cards.append(pil_img)

            x += width + x_gap
    labels = []
    for image in resized_cards:
        predicted_label = predict_image(image)
        labels.append(predicted_label)
    return labels
