from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding():
    # Initialize embeddings with the specified model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings  # Return the embedding function