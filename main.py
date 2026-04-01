from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

app = FastAPI(title="Novanews API")

# Enable CORS for your Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    # Uses the password from your .env file
    password = os.getenv("SupaBase_Password")
    conn = psycopg2.connect(
        host="db.imldatxbnfvktxemwdis.supabase.co",
        database="postgres",
        user="postgres",
        password=password,
        port="5432"
    )
    return conn

@app.get("/")
def health_check():
    return {"status": "online", "framework": "FastAPI"}

@app.get("/db-test")
def test_supabase():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        cur.close()
        conn.close()
        return {"connection": "success", "supabase_version": version}
    except Exception as e:
        return {"connection": "failed", "error": str(e)}