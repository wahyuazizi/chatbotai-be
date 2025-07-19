# Databricks notebook source

# COMMAND ----------
# MAGIC %pip install beautifulsoup4 pypdf langchain langchain-openai langchain-databricks

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
import os
from typing import List
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_databricks import DatabricksVectorSearch
from langchain_openai import AzureOpenAIEmbeddings

# COMMAND ----------
# --- Konfigurasi ---
# Anda bisa menyimpan nilai-nilai ini di Databricks Secrets untuk keamanan
# Contoh: dbutils.secrets.get(scope="your_scope", key="your_key")

# Mengambil kredensial dari Databricks Secrets
# Pastikan Anda sudah membuat secret scope dan menambahkan secret-secret ini
# Lihat panduan: https://docs.databricks.com/en/security/secrets/index.html
try:
    AZURE_OPENAI_API_KEY = dbutils.secrets.get(scope="chatbot-secrets", key="azureOpenaiApiKey")
    AZURE_OPENAI_ENDPOINT = dbutils.secrets.get(scope="chatbot-secrets", key="azureOpenaiEndpoint")
    DATABRICKS_HOST = dbutils.secrets.get(scope="chatbot-secrets", key="databricksHost")
    DATABRICKS_TOKEN = dbutils.secrets.get(scope="chatbot-secrets", key="databricksToken")
except Exception as e:
    print("Error: Pastikan Anda telah membuat Databricks Secret Scope bernama 'chatbot-secrets' dengan key yang diperlukan.")
    print("Key yang dibutuhkan: 'azureOpenaiApiKey', 'azureOpenaiEndpoint', 'databricksHost', 'databricksToken'")
    raise e

# Konfigurasi lainnya
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "text-embedding-3-small"
DATABRICKS_INDEX_NAME = "chatbot-ai.default.chatbot_index" # Nama lengkap indeks: catalog.schema.index_name

# --- Sumber Data ---
URLS_TO_SCRAPE = [
    "https://ft.hamzanwadi.ac.id/in/",
    "https://ft.hamzanwadi.ac.id/in/sejarah/",
    "https://ft.hamzanwadi.ac.id/in/prodi/s1-informatika/",
]
# Untuk memuat PDF, unggah file ke DBFS (Databricks File System) dan berikan path-nya
# Contoh: PDF_DIRECTORY = "/dbfs/FileStore/chatbot_data/"
PDF_DIRECTORY = "/dbfs/FileStore/chatbot_data/"


# COMMAND ----------
def get_azure_embedder() -> AzureOpenAIEmbeddings:
    """Initializes and returns a Langchain Azure Embeddings Model instance."""
    return AzureOpenAIEmbeddings(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
    )

def load_documents_from_urls(urls: List[str]) -> List[Document]:
    """Loads documents from a list of URLs."""
    print(f"Scraping {len(urls)} URL(s)...")
    loader = WebBaseLoader(
        web_paths=urls,
        requests_kwargs={"verify": False}
    )
    loader.requests_per_second = 1
    docs = loader.load()
    print(f"Successfully scraped {len(docs)} document(s).")
    return docs

def load_documents_from_pdfs(directory_path: str) -> List[Document]:
    """Loads all PDF documents from a specified DBFS directory."""
    print(f"Loading PDFs from '{directory_path}'...")
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}. Make sure to upload PDFs to this DBFS path.")
        return []
        
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith(".pdf")]
    all_docs = []
    for pdf_file in pdf_files:
        file_path = os.path.join(directory_path, pdf_file)
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
            print(f" - Loaded {len(docs)} pages from {pdf_file}")
        except Exception as e:
            print(f"   - Error loading {pdf_file}: {e}")
    print(f"Successfully loaded documents from {len(pdf_files)} PDF file(s).")
    return all_docs

def split_documents(docs: List[Document]) -> List[Document]:
    """Splits documents into smaller chunks."""
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"Created {len(split_docs)} text chunks.")
    return split_docs

def create_and_upload_vectors(split_docs: List[Document], embedder: AzureOpenAIEmbeddings):
    """Creates and uploads vector embeddings to Databricks."""
    print(f"Preparing to upload {len(split_docs)} vectors to Databricks index: '{DATABRICKS_INDEX_NAME}'")

    dbsvs = DatabricksVectorSearch(
        embedding=embedder,
        index_name=DATABRICKS_INDEX_NAME,
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN,
    )

    dbsvs.add_documents(documents=split_docs)
    print("Vector upload complete!")

# COMMAND ----------
# --- Main Execution Logic ---
print("--- Starting Data Ingestion Pipeline ---")

# Initialize embedder
azure_embedder = get_azure_embedder()

# Load data
# Pastikan direktori untuk PDF sudah dibuat di DBFS jika diperlukan
os.makedirs(PDF_DIRECTORY, exist_ok=True)
web_docs = load_documents_from_urls(URLS_TO_SCRAPE)
pdf_docs = load_documents_from_pdfs(PDF_DIRECTORY)
all_docs = web_docs + pdf_docs

if not all_docs:
    print("No documents found to process. Exiting.")
else:
    # Process and upload
    split_docs = split_documents(all_docs)
    create_and_upload_vectors(split_docs, azure_embedder)
    print("--- Data Ingestion Pipeline Finished ---")
