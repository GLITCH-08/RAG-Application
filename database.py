import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from embedding_function import get_embedding
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma

# Define paths for the Chroma database and the data directory
CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    # Clear the database if the reset flag is set
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Load documents, split them into chunks, and add them to Chroma
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def load_documents():
    # Load PDF documents from the specified directory
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    # Split documents into smaller chunks using a character-based splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    # Initialize the Chroma vector store with the embedding function
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding()
    )

    # Calculate unique IDs for each chunk
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get the existing documents from the database
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Add only new chunks that don't exist in the database
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    # Add new documents to the database and persist the changes
    if len(new_chunks):
        print(f"----->>> Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("----->>> No new documents to add")

def calculate_chunk_ids(chunks):
    # Create unique IDs for each chunk based on the source, page, and chunk index
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # Increment the chunk index if it's the same page
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Assign a unique ID to each chunk
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database():
    # Remove the Chroma directory to clear the database
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    main()
