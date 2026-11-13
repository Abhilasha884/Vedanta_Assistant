
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from rag.retriever import VedantaRetriever
import time

MODEL_NAME = "qwen3:4b"


class VedantaAssistant:

    def __init__(self):

        # Initialize Qdrant retriever
        self.retriever = VedantaRetriever()

        # Initialize Ollama LLM
        self.llm = ChatOllama(
            model=MODEL_NAME,
            temperature=0.3
        )

        # -----------------------------------------
        # DOMAIN CLASSIFICATION PROMPT
        # -----------------------------------------

        self.classification_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
You are a domain classifier for a Vedanta-based life guidance assistant.

Your task is to determine whether the user's question
belongs to the intended domain of the assistant.

IN_DOMAIN:
Questions about:
- Advaita Vedanta and spirituality
- Self, Atman, Brahman and consciousness
- Karma, duty, action and attachment
- Desire, anger, suffering and ignorance
- Liberation, self-knowledge and non-duality
- Everyday life situations that can reasonably be
  explored through Vedanta teachings, such as fear,
  failure, relationships, decisions and purpose.

OUT_OF_DOMAIN:
Questions unrelated to Vedanta, spirituality,
philosophy or relevant life guidance.

Examples:
- Product recommendations
- Programming questions
- Shopping recommendations
- Weather and general factual questions
- Entertainment recommendations

IMPORTANT RULES:
- Understand the meaning and intent of the question.
- Do not classify only by matching keywords.
- Everyday life questions can be IN_DOMAIN even without
  philosophical terminology.
- Do not assume every emotional or personal question
  must have a Vedanta-based answer.
- Do not force a Vedanta connection for unrelated questions.
- If the question is unclear or insufficiently related
  to the assistant's purpose, classify it as OUT_OF_DOMAIN.

Return exactly one of these labels:
IN_DOMAIN
OUT_OF_DOMAIN

Do not provide explanations or additional text.

User question:
{question}

Classification:
"""
        )

        # Classification chain
        self.classification_chain = (
            self.classification_prompt
            | self.llm
            | StrOutputParser()
        )

        # -----------------------------------------
        # MAIN ANSWER GENERATION PROMPT
        # -----------------------------------------

        self.prompt = PromptTemplate(
            input_variables=["question", "context", "chat_history"],
            template="""
You are a warm, thoughtful and practical Vedanta-based life guidance assistant.

Your purpose is to help users reflect on everyday life situations
using the teachings contained in the supplied Vedanta passages.

IMPORTANT RULES:

1. Use only the supplied passages to make claims about Vedanta.
2. Never invent quotations, Sanskrit verses, authors,
   commentators or source references.
3. Do not present invented examples or metaphors as scriptural teachings.
4. Clearly distinguish the original Vedanta teaching from
   your own practical suggestions.
5. Do not assume that a user's problem is caused by a particular
   Vedantic concept.
6. Do not dismiss practical factors such as preparation,
   external circumstances, expectations or lack of resources.
7. If the supplied passages do not sufficiently support an answer,
   explain this honestly instead of guessing.
8. Do not force a Vedanta connection for unrelated questions.
9. Use simple, respectful, empathetic and accessible language.
10. Identify the language of the user's question and respond
    in that language.
11. If the user writes in Hinglish, respond naturally in Hinglish.
12. Do not present philosophical guidance as medical or
    professional mental health treatment.
13. Do not claim that a difficult experience is a sign
    of spiritual growth or progress unless the retrieved
    passages explicitly support that claim.
14. Do not use philosophical teachings to dismiss,
    minimize, or explain away real-life difficulties.
15. When applying a teaching to a personal situation,
    clearly distinguish what the source says from your
    own practical interpretation.
16. Cite only the most relevant retrieved passages.
    Avoid citing duplicate or overlapping passages unnecessarily.
17. Include only the passages actually used in the response.
    Do not list every retrieved passage.

CONVERSATION HISTORY:

{chat_history}

Use the conversation history to understand the user's
previous questions and follow-up references.

For example, if the user asks "How can I apply this?",
use the previous conversation to understand what "this" refers to.

IMPORTANT:
- Conversation history is provided only for context and continuity.
- Do not treat previous assistant responses as authoritative
  Vedanta sources.
- Do not use previous assistant responses as evidence for
  philosophical claims.
- Ground all Vedanta explanations in the retrieved passages
  provided for the current question.
- The current user question takes priority over previous topics.

RESPONSE STYLE:

Write directly to the user in a natural conversational style.

- Begin with a brief, empathetic acknowledgement of the concern.
- Introduce the relevant Vedanta teaching naturally.
- Explain how the teaching may help the user reflect on the situation.
- Offer a few practical suggestions or reflection questions when relevant.
- End with a reassuring but realistic thought when appropriate.

FORMATTING RESTRICTIONS:

- Do not use numbered sections.
- Do not display headings such as "Understanding the situation",
  "Relevant Vedanta teaching" or "Practical reflection".
- Do not mention passage IDs, similarity scores, retrieval,
  embeddings, prompts or internal technical processes.
- Do not repeat the entire source passage.
- Avoid unnecessary repetition.
- Keep the response concise and conversational.

SOURCE REFERENCES:

At the end, include a short "Source" section.
Mention only passages that directly support the explanation.
Use the original work, reference and book page information
provided in the context.
Do not invent or modify references.

LANGUAGE RULES:

