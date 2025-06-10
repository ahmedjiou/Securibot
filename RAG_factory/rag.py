# Variable for scraping so that it doesnt seem suspicious
import os
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings

from pinecone import Pinecone, ServerlessSpec



# ----------- 1. Load Documents (PDF + Web) -----------
# Load multiple PDFs
pdf_paths = ["D:\PROGIETTO_AI_ICY_4A\chatbot\RAG_factory\cnil_guide_securite_personnelle.pdf"]
pdf_docs = []
for path in pdf_paths:
    loader = PyPDFLoader(path)
    pdf_docs.extend(loader.load())

# Load multiple websites
urls = [
    "https://numerique.uphf.fr/organisation/s%C3%A9curit%C3%A9%20des%20syst%C3%A8mes%20d%27information",
    "https://www.info.gouv.fr/risques/cyber-conseils-aux-usagers"
]
web_loader = WebBaseLoader(urls)
web_docs = web_loader.load()

# Combine all documents
all_docs = pdf_docs + web_docs

# ----------- 2. Split into Chunks -----------
# We could have used also token splitting here but we preferred using Caracter splitting because it is "more intelligent"
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=150
)
chunks = text_splitter.split_documents(all_docs)

# ----------- 3. Generate Embeddings -----------
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectors = embedding_model.embed_documents([doc.page_content for doc in chunks])

# ----------- 4. Push to Pinecone -----------
# Set your API key securely (don't hardcode in production)
api_key = "pcsk_4cgUGb_DnYNfZT3q8RyuMyPQSqgRU9NpiqF2LCZQsNDRV7Swo8W82feWgDpBVhikrpghMQ"
region = "us-east-1"

# Create Pinecone instance
pc = Pinecone(api_key=api_key)

# Use an index
index_name = "cyber-rag-index"

# Optional: create the index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # or whatever your embedding model uses
        metric="cosine",  # or "euclidean"
        spec=ServerlessSpec(cloud="aws", region=region)
    )

index = pc.Index(index_name)



# Upload vectors to Pinecone
for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
    index.upsert([
        {
            "id": f"doc-{i}",
            "values": vector,
            "metadata": {"text": chunk.page_content}
        }
    ])

print("✅ Upload complete. Vectors pushed to Pinecone.")
