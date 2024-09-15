import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

embedding_model = "text-embedding-3-large-1-api"
completion_model = "gpt-4o-2024-05-13-api"  # GPT model for generating summaries
api_version = "2023-05-15"

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
entra_scope = os.getenv("AZURE_OPENAI_ENTRA_SCOPE")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    entra_scope
)

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
)

def embed_text(text):
    response = client.embeddings.create(
        model=embedding_model,
        input=text
    )
    return response.data[0].embedding