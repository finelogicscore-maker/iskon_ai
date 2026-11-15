import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pinecone import Pinecone

# ---------------------------------------------------------
# Load Environment Variables & Validation
# ---------------------------------------------------------
load_dotenv()

if not os.getenv("PINECONE_API_KEY"):
    raise ValueError("PINECONE_API_KEY not found in environment or .env file.")
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment or .env file.")

# ---------------------------------------------------------
# Configuration & Initialization
# ---------------------------------------------------------
print("Connecting to Pinecone...")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

print("Loading Hugging Face embedding model locally...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.2)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

template = """You are a knowledgeable spiritual guide delivering wisdom from sacred scriptures based *only* on the provided context. Answer faithfully with spiritual clarity, conviction, and compassion. Use key philosophical terms naturally where appropriate. If the answer cannot be found in the provided context, state clearly that it is not mentioned in the text, rather than speculating.

Context:
{context}

Question: {question}"""

prompt = ChatPromptTemplate.from_template(template)

# ---------------------------------------------------------
# FastAPI App Setup
# ---------------------------------------------------------
app = FastAPI(
    title="Sacred Library RAG API",
    description="Multi-index RAG system for sacred texts.",
    version="1.0.0"
)

# Mount static directory for images
BASE_DIR = Path(__file__).parent
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ChatRequest(BaseModel):
    query: str = Field(..., description="The question to ask about the text", example="What is the nature of the soul?")

class ChatResponse(BaseModel):
    index_name: str
    query: str
    answer: str

@app.post("/{index_name}", response_model=ChatResponse)
async def chat_with_index(index_name: str, request: ChatRequest):
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing_indexes:
            raise HTTPException(
                status_code=404, 
                detail=f"Pinecone index '{index_name}' not found. Available indexes: {existing_indexes}"
            )

        vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings
        )

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = rag_chain.invoke(user_query)
        return ChatResponse(index_name=index_name, query=user_query, answer=response)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def home_page():
    html_path = BASE_DIR / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html file not found on the server.")
    return FileResponse(html_path)