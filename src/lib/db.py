import os

import psycopg

from lib import env_vars


def execute_db_query(query, params=None):
    # Connect to your PostgreSQL database using psycopg (psycopg3)
    conn = psycopg.connect(env_vars.env_vars.DATABASE_URL)

    cursor = conn.cursor()

    # Execute the DELETE query with the specified source
    cursor.execute(query, params)

    # Commit the changes to make sure the deletion takes effect
    conn.commit()

    # Clean up by closing the cursor and connection
    cursor.close()
    conn.close()
