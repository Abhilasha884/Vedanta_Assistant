
import React, { useEffect, useState } from "react";
import { getTopics, getPassages } from "../Services/api";

function Explore() {
    const [topics, setTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState("");
    const [passages, setPassages] = useState([]);

    const [loadingTopics, setLoadingTopics] = useState(true);
    const [loadingPassages, setLoadingPassages] = useState(false);
    const [error, setError] = useState("");

    // Fetch all available topics when the page loads
    useEffect(() => {
        const fetchTopics = async () => {
            try {
                const response = await getTopics();
                setTopics(response.data.topics || []);
            } catch (err) {
                console.error("Error fetching topics:", err);
                setError("Unable to load topics. Please try again.");
            } finally {
                setLoadingTopics(false);
            }
        };

        fetchTopics();
    }, []);

    // Fetch passages when a topic is selected
    const handleTopicSelect = async (topic) => {
        setSelectedTopic(topic);
        setPassages([]);
        setError("");
        setLoadingPassages(true);

        try {
            const response = await getPassages(topic);
            setPassages(response.data.passages || []);
        } catch (err) {
            console.error("Error fetching passages:", err);
            setError("Unable to load passages. Please try again.");
        } finally {
            setLoadingPassages(false);
        }
    };

    // Convert machine-friendly topic into readable text
    const formatTopic = (topic) => {
        return topic
            .split("_")
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    };

    return (
        <div className="explore-container">

            <h1>Explore Vedanta Topics</h1>

            <p>
                Explore different topics and discover the teachings
                of Advaita Vedanta.
            </p>

            {/* Topics Section */}
            <section className="topics-section">
                <h2>Available Topics</h2>

                {loadingTopics && <p>Loading topics...</p>}

                {!loadingTopics && topics.length === 0 && !error && (
                    <p>No topics available.</p>
                )}

                <div className="topics-list">
                    {topics.map((topic) => (
                        <button
                            key={topic}
                            className={
                                selectedTopic === topic
                                    ? "topic-button selected"
                                    : "topic-button"
                            }
                            onClick={() => handleTopicSelect(topic)}
                        >
                            {formatTopic(topic)}
                        </button>
                    ))}
                </div>
            </section>

            {/* Error Message */}
            {error && <p className="error">{error}</p>}

            {/* Passages Section */}
            {selectedTopic && (
                <section className="passages-section">

                    <h2>{formatTopic(selectedTopic)}</h2>

                    {loadingPassages && <p>Loading passages...</p>}

                    {!loadingPassages && passages.length === 0 && (
                        <p>No passages found for this topic.</p>
                    )}

                    {!loadingPassages && passages.map((passage, index) => (
                        <div
                            className="passage-card"
                            key={passage.passage_id || index}
                        >
                            <h3>Passage {index + 1}</h3>

                            {passage.source_summary && (
                                <p>
                                    <strong>Summary:</strong>{" "}
                                    {passage.source_summary}
                                </p>
                            )}

                            {passage.core_teaching && (
                                <p>
                                    <strong>Core Teaching:</strong>{" "}
                                    {passage.core_teaching}
                                </p>
                            )}

                            {passage.english_explanation && (
                                <p>
                                    <strong>English Explanation:</strong>{" "}
                                    {passage.english_explanation}
                                </p>
                            )}

                            {passage.hindi_explanation && (
                                <p>
                                    <strong>Hindi Explanation:</strong>{" "}
                                    {passage.hindi_explanation}
                                </p>
                            )}

                            <div className="passage-source">
                                <strong>Source:</strong>{" "}
                                {passage.original_work || "Unknown"}

                                {passage.source_reference && (
                                    <> — {passage.source_reference}</>
                                )}

                                {passage.start_book_page != null && (
                                    <>
                                        {" | "}
                                        {passage.start_book_page === passage.end_book_page
                                            ? "Page: "
                                            : "Pages: "
                                        }
                                        {passage.start_book_page}

                                        {passage.end_book_page != null &&
                                            passage.end_book_page !== passage.start_book_page &&
                                            `–${passage.end_book_page}`
                                        }
                                    </>
                                )}
                            </div>
                        </div>
                    ))}

                </section>
            )}

        </div>
    );
}

export default Explore;
