# ScholarMind AI

ScholarMind AI is a Retrieval-Augmented Generation (RAG) research assistant that allows users to upload PDF documents and ask questions about their content.

The system extracts text from uploaded PDFs, divides it into manageable chunks, generates semantic embeddings, stores them in a persistent vector database, retrieves the most relevant passages for a question, and generates a grounded answer using the Gemini API.

---

## Features

- PDF document upload
- PDF text extraction with PyMuPDF
- Recursive text chunking with overlap
- Semantic embedding generation
- Persistent vector storage with ChromaDB
- Similarity-based document retrieval
- Gemini-powered question answering
- Source document and chunk references
- FastAPI backend
- React and Vite frontend
- Loading, success, and error states
- PDF file validation
- Basic Gemini service error handling

---

## How It Works

ScholarMind AI follows a Retrieval-Augmented Generation pipeline:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
ChromaDB Storage
    ↓
User Question
    ↓
Question Embedding
    ↓
Semantic Similarity Search
    ↓
Relevant Document Chunks
    ↓
Gemini API
    ↓
Grounded Answer + Sources
```

Instead of sending the entire PDF to the language model, ScholarMind retrieves only the document sections that are most relevant to the user's question.

This reduces unnecessary context, improves response relevance, and allows the system to provide source metadata with each answer.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- PyMuPDF
- Sentence Transformers
- LangChain Text Splitters
- ChromaDB
- Google Gemini API
- Pydantic
- Python Dotenv

### Frontend

- React
- Vite
- JavaScript
- CSS
- Fetch API

---

## Project Structure

```text
scholarmind-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── services/
│   │   │   ├── pdf_reader.py
│   │   │   ├── text_chunker.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_store.py
│   │   │   └── llm_services.py
│   │   │
│   │   ├── routes/
│   │   ├── models/
│   │   └── utils/
│   │
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs/
├── .gitignore
└── README.md
```

---

## RAG Pipeline

### 1. PDF Processing

The uploaded PDF is read page by page using PyMuPDF.

```python
text += page.get_text() + "\n"
```

The extracted text is returned as a single string.

### 2. Text Chunking

The text is divided using `RecursiveCharacterTextSplitter`.

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

The overlap helps preserve context between neighboring chunks.

### 3. Embedding Generation

Each chunk is converted into a semantic vector using a Sentence Transformer model.

```text
Document chunk → 384-dimensional embedding
```

The same embedding model is used to represent user questions.

### 4. Vector Storage

Each record stored in ChromaDB contains:

```text
Unique ID
Document text
Embedding vector
Filename metadata
Chunk index metadata
```

### 5. Semantic Retrieval

When the user asks a question:

1. The question is converted into an embedding.
2. ChromaDB compares the question vector with stored chunk vectors.
3. The most relevant document chunks are returned.

### 6. Answer Generation

The retrieved chunks and the user's question are inserted into a controlled prompt.

Gemini is instructed to answer only from the supplied context and to state clearly when the answer cannot be found in the uploaded documents.

---

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "message": "ScholarMind AI backend is running"
}
```

### Upload PDF

```http
POST /upload
```

The endpoint:

- validates the file type,
- extracts PDF text,
- creates chunks,
- generates embeddings,
- stores the chunks in ChromaDB.

Example response:

```json
{
  "filename": "research-paper.pdf",
  "character": 13741,
  "chunk_count": 19,
  "embedding_dimension": 384,
  "stored": true
}
```

### Ask a Question

```http
POST /search
```

Example request:

```json
{
  "question": "What are the main findings of the document?"
}
```

Example response:

```json
{
  "question": "What are the main findings of the document?",
  "answer": "The study concludes that...",
  "sources": [
    {
      "filename": "research-paper.pdf",
      "chunk_index": 2
    }
  ],
  "distances": [
    0.42
  ]
}
```

---

## Local Installation

### Prerequisites

Make sure the following tools are installed:

- Python 3.10 or later
- Node.js
- npm
- Git

---

## Backend Setup

Clone the repository:

```bash
git clone https://github.com/Beyzaece/scholarmind-ai.git
cd scholarmind-ai
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
cd backend
python -m pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Start the backend:

```powershell
python -m uvicorn app.main:app --reload
```

Backend address:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend address:

```text
http://localhost:5173
```

The backend and frontend must run at the same time.

---

## Environment Variables

Create the following file:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

An example file is provided as:

```text
backend/.env.example
```

Never commit the real `.env` file or API key to GitHub.

---

## Design Decisions

### Why FastAPI?

FastAPI provides:

- automatic API documentation,
- request validation with Pydantic,
- support for asynchronous operations,
- strong Python integration,
- a suitable backend architecture for AI services.

### Why Recursive Character Splitting?

A fixed character slice can divide words or paragraphs at unsuitable positions.

`RecursiveCharacterTextSplitter` attempts to preserve more natural text boundaries while keeping chunks within the selected size.

### Why ChromaDB?

ChromaDB allows the project to store:

- embeddings,
- original chunk text,
- unique IDs,
- document metadata.

It also provides built-in vector similarity search and persistent local storage.

### Why RAG Instead of Fine-Tuning?

The purpose of this project is to answer questions using dynamically uploaded documents.

RAG was selected because:

- documents can be added without retraining a model,
- source passages can be retrieved,
- information can be updated easily,
- training cost and infrastructure requirements are reduced.

The embedding model and Gemini model are used for inference; their model weights are not trained or modified by this project.

---

## Current Limitations

- Source references currently use chunk indexes rather than PDF page numbers.
- The current embedding model may provide weaker retrieval results for multilingual queries.
- User authentication is not included.
- Conversation history is not persisted.
- Document-level filtering is not yet available.
- Scanned PDFs without embedded text require OCR support.
- Evaluation metrics for retrieval quality have not yet been implemented.

---

## Planned V2 Improvements

- Multi-document library
- Page-number-based citations
- Document selection and filtering
- Multilingual embedding model
- Conversation history
- Improved source previews
- Retrieval quality evaluation
- Duplicate document detection
- Automated document summaries
- Cross-document comparison
- Academic paper comparison
- Docker support
- Automated tests

---

## Security Notes

- API keys are stored in environment variables.
- `.env` is excluded from version control.
- Only PDF uploads are accepted by the upload endpoint.
- Backend origins are restricted through CORS configuration.
- Production deployments should also include file-size limits, authentication, rate limiting, and stricter document validation.

---

## What I Learned

This project provided practical experience with:

- Retrieval-Augmented Generation
- Semantic search
- Text chunking strategies
- Embedding models
- Vector databases
- Prompt construction
- LLM API integration
- FastAPI service architecture
- React–backend communication
- Error handling
- Environment variable management
- Modular AI application development

---

## Author

**Beyza Ece Deniz**

Software Engineering graduate focused on artificial intelligence, natural language processing, computer vision, and AI-powered software systems.

GitHub: `Beyzaece`

---

## License

This project is developed for educational and portfolio purposes.