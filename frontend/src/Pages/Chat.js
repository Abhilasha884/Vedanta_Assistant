
import React, { useState } from "react";
import { askQuestion, clearSession } from "../Services/api";

function Chat() {

    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // Generate a unique ID for this conversation
    const [sessionId, setSessionId] = useState(() =>
        crypto.randomUUID()
    );

    // Submit question
    const handleSubmit = async (e) => {

        e.preventDefault();

        if (!question.trim()) {
            return;
        }

        const currentQuestion = question.trim();

        setLoading(true);
        setError("");

        try {

            const response = await askQuestion(
                currentQuestion,
                sessionId
            );

            // Store the new question, answer and sources
            const newMessage = {
                question: currentQuestion,
                answer: response.data.answer || "",
                sources: response.data.sources || []
            };

            // Preserve previous conversation messages
            setMessages(prev => [...prev, newMessage]);

            setQuestion("");

        } catch (err) {

            console.error("Error:", err);

            const detail = err.response?.data?.detail;

            if (Array.isArray(detail)) {

                setError(
                    detail.map(item => item.msg || JSON.stringify(item)).join(", ")
                );

            } else if (typeof detail === "string") {

                setError(detail);

            } else if (detail && typeof detail === "object") {

                setError(JSON.stringify(detail));

            } else {

                setError(
                    "Unable to get a response. Please try again."
                );
            }

        } finally {

            setLoading(false);

        }
    };

    // Start a new conversation
    const handleNewConversation = async () => {

        const previousSessionId = sessionId;

        // Generate a new session ID
        setSessionId(crypto.randomUUID());

        // Reset the UI
        setQuestion("");
        setMessages([]);
        setError("");

        // Clear previous conversation from backend
        try {

            await clearSession(previousSessionId);

        } catch (err) {

            console.error("Unable to clear previous session:", err);

        }
    };

    return (

        <div className="chat-container">

            <h1>Vedanta Life Guidance</h1>

            <p>
                Ask questions and explore the wisdom of Advaita Vedanta.
            </p>

            {/* Conversation history */}
            <div className="conversation-history">

                {messages.map((message, index) => (

                    <div className="conversation-item" key={index}>

                        {/* User question */}
                        <div className="user-message">

                            <h3>You</h3>

                            <p>{message.question}</p>

                        </div>

                        {/* Assistant answer */}
                        <div className="answer-container">

                            <h2>Vedanta's Guidance</h2>

                            <p>{message.answer}</p>

                            {/* Sources */}
                            {message.sources.length > 0 && (

                                <div className="sources">

                                    <h3>Sources</h3>

                                    <ul>

                                        {message.sources.map((source, sourceIndex) => {

                                            const startPage = source.start_book_page;
                                            const endPage = source.end_book_page;

                                            return (

                                                <li key={source.passage_id || sourceIndex}>

                                                    <strong>
                                                        {source.original_work || "Unknown source"}
                                                    </strong>

                                                    {source.source_reference && (
                                                        <>
                                                            {" — Reference: "}
                                                            {source.source_reference}
                                                        </>
                                                    )}

                                                    {startPage != null && (
                                                        <>
                                                            {" | "}

                                                            {startPage === endPage
                                                                ? "Page: "
                                                                : "Pages: "
                                                            }

                                                            {startPage}

                                                            {endPage != null &&
                                                                endPage !== startPage &&
                                                                `–${endPage}`
                                                            }
                                                        </>
                                                    )}

                                                </li>

                                            );

                                        })}

                                    </ul>

                                </div>

                            )}

                        </div>

                    </div>

                ))}

            </div>

            {/* Loading indicator */}
            {loading && (

                <div className="thinking">
                    <span className="loader"></span>
                    <span>Reflecting on your question...</span>
                </div>

            )}

            {/* Error message */}
            {error && (

                <p className="error">
                    {error}
                </p>

            )}

            {/* Question input */}
            <form onSubmit={handleSubmit}>

                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask your question here..."
                    rows="4"
                    disabled={loading}
                />

                {/* Action buttons */}
                <div className="chat-actions">

                    <button
                        type="submit"
                        disabled={loading || !question.trim()}
                    >
                        {loading ? "Thinking..." : "Ask Question"}
                    </button>

                    <button
                        type="button"
                        onClick={handleNewConversation}
                        disabled={loading}
                        className="new-conversation-btn"
                    >
                        New Conversation
                    </button>

                </div>

            </form>

        </div>

    );

}

export default Chat;
