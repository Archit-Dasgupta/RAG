import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "personal-rag-index"

def delete_index():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        print("Error: PINECONE_API_KEY not found.")
        return

    try:
        pc = Pinecone(api_key=pinecone_api_key)
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if INDEX_NAME in existing_indexes:
            print(f"Deleting index '{INDEX_NAME}'...")
            pc.delete_index(INDEX_NAME)
            print(f"Index '{INDEX_NAME}' deleted successfully.")
        else:
            print(f"Index '{INDEX_NAME}' does not exist.")
            
    except Exception as e:
        print(f"Error deleting index: {e}")

if __name__ == "__main__":
    delete_index()
