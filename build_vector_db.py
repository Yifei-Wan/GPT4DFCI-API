import os
import argparse
from src.embedder import CSVEmbedder, TXTEmbedder
from src.utils import get_or_create_collection, store_embeddings

def process_input_folder(input_folder):
    # Get or create the collection
    collection = get_or_create_collection()

    print("========================================================")
    for filename in os.listdir(input_folder):
        print(f"Embedding file: {filename}") 
        input_path = os.path.join(input_folder, filename)
        if filename.endswith(".csv"):
            # embedder = CSVEmbedder(input_path)
            pass
        elif filename.endswith(".txt"):
            embedder = TXTEmbedder(input_path)
        else:
            print(f"Skipping unsupported file type: {filename}")
            continue

        # Process the input file (text or CSV), generate summary and metadata
        if filename.endswith(".txt"): ## TODO: remove test
            lines, summary = embedder.process()

        # Store embeddings and summary in Chroma DB
        if filename.endswith(".txt"): ## TODO: remove test
            store_embeddings(lines, summary, collection)

    print("--------------------------------------------------------")
    print("Embeddings and summary stored successfully in Chroma DB!")
    print("========================================================")

def main():
    parser = argparse.ArgumentParser(description="Embed CSV and TXT files into vector space and store in Chroma DB.")
    parser.add_argument("-i", "--input_folder", metavar='\b', type=str, help="Path to the input folder containing CSV and TXT files.")
    
    args = parser.parse_args()
    process_input_folder(args.input_folder)

if __name__ == "__main__":
    main()