# RAG SchoolBook - Quickstart Guide

## 📚 Project Overview

**RAG SchoolBook** is a Retrieval-Augmented Generation (RAG) system designed for the **Tamil Grade 8 textbook**. It combines:

- **OCR (Optical Character Recognition)** - Extracts text from scanned PDF pages using DeepSeek
- **Vector Search** - Uses PostgreSQL with pgvector extension for semantic similarity search
- **Knowledge Graph** - Neo4j stores relationships between topics and pages for contextual navigation
- **Generative AI** - OpenAI powers answer generation with multi-language support (Tamil/English)
- **Interactive UI** - Streamlit-based web interface for chat, search, and knowledge graph visualization

**Use case**: Ask questions about Tamil Grade 8 curriculum and get answers with citations, topic connections, and knowledge graph visualization.

---

## 🏗️ Architecture Overview

```
User Query
    ↓
Streamlit UI (Chat/Search/KG)
    ↓
├─→ RAG Pipeline
│   ├─→ Retriever (Vector Search + pgvector)
│   └─→ Answer Generator (OpenAI LLM)
│
├─→ Knowledge Graph
│   └─→ Neo4j (Topic-Page relationships)
│
└─→ PDF Processing Pipeline
    ├─→ PDF Extraction (pdfplumber)
    ├─→ OCR (DeepSeek)
    ├─→ Text Chunking
    ├─→ Embeddings (CLIP)
    └─→ Storage (PostgreSQL + pgvector)
```

---

## 📦 Directory Structure

```
rag_tamil_book/
├── requirements.txt           # Python dependencies
├── src/
│   ├── app/
│   │   └── streamlit_app.py  # Main Streamlit application
│   ├── config/
│   │   └── settings.py       # Configuration (empty - add your config here)
│   ├── data/
│   │   └── [place PDF files here]
│   ├── db/
│   │   ├── pgvector_store.py # PostgreSQL + pgvector connection
│   │   └── schema.sql        # Database schema
│   ├── embeddings/
│   │   ├── embedder.py       # OpenAI embedding helper
│   │   └── unified_embedder.py # CLIP multimodal embedding
│   ├── ingest/
│   │   ├── pdf_ingest.py     # PDF extraction & normalization
│   │   ├── chunker.py        # Text chunking strategy
│   │   ├── embedder.py       # Batch embedding
│   │   └── ocr_deepseek.py   # DeepSeek OCR integration
│   ├── kg/
│   │   └── neo4j_client.py   # Neo4j graph operations
│   ├── rag/
│   │   ├── pipeline.py       # Main RAG orchestration
│   │   ├── retriever.py      # Vector retrieval logic
│   │   └── answer_generator.py # LLM answer generation
│   └── ingest_to_pgvector.py # Data ingestion script
└── pythonenv/                # Python virtual environment
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.9+**
- **PostgreSQL 15+** with pgvector extension
- **Neo4j** database (community or enterprise)
- **OpenAI API Key** (for GPT-based answer generation)
- **PDF file** of Tamil Grade 8 textbook

### 2. Installation

#### Step 1: Set up Python environment
```powershell
cd C:\Users\pavit\OneDrive\Desktop\repo\RAG_SchoolBook
python -m venv pythonenv
# Activate virtual environment
pythonenv\Scripts\Activate.ps1
```

#### Step 2: Install dependencies
```powershell
cd rag_tamil_book
pip install -r requirements.txt
```

**What gets installed:**
- `streamlit` - Web UI framework
- `pdfplumber` - PDF text extraction
- `psycopg2-binary` - PostgreSQL driver
- `pgvector` - Vector database support
- `neo4j` - Graph database driver
- `openai` - LLM API client
- `sentence-transformers` - CLIP embeddings
- `pyvis` - Graph visualization
- Plus 30+ supporting libraries

### 3. Environment Configuration

Create a `.env` file in the `rag_tamil_book/` directory:

```env
# OpenAI API
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# PostgreSQL Configuration
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=tamil_rag
PG_USER=postgres
PG_PASSWORD=your_postgres_password

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### 4. Database Setup

#### PostgreSQL with pgvector

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE tamil_rag;

-- Connect to the database
\c tamil_rag

-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Schema will be auto-created by the ingestion script
```

#### Neo4j

Neo4j will auto-create nodes/relationships when you run the ingestion script. No manual schema setup needed.

### 5. Prepare Your PDF

1. Download or locate the Tamil Grade 8 textbook PDF
2. Place it at: `rag_tamil_book/data/tamil_grade8_book.pdf`
3. Ensure it's readable and preferably scanned/OCR-ready

### 6. Ingest Data

```powershell
cd rag_tamil_book
python src/ingest_to_pgvector.py
```

**What happens:**
1. Reads PDF using `pdfplumber`
2. Performs OCR on images using DeepSeek API
3. Chunks text into semantic units
4. Generates embeddings using CLIP model
5. Stores embeddings in PostgreSQL with pgvector
6. Creates Topic-Page relationships in Neo4j
7. Indexes vectors for fast retrieval

**Duration:** 5-30 minutes depending on PDF size (API calls are made per page)

### 7. Launch the App

```powershell
cd rag_tamil_book
streamlit run src/app/streamlit_app.py
```

Opens at: `http://localhost:8501`

