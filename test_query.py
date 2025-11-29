import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "personal-rag-index"
EMBEDDING_MODEL = "text-embedding-3-small"

def test_query(query):
    print(f"Querying: '{query}'")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    openai_client = OpenAI(api_key=openai_api_key)
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(INDEX_NAME)
    
    # Embed
    resp = openai_client.embeddings.create(input=query, model=EMBEDDING_MODEL)
    embedding = resp.data[0].embedding
    
    # Query
    results = index.query(vector=embedding, top_k=3, include_metadata=True)
    
    print(f"Found {len(results.matches)} matches.")
    for i, match in enumerate(results.matches):
        print(f"\nMatch {i+1} (Score: {match.score:.4f}):")
        print(f"Source: {match.metadata.get('filename', 'Unknown')}")
        print(f"Text: {match.metadata.get('text', '')[:200]}...") # Print first 200 chars

if __name__ == "__main__":
    test_query("Tell me more about Archit")
    test_query("What is Archit's biggest achievement?")
