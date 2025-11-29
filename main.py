import os
import io
from pypdf import PdfReader
from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize clients (lazy loading to allow app to start without keys initially)
def get_clients():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_api_key or not pinecone_api_key:
        raise HTTPException(status_code=500, detail="API Keys not found. Please check your .env file.")
    
    try:
        openai_client = OpenAI(api_key=openai_api_key)
        pc = Pinecone(api_key=pinecone_api_key)
        return openai_client, pc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize clients: {str(e)}")

# Constants
INDEX_NAME = "personal-rag-index"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

# Ensure index exists
def ensure_index(pc):
    existing_indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        try:
            pc.create_index(
                name=INDEX_NAME,
                dimension=1536, # Dimension for text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        except Exception as e:
            # Fallback for free tier or different regions if needed, but usually us-east-1 is safe default
            print(f"Index creation warning: {e}")

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_files(files: List[UploadFile]):
    openai_client, pc = get_clients()
    ensure_index(pc)
    index = pc.Index(INDEX_NAME)
    
    uploaded_count = 0
    
    for file in files:
        content = await file.read()
        
        if file.filename.lower().endswith('.pdf'):
            pdf = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        else:
            text = content.decode("utf-8")
        
        # Simple chunking (can be improved)
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate embedding
            response = openai_client.embeddings.create(
                input=chunk,
                model=EMBEDDING_MODEL
            )
            embedding = response.data[0].embedding
            
            # Create vector ID
            vector_id = f"{file.filename}-{i}"
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {"text": chunk, "filename": file.filename}
            })
            
        # Upsert to Pinecone (batching is better but simple loop for now)
        # Batching in groups of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            index.upsert(vectors=batch)
            
        uploaded_count += 1
        
    return {"message": f"Successfully processed {uploaded_count} files."}

@app.post("/chat")
async def chat(request: ChatRequest):
    openai_client, pc = get_clients()
    ensure_index(pc)
    index = pc.Index(INDEX_NAME)
    
    # Embed query
    query_embedding = openai_client.embeddings.create(
        input=request.message,
        model=EMBEDDING_MODEL
    ).data[0].embedding
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )
    
    # Construct context and unique sources
    context = ""
    sources = set()
    for match in results.matches:
        if match.metadata and "text" in match.metadata:
            context += f"\n---\nSource: {match.metadata['filename']}\n{match.metadata['text']}\n"
            sources.add(match.metadata['filename'])
            
    # Generate response
    system_prompt = f"""You are Archit, a professional and enthusiastic AI assistant. You are a representation of Archit himself, so refer to yourself as "I".
    
    CORE INSTRUCTIONS:
    1. Always be professional and enthusiastic.
    2. Refer to Archit as "I" (e.g., "I worked on this project...").
    3. If asked "who made you", reply EXACTLY: "I was made by Archit Dasgupta designed to handle queries and answer questions on behalf of him during his absence".
    4. If asked "what can you do", reply EXACTLY: "I can answer questions about Archit on behalf of him during his absence".
    5. Keep your answers concise (around 100 words), but feel free to extend if the explanation demands it.
    6. If the answer is not in the context, say you don't know based on the available information.

    PRIVACY & GUARDRAILS:
    - You ARE AUTHORIZED to provide personal information (like address, phone number, email) ONLY IF the user SPECIFICALLY asks for it.
    - Do NOT volunteer personal private information in general summaries or unprompted.
    - You strictly DO NOT support or discuss: sexual content, harmful messages, medical advice, or criminal activity.

    Context:
    {context}
    """
    
    completion = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
    )
    
    return {
        "response": completion.choices[0].message.content,
        "sources": list(sources)
    }

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
