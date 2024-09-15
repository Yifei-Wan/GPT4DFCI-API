import hashlib
from tqdm import tqdm
from src.azure_client import client, embed_text, embedding_model, completion_model
from src.chroma_client import chroma_client

def generate_short_hash(text):
    """
    Generate a short hash from the input text.
    """
    return hashlib.md5(text.encode()).hexdigest()[:8]  # Use the first 8 characters of the MD5 hash

def check_if_id_exists(collection, id_to_check):
    """
    Check if a specific ID already exists in the collection.
    """
    try:
        result = collection.get(ids=[id_to_check])
        return len(result["ids"]) > 0  # If the ID exists, return True
    except Exception as err:
        print(err)
        return False

def get_or_create_collection(collection_name="my_embeddings_collection"):
    try:
        collection = chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' found. Updating existing collection.")
    except ValueError as err:
        print(err) 
        collection = chroma_client.create_collection(name=collection_name)
        print(f"Collection '{collection_name}' not found. Created a new collection.")
    
    return collection

def summarize_text(text, metadata, path):
    head_text = text[:1000]  # Pass the first 1000 characters for summarization
    metadata = " ".join(metadata.split("\n"))
    head_text = f"file name: {path} " + head_text + f" metadata {metadata}"
    print(head_text)
    response = client.chat.completions.create(
        model=completion_model,
        messages=[
            {"role": "system", "content": "You are an AI with super-human data extraction and summarization abilities."},
            {"role": "user", "content": f"Please make the description and statistic based on the head part of table and its df.descibe:\n\n{head_text}"}
        ],
        max_tokens=500 # Limit the length of the summary
    )
    print("---------------------------------------------------------")
    print(" ".join(response.choices[0].message.content.strip().split("\n")))
    print("---------------------------------------------------------")
    return " ".join(response.choices[0].message.content.strip().split("\n"))  

def store_embeddings(lines, summary, collection):
    # Embed the original lines
    for line in tqdm(lines):
        unique_id = generate_short_hash(line)
        if not check_if_id_exists(collection, unique_id):
            embedding_vector = embed_text(line)
            collection.add(
                embeddings=[embedding_vector],
                metadatas=[{"input_text": line}],
                ids=[unique_id]
            )
        else:
            pass
            #print(f"ID {unique_id} for text '{line[:30]}...' already exists. Skipping insertion.")
    
    # Embed the summary if it exists
    if summary:
        unique_id = generate_short_hash(summary)
        if not check_if_id_exists(collection, unique_id):
            summary_embedding = embed_text(summary)
            collection.add(
                embeddings=[summary_embedding],
                metadatas=[{"input_text": "Summary", "summary": summary}],
                ids=[unique_id]
            )
        else:
            print(f"ID {unique_id} for the summary already exists. Skipping insertion.")