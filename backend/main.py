from uuid import uuid4
from typing import Dict,List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client.models import Filter, FieldCondition, MatchValue

from llm.llm import VedantaAssistant


# --------------------------------------------------
# Application startup and shutdown
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\nInitializing Vedanta Assistant...")

    try:
        app.state.assistant = VedantaAssistant()
        print("Vedanta Assistant initialized successfully!")

        yield

    finally:
        assistant = getattr(app.state, "assistant", None)

        if assistant and hasattr(assistant, "close"):
            assistant.close()

        print("Vedanta Assistant shut down.")


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Vedanta Life Guidance API",
    description="AI-powered Advaita Vedanta Life Guidance using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# --------------------------------------------------
# In-memory conversation history
# --------------------------------------------------

conversation_store: Dict[str, List[dict]] = {}

# --------------------------------------------------
# CORS configuration for React
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str
    session_id:str


# --------------------------------------------------
# Helper: Get existing Qdrant client
# --------------------------------------------------

def get_qdrant_client():

    assistant = getattr(app.state, "assistant", None)

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Vedanta Assistant is not initialized."
        )

    retriever = assistant.retriever

    return retriever.client


# --------------------------------------------------
# 1. GET /
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to Vedanta Life Guidance API",
        "documentation": "/docs"
    }


# --------------------------------------------------
# 2. GET /health
# --------------------------------------------------

@app.get("/health")
def health_check():

    assistant = getattr(app.state, "assistant", None)

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Vedanta Assistant is not initialized."
        )

    return {
        "status": "healthy",
        "message": "Vedanta Assistant API is running"
    }


# --------------------------------------------------
# 3. POST /ask
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()
    session_id = request.session_id.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty."
        )

    assistant = getattr(app.state, "assistant", None)

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Vedanta Assistant is not initialized."
        )

    try:

        # Get existing conversation history
        history = conversation_store.get(session_id, [])

        # Generate answer using conversation history
        result = assistant.ask(
            question,
            history=history
        )

        answer = result.get("answer", "")

        # Save the latest conversation messages
        history.append({
            "role": "user",
            "content": question
        })

        history.append({
            "role": "assistant",
            "content": answer
        })

        # Keep only the latest 10 conversation turns
        history = history[-20:]

        conversation_store[session_id] = history

        return {
            "session_id": session_id,
            "answer": answer,
            "sources": result.get("sources", []),
            "retrieved_passages": result.get(
                "retrieved_passages", []
            )
        }

    except Exception as e:

        print(f"Error generating answer: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer."
        )




@app.delete("/sessions/{session_id}")
def clear_session(session_id: str):

    if session_id in conversation_store:
        del conversation_store[session_id]

    return {
        "message": "Conversation cleared.",
        "session_id": session_id
    }
# --------------------------------------------------
# 4. GET /passages
# --------------------------------------------------

@app.get("/passages")
def get_passages(
    topic: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500)
):

    try:

        client = get_qdrant_client()

        qdrant_filter = None

        # Filter passages by topic if provided.
        if topic:

            qdrant_filter = Filter(
                must=[
                    FieldCondition(
                        key="topic",
                        match=MatchValue(value=topic)
                    )
                ]
            )

        # Get total matching passage count.
        count_result = client.count(
            collection_name="vedanta_passages",
            count_filter=qdrant_filter,
            exact=True
        )

        # Retrieve passages directly from Qdrant.
        records, next_offset = client.scroll(
            collection_name="vedanta_passages",
            limit=limit,
            offset=None,
            scroll_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False
        )

        selected_fields = [
            "passage_id",
            "topic",
            "source_text",
            "source_summary",
            "english_explanation",
            "hindi_explanation",
            "keywords",
            "original_work",
            "author_commentator",
            "translator",
            "source_book",
            "section",
            "source_reference",
            "start_book_page",
            "end_book_page",
            "pdf_page",
            "core_teaching",
            "practical_situations"
        ]

        passages = []

        for record in records:

            payload = record.payload or {}

            passage = {
                key: payload.get(key)
                for key in selected_fields
            }

            passages.append(passage)

        return {
            "total": count_result.count,
            "returned": len(passages),
            "has_more": next_offset is not None,
            "passages": passages
        }

    except HTTPException:
        raise

    except Exception as e:

        print(f"Error retrieving passages: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve passages."
        )


# --------------------------------------------------
# 5. GET /topics
# --------------------------------------------------

@app.get("/topics")
def get_topics():

    try:

        client = get_qdrant_client()

        topics = set()
        offset = None

        # Read all topic values from Qdrant.
        while True:

            records, next_offset = client.scroll(
                collection_name="vedanta_passages",
                limit=256,
                offset=offset,
                with_payload=["topic"],
                with_vectors=False
            )

            for record in records:

                payload = record.payload or {}
                topic = payload.get("topic")

                if topic:
                    topics.add(topic)

            if next_offset is None:
                break

            offset = next_offset

        return {
            "total": len(topics),
            "topics": sorted(topics)
        }

    except Exception as e:

        print(f"Error retrieving topics: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve topics."
        )
