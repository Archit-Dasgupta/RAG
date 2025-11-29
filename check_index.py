import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "personal-rag-index"

def check_index():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Error: PINECONE_API_KEY not found.")
        return

    pc = Pinecone(api_key=api_key)
    
    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        print(f"Index '{INDEX_NAME}' does not exist.")
        return

    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    print(f"Index Stats: {stats}")

if __name__ == "__main__":
    check_index()
