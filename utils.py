import re

def get_chunks(text, chunk_size=500, overlap=100):
    """
    Splits text into chunks of approximately `chunk_size` characters,
    respecting sentence and paragraph boundaries, with `overlap`.
    """
    if not text:
        return []

    # Split text into sentences (simple regex for punctuation)
    # This keeps the punctuation with the sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence exceeds chunk_size (and current_chunk is not empty)
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap
            # We take the last 'overlap' characters from the previous chunk
            # but try to keep it clean (e.g. last few words)
            # For simplicity, we just start the new chunk with the current sentence
            # and maybe some context if we were fancy, but let's stick to simple sentence grouping first.
            
            # Better overlap strategy:
            # Keep the last few sentences that fit within 'overlap' size
            overlap_text = ""
            if overlap > 0:
                # This is a bit complex to do perfectly with just strings.
                # Let's try a simpler approach: just keep accumulating until limit.
                pass
            
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    # If any chunk is still massive (e.g. no punctuation), force split it
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size * 1.5:
            # Hard split long chunks
            for i in range(0, len(chunk), chunk_size - overlap):
                final_chunks.append(chunk[i:i + chunk_size])
        else:
            final_chunks.append(chunk)
            
    return final_chunks