1. Detect the language used in the user's question.
2. You MUST write the entire response in the same language.
3. If the question is in Hindi, respond entirely in natural Hindi (Devanagari script).
4. If the question is in English, respond entirely in English.
5. Do not respond in English when the user asks in Hindi.
6. Keep Sanskrit philosophical terms such as Atman, Brahman,
   Karma and Moksha where appropriate, and explain them in Hindi.
7. Do not translate source references or original Sanskrit titles.

RETRIEVED VEDANTA PASSAGES:
{context}

USER QUESTION:
{question}

Now write the response for the user.
"""
        )

        # Main answer generation chain
        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

    # -----------------------------------------
    # DOMAIN CLASSIFICATION FUNCTION
    # -----------------------------------------

    def classify_question(self, question: str):

        result = self.classification_chain.invoke({
            "question": question
        })

        classification = result.strip().upper()

        # Accept only the two permitted labels
        if classification not in [
            "IN_DOMAIN",
            "OUT_OF_DOMAIN"
        ]:
            return "OUT_OF_DOMAIN"

        return classification

    # -----------------------------------------
    # MAIN ASK FUNCTION
    # -----------------------------------------

    def ask(self, question: str, history: list | None = None):

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        # Prepare recent conversation history
        history = history or []

        recent_history = history[-6:]

        chat_history = "\n".join(
            f"{'User' if message['role'] == 'user' else 'Assistant'}: "
            f"{message['content']}"
            for message in recent_history
        )

        if not chat_history:
            chat_history = "No previous conversation."

        # Step 1: Domain classification
        classification = self.classify_question(question)

        print(f"\nDomain Classification: {classification}")

        # Stop if the question is outside the domain
        if classification == "OUT_OF_DOMAIN":

            return {
                "answer": (
                    "I'm designed to help with questions related "
                    "to Advaita Vedanta and its application to "
                    "everyday life. Please ask me something "
                    "within this area."
                ),
                "sources": [],
                "retrieved_passages": []
            }

        # Step 2: Prepare contextual retrieval query

        retrieval_query = question

        if history:

            # Find the most recent question asked by the user
            previous_user_questions = [
                message["content"]
                for message in history
                if message["role"] == "user"
            ]

            if previous_user_questions:

                previous_question = previous_user_questions[-1]

                # Identify questions that depend on previous context
                follow_up_markers = [
                    "this", "that", "it", "these", "those",
                    "same", "apply", "explain further",
                    "daily life", "more about",
                    "इसका", "इसे", "इसको", "यह", "इस बारे में"
                ]

                question_lower = question.lower()

                is_follow_up = (
                    len(question.split()) <= 8
                    or any(
                        marker in question_lower
                        for marker in follow_up_markers
                    )
                )

                if is_follow_up:

                    retrieval_query = (
                        previous_question + "\n" + question
                    )

        # Step 3: Retrieve relevant passages from Qdrant
        passages = self.retriever.retrieve(retrieval_query)

        if not passages:

            return {
                "answer": (
                    "I could not find sufficiently relevant "
                    "passages in the available Vedanta knowledge "
                    "base to answer this question reliably."
                ),
                "sources": [],
                "retrieved_passages": []
            }

        # Step 4: Prepare retrieved passages as context
        context_parts = []

        sources = []

        for passage in passages:

            context_parts.append(
                f"""
Passage ID: {passage.get('passage_id')}
Topic: {passage.get('topic')}
Source: {passage.get('original_work')}
Reference: {passage.get('source_reference')}
Summary: {passage.get('source_summary')}
Core teaching: {passage.get('core_teaching')}
English explanation: {passage.get('english_explanation')}
Hindi explanation: {passage.get('hindi_explanation')}
"""
            )

            sources.append({
                "passage_id": passage.get("passage_id"),
                "original_work": passage.get("original_work"),
                "source_reference": passage.get("source_reference"),
                "start_book_page": passage.get("start_book_page"),
                "end_book_page": passage.get("end_book_page"),
                "pdf_page": passage.get("pdf_page")
            })

        context = "\n".join(context_parts)

        start_time = time.time()

        # Step 5: Generate grounded answer
        answer = self.chain.invoke({
            "question": question,
            "context": context,
            "chat_history": chat_history
        })

        print(f"LLM generation time: {time.time() - start_time:.2f} seconds")

        # Step 6: Return answer and source metadata
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_passages": passages
        }

    # -----------------------------------------
    # CLOSE RETRIEVER
    # -----------------------------------------

    def close(self):

        self.retriever.close()


# ---------------------------------------------
# TEST THE COMPLETE RAG PIPELINE
# ---------------------------------------------

def main():

    assistant = VedantaAssistant()

    try:

        print("\nVedanta Life Guidance Assistant")
        print("=" * 50)

        while True:

            question = input(
                "\nAsk your question (or type 'exit'): "
            )

            if question.strip().lower() == "exit":
                break

            try:

                result = assistant.ask(question)

                print("\nAssistant Response:")
                print("-" * 60)
                print(result["answer"])

                print("\nSource References:")

                if result["sources"]:

                    for source in result["sources"]:

                        print(
                            f"- {source['passage_id']}: "
                            f"{source['original_work']}, "
                            f"{source['source_reference']}, "
                            f"Book pages "
                            f"{source['start_book_page']}-"
                            f"{source['end_book_page']}"
                        )

                else:
                    print("No relevant source references found.")

            except Exception as error:

                print(f"\nError: {error}")

    finally:

        assistant.close()


if __name__ == "__main__":
    main()
