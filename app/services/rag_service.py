from fastapi import HTTPException, status
from langchain_databricks import DatabricksVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.core.clients import azure_llm, azure_embedder
from app.core.config import settings
from app.schemas.chat import ChatResponse, Source

class RAGService:
    def __init__(self):
        self.llm = azure_llm
        self.embedder = azure_embedder
        self.index_name = settings.DATABRICKS_INDEX_NAME
        
        try:
            self.vector_store = DatabricksVectorSearch(
                embedding=self.embedder,
                index_name=self.index_name,
                host=settings.DATABRICKS_HOST,
                token=settings.DATABRICKS_TOKEN,
            )
            self.retriever = self.vector_store.as_retriever()
        except Exception as e:
            # This can happen if the index doesn't exist yet.
            # The chat endpoint will fail, but the app can still start.
            print(f"Warning: Could not initialize Databricks vector store. Chat will not work until data is ingested. Error: {e}")
            self.vector_store = None
            self.retriever = None

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_answer(self, query: str) -> ChatResponse:
        if not self.retriever:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not available. Please ingest data first."
            )

        template = """
        You are a helpful assistant for a university. 
        Answer the question based ONLY on the following context.
        If you don't know the answer, just say that you don't know. Do not make up an answer.

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