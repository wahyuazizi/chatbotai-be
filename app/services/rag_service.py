from fastapi import HTTPException, status
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.clients import azure_llm, azure_embedder
from app.core.config import settings
from app.schemas.chat import ChatResponse, Source

class RAGService:
    def __init__(self):
        self.llm = azure_llm
        self.embedder = azure_embedder
        self.index_name = settings.AZURE_AI_SEARCH_INDEX_NAME
        
        try:
            self.vector_store = AzureSearch(
                azure_search_endpoint=settings.AZURE_AI_SEARCH_ENDPOINT,
                azure_search_key=settings.AZURE_AI_SEARCH_KEY,
                index_name=self.index_name,
                embedding_function=self.embedder.embed_query,
            )
            self.retriever = self.vector_store.as_retriever()
            print("Successfully connected to Azure AI Search.")
        except Exception as e:
            print(f"Warning: Could not connect to Azure AI Search. Error: {e}")
            self.vector_store = None
            self.retriever = None

    def ingest_data(self, file_paths: list[str] = None, urls: list[str] = None):
        """Ingests data from PDF files and URLs, creates embeddings, and adds them to Azure AI Search."""
        if not self.vector_store:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure AI Search is not available. Please check the configuration."
            )

        if not file_paths and not urls:
            raise ValueError("Either file_paths or urls must be provided.")

        docs = []
        if file_paths:
            for path in file_paths:
                loader = PyPDFLoader(path)
                docs.extend(loader.load())
        
        if urls:
            loader = WebBaseLoader(urls)
            docs.extend(loader.load())

        if not docs:
            print("No documents loaded. Ingestion skipped.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)

        print(f"Ingesting {len(split_docs)} document chunks into Azure AI Search...")
        
        # Add documents to the Azure AI Search index
        self.vector_store.add_documents(documents=split_docs)
        
        print("Ingestion complete.")

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_answer(self, query: str) -> ChatResponse:
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not available. Please check configuration and ingest data."
            )

        template = """
        You are a helpful assistant for a university. 
        Use the following context to answer the question. If the context is not relevant or if you cannot find the answer within the context, please answer based on your general knowledge.
        Always answer in Indonesian.

        Context:
        {context}

        Question:
        {question}
        """
        
        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Get relevant documents first to include in the response
        relevant_docs = self.retriever.get_relevant_documents(query)
        
        # Invoke the chain to get the answer
        answer = rag_chain.invoke(query)

        # Format sources
        sources = [
            Source(
                source=doc.metadata.get('source', 'Unknown'),
                content=doc.page_content
            ) for doc in relevant_docs
        ]

        return ChatResponse(answer=answer, sources=sources)

rag_service = RAGService()