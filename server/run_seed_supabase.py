
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to allow imports from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_engine, SessionLocal, get_db_session, engine
from app.database.models import Base

def run_seed_data():
    """Run the seed data function to populate the database."""
    print("🌱 Script started...")
    
    # Check if DATABASE_URL is set (it should be for Supabase)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables.")
        print("   Make sure you have set it in your .env file locally.")
        return

    print(f"🔌 Connecting to database: {db_url.split('@')[-1]}") # Hide password
    
    try:
        # Create tables first just in case
        print("🔨 Verifying tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables verified/created.")

        print("🌱 Seeding data...")
        from seed_data import seed_sample_data
        
        # We need to reuse the same session logic as seed_data
        seed_sample_data()
        print("✅ Data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_seed_data()
