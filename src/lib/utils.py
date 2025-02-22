
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector


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
