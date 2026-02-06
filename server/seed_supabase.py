import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure we use the Supabase URL
# Note: In Vercel this is set as DATABASE_URL, but for local run we set it explicitly or use .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or "supabase" not in DATABASE_URL and "postgres" not in DATABASE_URL:
    print("Warning: DATABASE_URL does not look like a Supabase/Postgres URL.")
    print(f"Current URL: {DATABASE_URL}")
    response = input("Do you want to continue? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

from app.database.connection import engine, Base, seed_sample_data, SessionLocal

def run_seed():
    print(f"Connecting to database...")
    
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    # Seed data
    print("Seeding sample data...")
    seed_sample_data()
    print("Done!")

if __name__ == "__main__":
    run_seed()
