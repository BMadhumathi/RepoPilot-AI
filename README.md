# RepoPilot-AI

RepoPilot-AI is an AI-powered software repository assistant designed to understand and answer questions about codebases.

The project is being built incrementally to explore and implement:

* Retrieval-Augmented Generation (RAG)
* AI Agents
* Tool Calling
* Model Context Protocol (MCP)
* Multi-Agent Orchestration
* React-based interfaces

The current implementation focuses on building a reliable **RAG foundation** before introducing agents and MCP.

---

## Current Status

### Phase 1 — RAG Foundation: COMPLETE ✅

The current backend can:

* Clone GitHub repositories
* Scan supported source files
* Parse repository files
* Split files into overlapping chunks
* Generate Gemini embeddings
* Store embeddings in ChromaDB
* Detect unchanged files using SHA-256 hashes
* Re-index changed files
* Retrieve relevant code chunks
* Generate grounded answers using Gemini
* Return source metadata with answers
* Reject questions that are not supported by repository context
* Retry transient Gemini embedding and generation failures
* Handle invalid empty questions with HTTP 400
* Keep generated repository and vector database data out of Git

The system has been tested against the `itsdangerous` repository.

---

# Architecture

Current Phase 1 architecture:

```text
                    GitHub Repository
                           │
                           ▼
                    Repository Service
                           │
                           ▼
                      File Scanner
                           │
                           ▼
                       Code Parser
                           │
                           ▼
                      Chunk Service
                           │
                           ▼
                  Gemini Embedding API
                           │
                           ▼
                       ChromaDB
                           │
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             │
                User Question     │
                    │             │
                    ▼             │
              Query Embedding     │
                    │             │
                    ▼             │
               Similarity Search ◄┘
                    │
                    ▼
                Top-K Chunks
                    │
                    ▼
             Grounded Prompt
                    │
                    ▼
              Gemini 2.5 Flash
                    │
                    ▼
             Answer + Sources
```

---

# RAG Pipeline

RepoPilot-AI currently follows this pipeline:

```text
GitHub Repository
        ↓
File Scanner
        ↓
Code Parser
        ↓
Chunk Service
        ↓
Gemini Embeddings
        ↓
ChromaDB
        ↓
User Question
        ↓
Question Embedding
        ↓
Similarity Search
        ↓
Top-K Retrieved Chunks
        ↓
Prompt + Repository Context
        ↓
Gemini 2.5 Flash
        ↓
Grounded Answer + Sources
```

The important principle is that Gemini does not receive the entire repository.

Instead:

1. The repository is indexed.
2. Code is split into chunks.
3. Each chunk receives an embedding.
4. Embeddings are stored in ChromaDB.
5. A user question is converted into an embedding.
6. ChromaDB retrieves the most relevant chunks.
7. Those chunks are placed into the prompt.
8. Gemini generates an answer using the retrieved repository context.

---

# Project Structure

```text
RepoPilot-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── repository.py
│   │   │   └── chat.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logger.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat_request.py
│   │   │   ├── code_chunk.py
│   │   │   ├── code_file.py
│   │   │   └── repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── file_scanner.py
│   │   │   ├── code_parser.py
│   │   │   ├── chunk_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── repository_service.py
│   │   │   └── python_metadata_extractor.py
│   │   │
│   │   ├── vectorstore/
│   │   │   └── chroma_service.py
│   │   │
│   │   ├── rag/
│   │   ├── agents/
│   │   └── utils/
│   │
│   └── requirements.txt
│
├── docs/
│   └── architectre.md
│
├── README.md
├── .env.example
└── .gitignore
```

---

# Main Components

## 1. File Scanner

`file_scanner.py`

Scans the cloned repository and identifies supported files.

Supported examples include:

```text
.py
.java
.js
.ts
.tsx
.jsx
.html
.css
.json
.md
.xml
.yaml
.yml
.sql
.properties
.txt
```

Directories such as:

```text
.git
node_modules
__pycache__
venv
.idea
.vscode
dist
build
target
```

are ignored.

---

## 2. Code Parser

`code_parser.py`

Reads repository files and converts them into structured `CodeFile` objects.

The parsed representation contains information such as:

* file name
* file path
* programming language
* file content

This creates a consistent input for the chunking stage.

---

## 3. Chunk Service

`chunk_service.py`

Large files are split into smaller pieces before embedding.

Current configuration:

```text
Chunk size: 100 lines
Overlap:    20 lines
```

For example:

```text
Lines 1–100
     ↓
Lines 81–180
     ↓
Lines 161–260
```

The overlap helps preserve context between neighboring chunks.

Each chunk receives a deterministic SHA-256 ID based on its:

* file path
* start line
* end line
* content

This makes chunk identification stable across indexing operations.

---

## 4. Embedding Service

`embedding_service.py`

The project uses:

```text
gemini-embedding-001
```

Each code chunk is converted into a numerical vector.

Conceptually:

```text
Code
 ↓
Embedding Model
 ↓
[0.012, -0.084, 0.221, ...]
```

These vectors allow semantically similar code and questions to be located near each other in vector space.

The embedding service also retries transient rate-limit errors using exponential backoff.

---

## 5. ChromaDB

`chroma_service.py`

ChromaDB is used as the vector database.

Each stored chunk contains:

```text
chunk ID
embedding
document
file metadata
```

Metadata includes:

```text
file_name
file_path
language
start_line
end_line
file_hash
```

This metadata allows retrieved chunks to be connected back to their original repository locations.

---

## 6. Change Detection

`repository_service.py`

