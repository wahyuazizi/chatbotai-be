import logging
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
            self.retriever = self.vector_store.as_retriever(k=10)
            logging.info("Successfully connected to Azure AI Search.")
        except Exception as e:
            logging.warning(f"Could not connect to Azure AI Search. Error: {e}")
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
            logging.info("No documents loaded. Ingestion skipped.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)

        logging.info(f"Ingesting {len(split_docs)} document chunks into Azure AI Search...")
        
        # Add documents to the Azure AI Search index
        self.vector_store.add_documents(documents=split_docs)
        
        logging.info("Ingestion complete.")

    def _format_docs(self, docs):
        formatted_docs = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown Source').split('/')[-1] # Extract filename
            page = doc.metadata.get('page_label', doc.metadata.get('page', 'Unknown Page')) # Get page label or page number
            formatted_docs.append(f"Content from {source} (Page {page}):\n{doc.page_content}")
        return "\n\n".join(formatted_docs)

    def get_answer(self, query: str) -> ChatResponse:
        logging.info(f"get_answer method called with query: {query}")
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not available. Please check configuration and ingest data."
            )

        off_topic_template = """
        Anda adalah asisten AI. Tugas Anda adalah menolak permintaan yang tidak pantas atau di luar topik dengan sopan dan mengarahkan kembali percakapan ke topik yang relevan.
        Tolak permintaan untuk mengerjakan PR atau tugas sekolah.
        Jawab secara eksklusif dalam bahasa Indonesia.
        Arahkan kembali pengguna untuk bertanya tentang Universitas Hamzanwadi, khususnya Fakultas Teknik.

        Contoh:
        User: Kerjakan PR saya.
        AI: Mohon maaf, saya tidak dapat membantu mengerjakan tugas. Silakan bertanya tentang Universitas Hamzanwadi.

        User: Apa itu ibu kota perancis?
        AI: Mohon maaf, saya hanya dapat memberikan informasi terkait Universitas Hamzanwadi. Ada yang bisa saya bantu seputar kampus?
        
        Pertanyaan Pengguna:
        {question}
        """

        rag_template = """
        Anda adalah asisten AI untuk Universitas Hamzanwadi.
        Gunakan informasi dari bagian 'Konteks' berikut untuk menjawab pertanyaan. Jika Anda tidak dapat menemukan jawabannya di dalam konteks yang diberikan, nyatakan bahwa informasi tersebut tidak tersedia dalam dokumen yang Anda miliki.
        Jangan gunakan pengetahuan umum Anda untuk menjawab pertanyaan yang seharusnya dijawab dari konteks.
        Selalu jawab dalam bahasa Indonesia.
        Jika sesuai, arahkan percakapan untuk membahas Fakultas Teknik.

        Konteks:
        {context}

        Pertanyaan:
        {question}
        """
        
        # Preliminary check for off-topic questions
        off_topic_prompt = ChatPromptTemplate.from_template(off_topic_template)
        off_topic_chain = off_topic_prompt | self.llm | StrOutputParser()
        
        # Note: This is a simplified check. A more robust implementation might use a separate classifier.
        # is_off_topic = "pr" in query.lower() or "tugas" in query.lower() # Temporarily disabled for debugging

        # if is_off_topic: # Temporarily disabled for debugging
        #     answer = off_topic_chain.invoke({"question": query})
        #     return ChatResponse(answer=answer, sources=[]) # Temporarily disabled for debugging

        prompt = ChatPromptTemplate.from_template(rag_template)

        rag_chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Get relevant documents first to include in the response
        relevant_docs = self.retriever.get_relevant_documents(query)
        
        context_string = self._format_docs(relevant_docs)

        # Invoke the chain to get the answer
        answer = rag_chain.invoke({"context": context_string, "question": query})

        # Fallback for out-of-scope questions that weren't caught by the initial check
        # if not relevant_docs: # Temporarily disabled for debugging
        #     answer = off_topic_chain.invoke({"question": query})
        #     return ChatResponse(answer=answer, sources=[]) # Temporarily disabled for debugging

        # Format sources
        sources = [
            Source(
                source=doc.metadata.get('source', 'Unknown'),
                content=doc.page_content
            ) for doc in relevant_docs
        ]

        debug_info = {
            "relevant_docs": [doc.dict() for doc in relevant_docs], # Convert to dict for serialization
            "context_string": context_string
        }

        return ChatResponse(answer=answer, sources=sources, debug_info=debug_info)
