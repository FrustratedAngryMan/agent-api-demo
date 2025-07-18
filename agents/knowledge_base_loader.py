from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType

class KnowledgeBaseLoader:
    # --- Configuration ---
    PG_DB_URL = "postgresql+psycopg://ai:ai@pgvector:5432/ai"
    CODE_BASE_PATH = "/Users/prabhu.moorthy/Documents/ai-demo-codebases/DemoProductAPI/src/main/"  # Replace with the path to your codebase
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

    # --- 1. Initialize Ollama Embedder and LLM ---
    ollama_embedder = OllamaEmbedder(id="nomic-embed-text", dimensions=768)

    # --- 2. Setup PgVector as the Knowledge Base ---
    pg_vector_db = PgVector(
        table_name="code_chunks",
        db_url=PG_DB_URL,
        embedder=ollama_embedder,
        search_type=SearchType.vector, # Use vector similarity search
    )

    # --- 3. Create a Knowledge Base from your Codebase ---
    # This is the correct way to use the TextKnowledgeBase definition you provided
    code_knowledge_base = TextKnowledgeBase(
        path=CODE_BASE_PATH, # Provide the base path, TextKnowledgeBase will read files from here
        formats=[".java", ".csv"], # Specify formats to include your code files
        vector_db=pg_vector_db,
        num_documents=20
        # chunking_strategy = RecursiveChunking(chunk_size=1000, overlap=100),
    )

    # Load the knowledge base. This will process the files, chunk them,
    # generate embeddings, and store them in PostgreSQL.
    print("Loading codebase into vector database. This may take a while...")
    code_knowledge_base.load(recreate=True)
    print("Codebase loaded successfully!")
