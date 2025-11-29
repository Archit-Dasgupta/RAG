import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

INDEX_NAME = "personal-rag-index"

def get_pinecone_client():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Error: PINECONE_API_KEY not found in .env file.")
        return None
    return Pinecone(api_key=api_key)

def list_indexes(pc):
    print("\nListing indexes...")
    indexes = pc.list_indexes()
    names = [i.name for i in indexes]
    if not names:
        print("No indexes found.")
    else:
        print(f"Found indexes: {', '.join(names)}")
    return names

def delete_index(pc):
    print(f"\nAttempting to delete index '{INDEX_NAME}'...")
    try:
        pc.delete_index(INDEX_NAME)
        print(f"Successfully deleted index '{INDEX_NAME}'.")
    except Exception as e:
        print(f"Error deleting index: {e}")

def create_index(pc):
    print(f"\nCreating index '{INDEX_NAME}'...")
    try:
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Successfully created index '{INDEX_NAME}'.")
    except Exception as e:
        print(f"Error creating index: {e}")

def main():
    pc = get_pinecone_client()
    if not pc:
        return

    while True:
        print("\n--- Pinecone Index Manager ---")
        print("1. List Indexes")
        print("2. Delete Index")
        print("3. Create Index")
        print("4. Recreate Index (Delete then Create)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            list_indexes(pc)
        elif choice == '2':
            delete_index(pc)
        elif choice == '3':
            create_index(pc)
        elif choice == '4':
            delete_index(pc)
            print("Waiting 10 seconds before creating...")
            time.sleep(10)
            create_index(pc)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