Before indexing a file, RepoPilot-AI calculates a SHA-256 hash of the file contents.

Conceptually:

```text
Current file
     ↓
SHA-256
     ↓
Current hash
     ↓
Compare with stored hash
```

If the hashes match:

```text
File unchanged
      ↓
Skip re-indexing
```

If the hashes differ:

```text
File changed
      ↓
Re-parse
      ↓
Re-chunk
      ↓
Re-embed
      ↓
Replace stored chunks
```

This avoids unnecessarily generating embeddings for unchanged files.

---

# Chat / RAG Flow

`chat_service.py`

When a user asks a question:

```text
User Question
      ↓
Validate question
      ↓
Generate question embedding
      ↓
Query ChromaDB
      ↓
Retrieve top 5 chunks
      ↓
Build repository context
      ↓
Build grounded prompt
      ↓
Gemini 2.5 Flash
      ↓
Answer + source metadata
```

The generated prompt instructs Gemini to:

* use only repository context
* avoid inventing repository facts
* identify when the repository does not contain enough information
* reference retrieved sources
* mention relevant files and line ranges when useful

For unsupported questions, the expected response is:

```text
I couldn't find that information in the repository.
```

---

# Reliability Improvements

Phase 1 introduced several reliability improvements.

### Embedding retry

Transient Gemini embedding rate limits are retried with exponential backoff.

### Gemini generation retry

Transient server errors such as HTTP 503 responses are retried before failing.

### Empty-question validation

An empty question is rejected with:

```text
HTTP 400
```

instead of becoming an internal server error.

### Empty vector database handling

If ChromaDB contains no vectors, the system returns a repository-not-found response instead of attempting an invalid vector query.

---

# Source References

Retrieved chunks include metadata such as:

```text
File: serializer.py
Path: repositories/itsdangerous/src/itsdangerous/serializer.py
Lines: 161-260
```

The LLM can therefore reference retrieved sources in responses:

```text
[SOURCE 1]
[SOURCE 2]
```

This makes answers easier to verify against the actual repository.

---

# Testing

Phase 1 was tested using the `itsdangerous` repository.

Tests performed:

```text
Backend startup                  ✅
Fresh repository ingestion      ✅
Unchanged file detection        ✅
Changed file detection          ✅
Repository RAG question         ✅
Source references               ✅
Out-of-repository grounding     ✅
Gemini transient error retry    ✅
Empty question handling         ✅
Git cleanup                     ✅
```

Example repository question:

```text
How does Serializer work in this repository?
```

The system returned a repository-grounded explanation with source references.

Example unsupported question:

```text
What is the current weather in Chennai?
```

The system returned:

```text
I couldn't find that information in the repository.
```

rather than inventing a repository answer.

---

# Environment Setup

## Requirements

Recommended environment:

```text
Python 3.11
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

---

# Environment Variables

Create:

```text
backend/.env
```

with the required Gemini API configuration.

Example:

```text
GEMINI_API_KEY=your_api_key
```

Do not commit `.env`.

The project includes `.env.example` for documenting required environment variables.

---

# Running the Backend

From the backend directory:

```powershell
cd C:\Ai-projects\RepoPilot-AI\backend
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Git Hygiene

Generated and sensitive files are excluded using `.gitignore`.

Ignored examples:

```text
.env
venv/
chromadb/
repositories/
chroma_db/
__pycache__/
*.log
.vscode/
.idea/
```

The repository should contain source code and documentation, not generated vector databases or cloned repositories.

---

# Current Limitations

The current Phase 1 implementation is intentionally focused on establishing a reliable RAG foundation.

Known areas for future improvement include:

* removing vectors for deleted repository files
* pulling remote changes when a repository already exists locally
* stronger retrieval relevance filtering
* more sophisticated code-aware chunking
* better API-level handling of exhausted external API failures
* richer repository metadata
* automated tests

These are intentionally not being addressed before moving to the next architectural phase.

---

# Development Roadmap

The project is being developed in the following order:

```text
PHASE 1
Stabilize & understand RAG
        ↓
PHASE 2
Build ONE real Code Agent
        ↓
PHASE 3
Learn + implement MCP
        ↓
PHASE 4
Build Manager Agent
        ↓
PHASE 5
Add MCP tool ecosystem
        ↓
PHASE 6
Connect RAG properly into agents
        ↓
PHASE 7
Build React UI
```

The learning progression is:

```text
RAG
 ↓
Agents
 ↓
Tool Calling
 ↓
MCP
 ↓
Multi-Agent Orchestration
 ↓
React UI
```

The project intentionally follows this progression instead of introducing multiple agents and tools before the underlying concepts are understood.

---

# Long-Term Architecture

The planned architecture is:

```text
React UI
   │
FastAPI Backend
   │
Manager Agent
   │
Code Agent / API Agent / Docs Agent / Test Agent
   │
Tool Layer (MCP)
   │
GitHub | Filesystem | SQLite
   │
RAG Service
   │
ChromaDB + Embeddings
   │
Gemini
```

The current implementation represents the RAG foundation of this architecture.

Agents, MCP, multi-agent orchestration, and the React UI will be introduced incrementally in later phases.

---

# Goal

The goal of RepoPilot-AI is not simply to build a chatbot.

The project is intended to demonstrate an understanding of how modern AI software systems are constructed:

```text
RAG
 ↓
Agents
 ↓
Tools
 ↓
MCP
 ↓
Multi-Agent Orchestration
 ↓
User Interface
```

Each phase is implemented, tested, and understood before moving to the next one.
