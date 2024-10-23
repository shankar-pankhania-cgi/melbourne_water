import os
from fastapi import FastAPI, HTTPException
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['LANGSMITH_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
os.environ['LANGCHAIN_TRACING_V2'] = "true"

# FastAPI app configuration
app = FastAPI()

# Initialize Chroma Vector Store
persist_directory = "./chroma_data"  # Directory for persistent data
embedding_function = OpenAIEmbeddings()

# Load vector store from the local persistence directory
try:
    vector_store = Chroma(
        collection_name="qa_system",  # Ensure this matches your collection name
        embedding_function=embedding_function,
        persist_directory=persist_directory  # Directory for persistent data
    )
    vector_store._collection  # Access collection to force load
    print("Collection loaded successfully.")
except Exception as e:
    print(f"Error loading collection: {e}")
    raise HTTPException(status_code=500, detail="Failed to load vector store")

# Query the Chroma vector store and return the best-matched document content
def query_chroma(question):
    docs = vector_store.similarity_search(question, k=3)  # Retrieve the top 3 most similar documents
    context = "\n".join([doc.page_content for doc in docs])  # Combine their content
    return context

# FastAPI route to handle the question
@app.post("/answer")
def answer_question(question: dict):
    question_text = question.get("question", "")
    if not question_text:
        raise HTTPException(status_code=400, detail="Question not provided")
    
    # Retrieve relevant context from Chroma
    context = query_chroma(question_text)
    
    # RAG chain setup using the retriever and the LLM
    retriever = vector_store.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model="gpt-4o-mini")  # Replace with your preferred model
    
    # Define the RAG chain
    rag_chain = (
        {"context": retriever | (lambda docs: "\n\n".join([doc.page_content for doc in docs])), 
         "question": RunnablePassthrough()}  # Context and question pass-through
        | prompt
        | llm
        | StrOutputParser()  # Parse the output into a string
    )

    # Invoke the RAG chain with the question
    answer = rag_chain.invoke(question_text)

    # Return the answer from the RAG chain
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
