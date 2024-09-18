import argparse
from src.azure_client import client
from src.chroma_client import chroma_client
from src.utils import generate_answer, get_relevant_docs

def main():
    parser = argparse.ArgumentParser(description="Query the vector database and generate answers using GPT-4o.")
    parser.add_argument("-q", "--question", metavar="\b", type=str, required=True, help="The question to ask.")
    
    args = parser.parse_args()
    question = args.question

    # Query the vector database
    relevant_docs = get_relevant_docs(question, chroma_client)

    # Generate the answer
    answer = generate_answer(question, relevant_docs, client)
    print("Answer:", answer)

if __name__ == "__main__":
    main()