# Vedanta_Assistant
# Vedanta Life Guidance

An AI-powered conversational assistant that connects everyday life questions with the teachings of Advaita Vedanta.

The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant passages from a curated Vedanta knowledge base and generate conversational responses using a locally running Large Language Model (LLM).

## Project Overview

Vedanta Life Guidance aims to make the teachings of Advaita Vedanta more accessible by connecting philosophical concepts with everyday situations such as anger, worry, disappointment, attachment, and decision-making.

Users can ask questions in English or Hindi and receive responses supported by relevant passages from the selected source book:

*The Essential Vedanta: A New Source Book of Advaita Vedanta*, edited by Eliot Deutsch and Rohit Dalvi.

The application also provides source references so users can identify the passages used to generate the responses.

## Key Features

- **Conversational Interface:** Ask questions through a React-based chat interface.
- **Retrieval-Augmented Generation:** Retrieves relevant passages before generating an answer.
- **Multilingual Support:** Supports English and Hindi queries through multilingual embeddings.
- **Semantic Search:** Uses BGE-M3 embeddings and Qdrant for similarity-based retrieval.
- **Local LLM Integration:** Uses Qwen3:4b through Ollama.
- **Source References:** Displays relevant text references and page numbers with responses.
- **Session Management:** Maintains conversation context using session IDs.
- **Domain Awareness:** Handles questions outside the intended Vedanta guidance domain.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js |
| Backend | Python, FastAPI |
| Language Model | Qwen3:4b |
| Local Model Runtime | Ollama |
| LLM Framework | LangChain |
| Embedding Model | BGE-M3 |
| Vector Database | Qdrant |
| Knowledge Base | JSON |
| API Communication | Axios |

## System Architecture

The application follows a RAG-based architecture.

1. The user submits a question through the React frontend.
2. The question is sent to the FastAPI backend along with a session ID.
3. BGE-M3 converts the question into a vector embedding.
4. Qdrant searches the knowledge base for semantically relevant passages.
5. The retrieved passages are provided as context to the language model.
6. Qwen3:4b generates a response through Ollama.
7. The backend returns the answer and source information to the frontend.
8. Conversation history is maintained for follow-up questions within the same session.

## Project Structure

```text
Vedanta_Assistant/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── Components/
│   │   ├── Pages/
│   │   └── Services/
│   └── package.json
│
├── backend/
│   ├── data/
│   │   ├── vedanta_passages.json
│   │   └── prepared_passages.json
│   │
│   ├── rag/
│   │   ├── vectore_store.py
│   │   └── retriever.py
│   │
│   ├── llm/
│   │   └── llm.py
│   │
│   ├── vector_store/
│   │   └── qdrant/
│   │
│   ├── main.py
│   └── requirements.txt
│
├── docs/
│   ├── architecture.png
│   ├── sample_results.md
│   └── project_report.pdf
│
|
├── .gitignore
└── README.md
```

## Prerequisites

Make sure the following software is installed:

- Python 3.13 or a compatible Python version.
- Node.js and npm.
- Ollama.
- Git.

You also need sufficient disk space and system resources to run the local language model and embedding model.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Vedanta_Assistant
```

Replace the placeholder with your GitHub repository URL.

### 2. Create and Activate a Python Virtual Environment

From the project root directory, run:

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use an appropriate execution policy for your environment or activate the environment through Command Prompt.

### 3. Install Backend Dependencies

Navigate to the backend directory:

```powershell
cd backend
```

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

Return to the project root when needed:

```powershell
cd ..
```

### 4. Set Up Ollama and the Language Model

Install Ollama and make sure it is running.

Download the Qwen3:4b model:

```powershell
ollama pull qwen3:4b
```

Verify that the model is available:

```powershell
ollama list
```

The application uses the locally hosted model through Ollama.

### 5. Prepare the Vector Database

The application uses BGE-M3 for embeddings and Qdrant for vector storage.

Make sure the curated and prepared passage JSON files are present in:

```text
backend/data/
```

Run the vector-store preparation script from the backend directory:

```powershell
cd backend
python rag/vectore_store.py
```

This step should be performed when creating or rebuilding the vector database. It may take some time because the embedding model needs to process the passages.

**Note:** The vector database must be generated using the same embedding model and vector dimensions expected by the retriever.

### 6. Start the Backend Server

From the `backend` directory, run:

```powershell
uvicorn main:app --reload
```

The FastAPI backend will be available at:

```text
http://localhost:8000
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

### 7. Install Frontend Dependencies

Open a new terminal and navigate to the frontend directory:

```powershell
cd frontend
```

Install the Node.js dependencies:

```powershell
npm install
```

### 8. Start the Frontend

For a Create React App project, run:

```powershell
npm start
```

For a Vite-based project, run:

```powershell
npm run dev
```

Use the command configured in the `frontend/package.json` file.

Open the local frontend address shown in the terminal.

## API Endpoints

The FastAPI backend provides the following endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Checks backend health status. |
| `/topics` | GET | Retrieves available knowledge-base topics. |
| `/passages` | GET | Retrieves passages, with an optional topic filter. |
| `/ask` | POST | Accepts a question and session ID and returns the generated answer and sources. |
| `/sessions/{session_id}` | DELETE | Deletes a conversation session, if this endpoint is implemented. |

## Example Questions

Users can try questions such as:

1. How can I control my anger?
2. I constantly worry about my future and cannot focus on the present.
3. I work hard but feel disappointed when I do not get the expected results.
4. How can I understand my true identity?
5. What is the difference between what is pleasant and what is beneficial?

The application is intended for questions related to Advaita Vedanta and its application to everyday life.

## Sample Results

Sample questions, generated responses, and retrieved source references are documented in:

```text
docs/sample_results.md
```

The document includes examples of both supported and unsupported questions.

## Configuration

An `.env.example` file is included to document any environment variables required by the project.

Copy it to `.env` if the application requires local environment configuration:

```powershell
Copy-Item .env.example .env
```

Update the values according to your local setup. Do not commit real credentials, private keys, or sensitive configuration values to GitHub.

## Limitations

- The current application uses in-memory conversation storage. Conversation history is lost when the backend restarts.
- Response generation speed depends on the available CPU/GPU resources and local model configuration.
- The quality of generated responses depends on the relevance and coverage of the curated knowledge base.
- The application is focused on Advaita Vedanta and is not intended to answer general-purpose questions.
- Generated practical suggestions are AI interpretations inspired by retrieved teachings and should not be treated as direct quotations from the source text.

## Future Enhancements

Possible improvements include:

- Persistent conversation storage using Redis or a relational database.
- User registration, authentication, and personalized conversation history.
- Expansion of the curated Vedanta knowledge base.
- Improved retrieval and response evaluation.
- GPU-based model inference for faster response generation.
- Deployment to cloud infrastructure to support multiple users.
- Improved frontend experience and mobile accessibility.

## Documentation

Additional project documentation is available in the `docs/` directory:

- `architecture.png` – System architecture diagram.
- `sample_results.md` – Sample questions, generated responses, and source references.
- `project_report.pdf` – Detailed project report.