---

## 💬 Using the Application

### Tab 1: Chat
- Ask questions in **Tamil or English**
- Get AI-generated answers with **source citations**
- Chat history is maintained in session
- Example: "பொருளாதாரம் என்றால் என்ன?" (What is economics?)

### Tab 2: Quick Search
- Direct vector similarity search
- Returns top-k relevant chunks from the textbook
- Good for checking if specific topics are covered

### Tab 3: Knowledge Graph
- Visual graph of Topic-Page relationships
- Search by topic name
- Interactive visualization with PyVis
- Shows how concepts connect across the textbook

---

## 🔧 Key Components Explained

### PDF Ingestion (`src/ingest/pdf_ingest.py`)
- Handles both **digital PDFs** (with selectable text) and **scanned PDFs**
- Falls back to full-page OCR for scanned content
- Normalizes text using Unicode NFKC normalization

### Text Chunking (`src/ingest/chunker.py`)
- Splits documents into semantic chunks
- Preserves context by overlapping chunks
- Maintains metadata (page number, source)

### Embeddings (`src/embeddings/unified_embedder.py`)
- Uses **CLIP-ViT-B-32** for multimodal embeddings
- Handles both text and image embedding
- Returns 512-dimensional vectors

### Vector Storage (`src/db/pgvector_store.py`)
- PostgreSQL with IVFFlat index for fast retrieval
- Stores embeddings, text, page numbers, and metadata
- Supports approximate nearest neighbor search

### Answer Generation (`src/rag/answer_generator.py`)
- Uses OpenAI GPT models
- Incorporates retrieved context
- Multi-language support (Tamil/English)
- Adds source citations

### Knowledge Graph (`src/kg/neo4j_client.py`)
- Creates nodes: `Topic`, `Page`
- Relationships: `EXPLAINED_ON`, and others
- Enables topic-based navigation

---

## 🔍 Troubleshooting

### Issue: "pgvector extension not found"
```sql
-- Run this in PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: "Neo4j connection failed"
- Verify Neo4j is running: `http://localhost:7474`
- Check credentials in `.env`
- Restart Neo4j if needed

### Issue: "OpenAI API error"
- Verify `OPENAI_API_KEY` is valid
- Check API quota and billing
- Ensure model name (e.g., `gpt-4o-mini`) is available

### Issue: "OCR taking too long"
- The DeepSeek API call can be slow for large PDFs
- Consider splitting PDF into sections
- Increase timeout in `ocr_deepseek.py`

### Issue: "Streamlit page not loading"
```powershell
# Clear Streamlit cache
streamlit cache clear
streamlit run src/app/streamlit_app.py
```

---

## 📊 Performance Tuning

### Vector Search Speed
- Adjust `lists` parameter in `schema.sql` (higher = more accurate, slower)
- Default: `lists = 100` for medium datasets

### Embedding Generation
- Batch size can be adjusted in `src/ingest/embedder.py`
- Default: 32 for balance between speed and memory

### OCR Accuracy
- Use higher resolution in `pdf_ingest.py`: currently `resolution=300`
- DeepSeek API automatically detects language (Tamil/English)

---

## 🔐 Security Notes

- **Never commit `.env` file** to version control
- Store API keys securely (use secrets management for production)
- Database credentials should use strong passwords
- For production, use environment variables or secret managers

---

## 📚 Dependencies Summary

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `pdfplumber` | PDF extraction |
| `pillow` | Image processing |
| `psycopg2-binary` | PostgreSQL driver |
| `pgvector` | Vector embedding support |
| `neo4j` | Graph database |
| `openai` | LLM API |
| `sentence-transformers` | CLIP embeddings |
| `pyvis` | Network visualization |
| `python-dotenv` | Environment config |
| `requests` | HTTP client |

---

## 🚦 Next Steps

1. ✅ Install dependencies
2. ✅ Set up `.env` with credentials
3. ✅ Create PostgreSQL database
4. ✅ Prepare PDF file
5. ✅ Run ingestion script
6. ✅ Launch Streamlit app
7. ✅ Ask questions!

---

## 📝 Example Questions

- **Tamil**: "புலவர் என்பவர் யார்?" (Who is a poet?)
- **English**: "What are the main themes in the textbook?"
- **Code-mixed**: "Explain the concept of 'வாணிபம்' (commerce) in simple terms"

---

## 🤝 Support & Debugging

For issues with:
- **PDF extraction**: Check `ingest_to_pgvector.py` logs
- **Vector database**: Query PostgreSQL directly with `psql`
- **Knowledge graph**: Check Neo4j Browser at `http://localhost:7474`
- **LLM responses**: Review OpenAI API logs

---

## 📄 License & Attribution

This project uses:
- OpenAI's GPT models
- DeepSeek's OCR capabilities
- Meta's CLIP model
- Neo4j graph database
- PostgreSQL & pgvector
- Streamlit framework

Ensure compliance with respective licenses.

---

**Last Updated**: November 22, 2025  
**Status**: Ready for Development
