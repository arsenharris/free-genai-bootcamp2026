import json
from typing import Dict, Optional
from backend.vector_store import QuestionVectorStore
import ollama
import re

class QuestionGenerator:
    #This is the constructor for the QuestionGenerator class.
    # It initializes:
    #  client for generating questions via the model amazon.nova-lite-v1:0.
    # Vector store (QuestionVectorStore) – used to search for similar questions to provide context.
    # Model ID – points to a  LLM.
    def __init__(self):
        """Initialize Ollama client and vector store"""
        # CORRECT:
        self.ollama_client = ollama.Client()  # Use the client directly
        self.vector_store = QuestionVectorStore()
        self.model_id = "llama3.2:1b"

    # Sends a prompt to  and returns the generated text.
    # Uses converse API (  LLM) with a temperature of 0.7 (creativity).
    # Returns the generated question as a string.
    # Catches exceptions and prints them.
    def _invoke_ollama(self, prompt: str) -> Optional[str]:
        """Invoke local Ollama LLaMA model with the given prompt"""
        try:
            # Call the Ollama local model
            response = ollama.generate(          # Direct function, not Client
                model=self.model_id,
                prompt=prompt,
                options={
                    'temperature': 0.7,        # ✅ Nested in options
                    'num_predict': 2000        # ✅ Correct param name
                }
            )
            return response['response']  
        except Exception as e:
            print(f"Error invoking Ollama: {str(e)}")
            return None

    # Generates a new listening question based on:
    # section_num ( section 2 or 3)
    # topic (e.g., "restaurant", "travel")
    # Uses your vector store to get 3 similar questions for context.
    # Builds a prompt that includes:
    # Example questions
    # Instructions for generating a new question
    # Requirement: exactly 4 options
    # Sends this prompt to _invoke_ollama.
    # Parses the response line by line to create a Python dictionary
    def generate_similar_question(self, section_num: int, topic: str) -> Dict:
        """Generate a new question similar to existing ones on a given topic"""
        # Get similar questions for context
        similar_questions = self.vector_store.search_similar_questions(section_num, topic, n_results=3)
        if not similar_questions:
            return None
        # Create context from similar questions
        context = "Here are some example Spanish listening questions:\n\n"
        for idx, q in enumerate(similar_questions, 1):
            if section_num == 2:
                context += f"Example {idx}:\n"
                context += f"Introduction: {q.get('Introduction', '')}\n"
                context += f"Conversation: {q.get('Conversation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{i}. {opt}\n"
            else:  # section 3
                context += f"Example {idx}:\n"
                context += f"Situation: {q.get('Situation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{i}. {opt}\n"
            context += "\n"
        # Create prompt for generating new question
        prompt = f"""
        You are a Spanish teacher generating listening comprehension questions.
        Based on the following example questions about **{topic}**, create ONE new question
        in the same style and difficulty. Use Spanish for all content.
        Return your answer *strictly* as a valid JSON object with this exact structure:
        {{
        "Introduction": "string (brief setup about the situation)",
        "Conversation": "string (a natural dialogue in Spanish)",
        "Question": "string (the actual question about what was heard)",
        "Options": ["option1", "option2", "option3", "option4"],
        "Answer": 1
        }}
        ⚠️ Important Rules:
        - The value of "Question" must be a Spanish question sentence — not JSON.
        - "Options" must be an array of four plain strings, not keys like opt1 or opt2.
        - Do not nest data inside other fields.
        - Do not include explanations or extra text; output the JSON only.
        Here are example questions for reference:
        {context}
        Now generate the new JSON object ONLY — no introductions, notes, or markdown.
        """
        # Generate new question
        response = self._invoke_ollama(prompt)
        if not response:
            return None
        # Parse the generated question
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in model output")
            raw_json = match.group(0)
            question = json.loads(raw_json)
            # --- Auto‑correct common model mistakes ---
            # Case 1: options nested inside 'Question' field
            if isinstance(question.get("Question"), dict):
                inner = question["Question"]
                if all(k.lower().startswith("opt") for k in inner.keys()):
                    question["Options"] = list(inner.values())
                    question["Question"] = "¿Cuál es la respuesta correcta?"  # generic fix
            # Case 2: options given as key:value instead of list
            if "Options" not in question and any(k.lower().startswith("opt") for k in question.keys()):
                opts = [v for k, v in question.items() if k.lower().startswith("opt")]
                question["Options"] = opts
            # --- Fill missing fields safely ---
            if section_num == 2:
                question.setdefault("Introduction", "Introducción no generada.")
                question.setdefault("Conversation", "Conversación no generada.")
            else:
                question.setdefault("Situation", "Situación no generada.")
            question.setdefault("Question", "Pregunta no generada.")
            if "Options" not in question or len(question["Options"]) != 4:
                question["Options"] = [
                    "Comer pizza", "Comer hamburguesa", "Comer ensalada", "Comer pasta"
                ]
            print("[DEBUG] Cleaned parsed question:", json.dumps(question, ensure_ascii=False, indent=2))
            return question
        except Exception as e:
            print(f"Error parsing question JSON: {e}")
            print("Raw model response:\n", response)
            return None


    # Generates a new  listening question based on:
    # section_num ( section 2 or 3)
    # topic (e.g., "restaurant", "travel")
    # Uses your vector store to get 3 similar questions for context.
    # Builds a prompt that includes:
    # Example questions
    # Instructions for generating a new question
    # Requirement: exactly 4 options
    # Sends this prompt to invoke_ollama.
    # Parses the response line by line to create a Python dictionary
    def get_feedback(self, question: Dict, selected_answer: int) -> Dict:
        """Generate feedback for the selected answer"""
        if not question or 'Options' not in question:
            return None
        correct_index = question.get("Answer")
        if correct_index:
            correct_index = int(correct_index)
            correct = (selected_answer == correct_index)
            explanation = (
                "¡Correcto! Elegiste la respuesta adecuada."
                if correct
                else f"La respuesta correcta era la opción {correct_index}: {question['Options'][correct_index - 1]}."
            )
            return {
                "correct": correct,
                "explanation": explanation,
                "correct_answer": correct_index
            }
        # Create prompt for generating feedback
        prompt = f"""Given this Spanish listening comprehension question and selected answer, 
        provide feedback in Spanish. Return as JSON with fields:
        - correct (true/false)
        - explanation (brief Spanish explanation)
        - correct_answer (number 1-4)
        Introduction: {question.get('Introduction', '')}
        Conversation: {question.get('Conversation', question.get('Situation', ''))}
        Question: {question.get('Question', '')}
        Options:
        {json.dumps(question['Options'], ensure_ascii=False)}
        Selected Answer: {selected_answer}
        """
        response = self._invoke_ollama(prompt)
        if 'Introduction' in question:
            prompt += f"Introduction: {question['Introduction']}\n"
            prompt += f"Conversation: {question['Conversation']}\n"
        else:
            prompt += f"Situation: {question['Situation']}\n"
        prompt += f"Question: {question['Question']}\n"
        prompt += "Options:\n"
        for i, opt in enumerate(question['Options'], 1):
            prompt += f"{i}. {opt}\n"
        prompt += f"\nSelected Answer: {selected_answer}\n"
        prompt += "\nProvide feedback in JSON format with these fields:\n"
        prompt += "- correct: true/false\n"
        prompt += "- explanation: brief explanation of why the answer is correct/incorrect\n"
        prompt += "- correct_answer: the number of the correct option (1-4)\n"
        # Get feedback
        response = self._invoke_ollama(prompt)
        if not response:
            return None
        try:
            # Parse the JSON response
            feedback = json.loads(response.strip())
            return feedback
        except:
            # If JSON parsing fails, return a basic response with a default correct answer
            return {
                "correct": False,
                "explanation": "Unable to generate detailed feedback. Please try again.",
                "correct_answer": 1  # Default to first option
            }
