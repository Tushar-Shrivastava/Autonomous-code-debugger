import os

# Anthropic API Key for Langchain
ANTHROPIC_API_KEY = 'Your-API-Key'

# Paths
VECTOR_DB_PATH = 'data/vector_db'
DOCS_PATH = 'data/docs'                 # Local PDF's and text are stored here

# Embeddings (Hugging Face)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 64
USE_GPU = None

# RAG SETTING
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 6

# Execution sandbox
USE_DOCKER_SANDBOX = bool(int(os.getenv("USE_DOCKER_SANDBOX", "0")))
SANDBOX_DOCKER_IMAGE = os.getenv("SANDBOX_DOCKER_IMAGE", "python:3.11-slim")

# Agent settings
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))
EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "20"))

# Temp dir for runner files
TEMP_DIR = "tmp"