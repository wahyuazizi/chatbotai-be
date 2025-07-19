import asyncio
from app.services.rag_service import rag_service

async def main():
    print("Starting direct ingestion test...")
    try:
        # Running the synchronous function in a thread to avoid blocking asyncio
        rag_service.ingest_data(urls=["https://en.wikipedia.org/wiki/Artificial_intelligence"])
        print("Direct ingestion test finished.")
    except Exception as e:
        print(f"An error occurred during direct ingestion: {e}")

if __name__ == "__main__":
    # rag_service.ingest_data is synchronous, so we don't need a full async setup
    # unless other parts of your app require it.
    # For this test, a simple direct call is enough.
    print("Starting direct ingestion test...")
    try:
        rag_service.ingest_data(urls=["https://en.wikipedia.org/wiki/Artificial_intelligence"])
        print("Direct ingestion test finished successfully.")
    except Exception as e:
        import traceback
        print(f"An error occurred during direct ingestion: {e}")
        traceback.print_exc()
