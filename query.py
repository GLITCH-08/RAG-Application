import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from embedding_function import get_embedding

# Path to the Chroma database
CHROMA_PATH = "chroma"

# Template for the prompt to be used by the LLM
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
    # Create a command-line interface to accept the query text
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def query_rag(query_text: str):
    # Initialize the embedding function
    embedding_function = get_embedding()
    
    # Load the Chroma vector store with the embedding function
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Perform a similarity search on the database with the query text
    results = db.similarity_search_with_score(query_text, k=5)

    # Combine the search results into a single context string
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Format the prompt using the context and the query
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # Initialize the model and generate a response
    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)

    # Extract source IDs from the search results
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    
    # Format and print the response with the sources
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

if __name__ == "__main__":
    main()
