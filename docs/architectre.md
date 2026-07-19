                React UI
                    │
              FastAPI Backend
                    │
           ┌─────────────────┐
           │  Manager Agent   │
           └─────────────────┘
          /    |      |      \
         /     |      |       \
 Code Agent API Agent Docs Agent Test Agent
         \     |      |       /
          └────┴──────┴───────┘
                    │
              Tool Layer (MCP)
                    │
     GitHub | Filesystem | SQLite
                    │
              RAG Service
                    │
         ChromaDB + Embeddings
                    │
             Gemini 2.5 Flash






            GitHub URL
      │
      ▼
RepositoryService
      │
      ▼
FileScanner
      │
      ▼
CodeParser
      │
      ▼
Parsed Code Objects
      │
      ▼
Chunk Service
      │
      ▼
Embedding Service
      │
      ▼
ChromaDB
      │
      ▼
Only return:

✓ repository
✓ total files
✓ indexed chunks
✓ status