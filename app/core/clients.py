
from supabase import create_client, Client as SupabaseClient
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from app.core.config import settings

# --- Supabase Client ---
def get_supabase_client() -> SupabaseClient:
    """Initializes and returns a Supabase client instance."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

supabase_client: SupabaseClient = get_supabase_client()



# --- Azure OpenAI Client (for general purpose use) ---
def get_azure_openai_client() -> AzureOpenAI:
    """Initializes and returns a general Azure OpenAI client."""
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )

azure_openai_client: AzureOpenAI = get_azure_openai_client()


# --- Langchain Specific Clients ---
def get_azure_llm() -> AzureChatOpenAI:
    """Initializes and returns a Langchain Azure Chat Model instance."""
    return AzureChatOpenAI(
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_deployment=settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        temperature=0,
        max_tokens=1024,
    )

def get_azure_embedder() -> AzureOpenAIEmbeddings:
    """Initializes and returns a Langchain Azure Embeddings Model instance."""
    return AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
    )

# Instantiate Langchain clients for use in services
azure_llm = get_azure_llm()
azure_embedder = get_azure_embedder()
