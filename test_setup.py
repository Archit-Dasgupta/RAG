import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

def test_setup():
    print("Loading environment variables...")
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_key:
        print("ERROR: OPENAI_API_KEY not found in .env")
    else:
        print(f"OPENAI_API_KEY found: {openai_key[:5]}...{openai_key[-4:]}")
        
    if not pinecone_key:
        print("ERROR: PINECONE_API_KEY not found in .env")
    else:
        print(f"PINECONE_API_KEY found: {pinecone_key[:5]}...{pinecone_key[-4:]}")
        
    if not openai_key or not pinecone_key:
        return

    print("\nTesting OpenAI connection...")
    try:
        client = OpenAI(api_key=openai_key)
        # Simple test call
        client.models.list()
        print("SUCCESS: OpenAI connection established.")
    except Exception as e:
        print(f"ERROR: OpenAI connection failed: {e}")

    print("\nTesting Pinecone connection...")
    try:
        pc = Pinecone(api_key=pinecone_key)
        # Simple test call
        pc.list_indexes()
        print("SUCCESS: Pinecone connection established.")
    except Exception as e:
        print(f"ERROR: Pinecone connection failed: {e}")

if __name__ == "__main__":
    test_setup()
