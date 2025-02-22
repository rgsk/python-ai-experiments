import os

from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lib import db

from .env_vars import env_vars

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


def get_vector_store(collection_name: str):
    connection = env_vars.DATABASE_URL.replace(
        'postgresql', 'postgresql+psycopg'
    )

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vector_store


def save_website(url: str):

    docs_list = WebBaseLoader(
        url
    ).load()

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )

    # Split the documents into chunks
    doc_splits = text_splitter.split_documents(docs_list)
    # Uses psycopg3!

    connection = env_vars.DATABASE_URL.replace(
        'postgresql', 'postgresql+psycopg'
    )
    collection_name = "rahul portfolio website"

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    vector_store.add_documents(doc_splits)


def delete_website(url: str):
    delete_query = """
    DELETE FROM langchain_pg_embedding
    WHERE cmetadata->>'source' = %s;
    """
    db.execute_db_query(delete_query, (url,))
