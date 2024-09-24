import os
import argparse
from src.embedder import CSVEmbedder, TXTEmbedder
from src.utils import get_or_create_collection, store_embeddings

def process_input_folder(input_folder, recursive):
    # Get or create the collection
    collection = get_or_create_collection()

    print("========================================================")
    if recursive:
        for root, _, files in os.walk(input_folder):
            for filename in files:
                process_file(root, filename, collection)
    else:
        for filename in os.listdir(input_folder):
            process_file(input_folder, filename, collection)

    print("--------------------------------------------------------")
    print("Embeddings and summary stored successfully in Chroma DB!")
    print("========================================================")

def process_file(folder, filename, collection):
    print(f"Embedding file: {filename}")
    input_path = os.path.join(folder, filename)
    if filename.endswith(".csv"):
        embedder = CSVEmbedder(input_path)
    elif filename.endswith(".txt"):
        embedder = TXTEmbedder(input_path)
    else:
        print(f"Skipping unsupported file type: {filename}")
        return

    # Process the input file (text or CSV), generate summary and metadata
    lines, summary = embedder.process()

    # Store embeddings and summary in Chroma DB
    store_embeddings(lines, summary, collection)

def main():
    parser = argparse.ArgumentParser(description="Embed CSV and TXT files into vector space and store in Chroma DB.")
    parser.add_argument("-i", "--input_folder", metavar='\b', type=str, required=True, help="Path to the input folder containing CSV and TXT files.")
    parser.add_argument("-r", "--recursive", action='store_true', help="Recursively list input folder.")
    
    args = parser.parse_args()
    process_input_folder(args.input_folder, args.recursive)

if __name__ == "__main__":
    main()