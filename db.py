import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
 
load_dotenv()
 
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://taskuser:taskpass@localhost:5432/taskdb",
)
 
 
def get_connection():
    """
    Open a fresh connection for each operation. RealDictCursor makes rows
    come back as plain dicts (e.g. {"id": 1, "title": "...", "done": False})
    instead of tuples, so the rest of the app doesn't need to know about
    column ordering.
    """
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
 