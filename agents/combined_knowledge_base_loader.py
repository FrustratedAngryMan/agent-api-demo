from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType


class CombinedKnowledgeBaseLoader:
    # --- Configuration ---
    PG_DB_URL = "postgresql+psycopg://ai:ai@pgvector:5432/ai"
    CODE_BASE_PATH = "/Users/prabhu.moorthy/Downloads/DemoProductAPI/"  # Replace with the path to your codebase
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

    ollama_embedder = OllamaEmbedder(id=OLLAMA_EMBEDDING_MODEL, dimensions=768)

    pg_vector_db1 = PgVector(
        table_name="code_chunks_combined_kb",
        db_url=PG_DB_URL,
        embedder=ollama_embedder,
        search_type=SearchType.vector, # Use vector similarity search
    )

    pg_vector_db2 = PgVector(
        table_name="test_chunks_combined_kb",
        db_url=PG_DB_URL,
        embedder=ollama_embedder,
        search_type=SearchType.vector,  # Use vector similarity search
    )

    pg_vector_db3 = PgVector(
        table_name="combined_chunks_combined_kb",
        db_url=PG_DB_URL,
        embedder=ollama_embedder,
        search_type=SearchType.vector,  # Use vector similarity search
    )

    java_code_kb = TextKnowledgeBase(
        path="/Users/prabhu.moorthy/Documents/ai-demo-codebases/DemoProductAPI/src/main/",
        vector_db=pg_vector_db1,  # Use the same vector DB for all
        #chunking_strategy=RecursiveChunking(chunk_size=1000, overlap=100),
        # You might want different chunking for code vs docs
        formats=[".java", ".csv", ".properties"], # Explicitly specify formats if needed
        num_documents = 17,
    )

    test_code_kb = TextKnowledgeBase(
        path="/Users/prabhu.moorthy/Documents/ai-demo-codebases/DemoProductAPI/src/test/",
        vector_db=pg_vector_db2,  # Use the same vector DB for all
        #chunking_strategy=RecursiveChunking(chunk_size=1000, overlap=100),
        # You might want different chunking for code vs docs
        formats=[".java"],  # Explicitly specify formats if needed
        num_documents = 2,
    )

    #print("Loading Java code knowledge base...")
    #java_code_kb.load(recreate=True)  # recreate=True for initial load or full refresh
    #print("Loading Test code knowledge base...")
    #test_code_kb.load(recreate=True)

    # Pass a list of the individual knowledge base instances
    combined_knowledge_base = CombinedKnowledgeBase(
        sources=[java_code_kb, test_code_kb],
        vector_db=pg_vector_db3,
        num_documents=20,
    )

    print("Loading combined knowledge base...")
    combined_knowledge_base.load(recreate=True)
    print("Loading combined knowledge base... Completed")
