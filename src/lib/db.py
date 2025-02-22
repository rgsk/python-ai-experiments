import os

import psycopg


def execute_db_query(query, params=None):
    # Connect to your PostgreSQL database using psycopg (psycopg3)
    conn = psycopg.connect(os.getenv('DATABASE_URL'))

    cursor = conn.cursor()

    # Execute the DELETE query with the specified source
    cursor.execute(query, params)

    # Commit the changes to make sure the deletion takes effect
    conn.commit()

    # Clean up by closing the cursor and connection
    cursor.close()
    conn.close()
