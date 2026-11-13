
import axios from "axios";

const API = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json"
    }
});

// Check backend health
export const checkHealth = () => API.get("/health");

// Get all available topics
export const getTopics = () => API.get("/topics");

// Get passages, optionally filtered by topic
export const getPassages = (topic = null) =>
    API.get("/passages", {
        params: topic ? { topic } : {}
    });

// Ask a question with its conversation session ID
export const askQuestion = (question, sessionId) =>
    API.post("/ask", {
        question: question,
        session_id: sessionId
    });

// Clear a conversation session
export const clearSession = (sessionId) =>
    API.delete(`/sessions/${sessionId}`);

export default API;
