import json
from pathlib import Path
from typing import Dict, Optional
import re
from copy import deepcopy

FALLBACK_QUESTIONS = {
    "restaurant": {
        "Introduction": "En un restaurante, una camarera y un cliente estan hablando.",
        "Conversation": "Buenas tardes. Quiero pedir algo ligero. Tenemos sopa, ensalada y pescado. Entonces quiero la ensalada y un vaso de agua, por favor.",
        "Question": "Que va a pedir el cliente?",
        "Options": ["Una ensalada", "Un cafe", "Una hamburguesa", "Un pastel"],
        "Answer": 1,
    },
    "cafe": {
        "Introduction": "En una cafeteria, una persona esta haciendo un pedido.",
        "Conversation": "Hola, que desea tomar? Quiero un cafe con leche y un bocadillo pequeno. Para llevar o para tomar aqui? Para tomar aqui, gracias.",
        "Question": "Que bebida pide la persona?",
        "Options": ["Cafe con leche", "Te frio", "Jugo de naranja", "Agua mineral"],
        "Answer": 1,
    },
    "airport": {
        "Introduction": "En el aeropuerto, una pasajera habla con un empleado.",
        "Conversation": "Disculpe, donde esta la puerta doce? Siga recto y gire a la derecha despues de la tienda. El embarque empieza en veinte minutos.",
        "Question": "A donde tiene que ir la pasajera?",
        "Options": ["A la puerta doce", "A la salida principal", "Al restaurante", "A la estacion de tren"],
        "Answer": 1,
    },
    "hotel": {
        "Introduction": "En un hotel, un turista habla con la recepcionista.",
        "Conversation": "Buenas noches. Tengo una reserva a nombre de Garcia. Si, aqui esta. Su habitacion esta en el tercer piso y el desayuno empieza a las siete.",
        "Question": "En que piso esta la habitacion?",
        "Options": ["En el tercer piso", "En el primer piso", "En el quinto piso", "En la planta baja"],
        "Answer": 1,
    },
    "shopping": {
        "Introduction": "En una tienda, una clienta habla con un vendedor.",
        "Conversation": "Me gusta esta camisa, pero necesito una talla mas grande. Claro, tenemos una mediana en azul. Perfecto, me la pruebo.",
        "Question": "Que necesita la clienta?",
        "Options": ["Una talla mas grande", "Un color rojo", "Un precio mas bajo", "Un bolso nuevo"],
        "Answer": 1,
    },
    "travel": {
        "Introduction": "En la estacion, dos amigos hablan sobre su viaje.",
        "Conversation": "El tren sale a las nueve y media. Tenemos que comprar los boletos ahora. Si, y despues buscamos el anden numero cuatro.",
        "Question": "A que hora sale el tren?",
        "Options": ["A las nueve y media", "A las ocho", "A las diez y cuarto", "A las siete y media"],
        "Answer": 1,
    },
    "school": {
        "Introduction": "En la escuela, dos estudiantes hablan despues de clase.",
        "Conversation": "Tienes el libro de historia? No, lo deje en casa, pero tengo mis apuntes. Podemos estudiar en la biblioteca despues del almuerzo.",
        "Question": "Donde van a estudiar?",
        "Options": ["En la biblioteca", "En la cafeteria", "En casa", "En el parque"],
        "Answer": 1,
    },
    "directions": {
        "Introduction": "En la calle, una turista pide direcciones.",
        "Conversation": "Perdone, como llego al museo? Camine dos cuadras, gire a la izquierda y el museo esta frente al banco.",
        "Question": "Donde esta el museo?",
        "Options": ["Frente al banco", "Dentro del hotel", "Al lado del cafe", "Detras de la escuela"],
        "Answer": 1,
    },
}

FALLBACK_QUESTION_BANK = {
    "restaurant": [
        FALLBACK_QUESTIONS["restaurant"],
        {
            "Introduction": "En un restaurante, dos amigos miran el menu.",
            "Conversation": "Yo voy a pedir pescado con arroz. Yo prefiero la sopa del dia. Tambien podemos compartir una ensalada.",
            "Question": "Que quiere pedir una de las personas?",
            "Options": ["Pescado con arroz", "Cafe con leche", "Helado de chocolate", "Pan con queso"],
            "Answer": 1,
        },
        {
            "Introduction": "En un restaurante, una familia habla con el camarero.",
            "Conversation": "Tenemos una mesa para cuatro? Si, junto a la ventana. Perfecto, queremos sentarnos alli.",
            "Question": "Donde quiere sentarse la familia?",
            "Options": ["Junto a la ventana", "En la barra", "Fuera del restaurante", "Cerca de la cocina"],
            "Answer": 1,
        },
    ],
    "cafe": [
        FALLBACK_QUESTIONS["cafe"],
        {
            "Introduction": "En una cafeteria, una estudiante habla con el barista.",
            "Conversation": "Necesito algo caliente para estudiar. Tenemos chocolate caliente y te. Entonces quiero un chocolate caliente, por favor.",
            "Question": "Que pide la estudiante?",
            "Options": ["Chocolate caliente", "Agua fria", "Cafe solo", "Un refresco"],
            "Answer": 1,
        },
        {
            "Introduction": "En un cafe, dos companeros se encuentran por la manana.",
            "Conversation": "Quieres desayunar aqui? Si, tengo poco tiempo. Pedire un croissant y un te.",
            "Question": "Que comida va a pedir la persona?",
            "Options": ["Un croissant", "Una pizza", "Una sopa", "Un plato de arroz"],
            "Answer": 1,
        },
    ],
    "airport": [
        FALLBACK_QUESTIONS["airport"],
        {
            "Introduction": "En el aeropuerto, un pasajero escucha un anuncio.",
            "Conversation": "El vuelo a Madrid sale de la puerta siete. Los pasajeros pueden embarcar en diez minutos.",
            "Question": "De que puerta sale el vuelo?",
            "Options": ["De la puerta siete", "De la puerta doce", "De la puerta dos", "De la puerta veinte"],
            "Answer": 1,
        },
        {
            "Introduction": "En el aeropuerto, una mujer pregunta por su maleta.",
            "Conversation": "Mi maleta no salio en la cinta. De que color es? Es roja y tiene una etiqueta blanca.",
            "Question": "De que color es la maleta?",
            "Options": ["Roja", "Azul", "Negra", "Verde"],
            "Answer": 1,
        },
    ],
    "hotel": [
        FALLBACK_QUESTIONS["hotel"],
        {
            "Introduction": "En un hotel, una pareja pregunta por el desayuno.",
            "Conversation": "El desayuno esta incluido? Si, se sirve en el comedor desde las siete hasta las diez.",
            "Question": "Donde se sirve el desayuno?",
            "Options": ["En el comedor", "En la habitacion", "En la piscina", "En la recepcion"],
            "Answer": 1,
        },
        {
            "Introduction": "En la recepcion de un hotel, un huesped necesita ayuda.",
            "Conversation": "La llave no funciona. No hay problema, le doy otra. Su habitacion es la doscientos cuatro, verdad?",
            "Question": "Que problema tiene el huesped?",
            "Options": ["La llave no funciona", "No tiene reserva", "Perdio su equipaje", "Quiere cambiar de hotel"],
            "Answer": 1,
        },
    ],
    "shopping": [
        FALLBACK_QUESTIONS["shopping"],
        {
            "Introduction": "En una tienda de ropa, un cliente busca un regalo.",
            "Conversation": "Busco una bufanda para mi hermana. Tenemos esta azul y esta verde. Creo que la azul le va a gustar.",
            "Question": "Que color elige el cliente?",
            "Options": ["Azul", "Verde", "Rojo", "Negro"],
            "Answer": 1,
        },
        {
            "Introduction": "En el mercado, una mujer compra fruta.",
            "Conversation": "Cuanto cuestan las manzanas? Dos euros el kilo. Entonces quiero un kilo, por favor.",
            "Question": "Cuantas manzanas compra la mujer?",
            "Options": ["Un kilo", "Dos kilos", "Tres manzanas", "Media bolsa"],
            "Answer": 1,
        },
    ],
    "travel": [
        FALLBACK_QUESTIONS["travel"],
        {
            "Introduction": "En una oficina de turismo, un viajero pide informacion.",
            "Conversation": "Quiero visitar la catedral. Puede ir en autobus o caminar quince minutos. Prefiero caminar.",
            "Question": "Como va a ir el viajero?",
            "Options": ["Caminando", "En taxi", "En tren", "En bicicleta"],
            "Answer": 1,
        },
        {
            "Introduction": "En la estacion de autobuses, dos turistas hablan.",
            "Conversation": "El autobus a Sevilla sale a las cinco. Tenemos media hora para comprar agua.",
            "Question": "A que hora sale el autobus?",
            "Options": ["A las cinco", "A las cuatro", "A las seis", "A las cinco y media"],
            "Answer": 1,
        },
    ],
    "school": [
        FALLBACK_QUESTIONS["school"],
        {
            "Introduction": "En clase, una profesora habla con sus estudiantes.",
            "Conversation": "Manana tenemos examen de vocabulario. Estudien las palabras de la unidad tres.",
            "Question": "Que examen tienen manana?",
            "Options": ["De vocabulario", "De musica", "De historia", "De matematicas"],
            "Answer": 1,
        },
        {
            "Introduction": "En la escuela, un estudiante pregunta por una actividad.",
            "Conversation": "Cuando empieza el club de espanol? Empieza el jueves despues de clase, en el aula cinco.",
            "Question": "Cuando empieza el club?",
            "Options": ["El jueves", "El lunes", "El sabado", "El martes"],
            "Answer": 1,
        },
    ],
    "directions": [
        FALLBACK_QUESTIONS["directions"],
        {
            "Introduction": "En una plaza, un hombre pregunta por la farmacia.",
            "Conversation": "La farmacia esta lejos? No, cruce la plaza y gire a la derecha. Esta al lado de la panaderia.",
            "Question": "Donde esta la farmacia?",
            "Options": ["Al lado de la panaderia", "Detras del museo", "Dentro del banco", "Frente al hotel"],
            "Answer": 1,
        },
        {
            "Introduction": "En la calle, una persona busca la estacion.",
            "Conversation": "Siga todo recto hasta el semaforo. Luego gire a la izquierda y vera la estacion.",
            "Question": "Que debe hacer despues del semaforo?",
            "Options": ["Girar a la izquierda", "Tomar un taxi", "Entrar en una tienda", "Cruzar el puente"],
            "Answer": 1,
        },
    ],
}

try:
    import ollama
except ImportError:
    ollama = None

try:
    from .vector_store import QuestionVectorStore
except ImportError:
    if __package__:
        QuestionVectorStore = None
    else:
        try:
            from vector_store import QuestionVectorStore
        except ImportError:
            QuestionVectorStore = None

class QuestionGenerator:
    #This is the constructor for the QuestionGenerator class.
    # It initializes:
    #  client for generating questions via the model amazon.nova-lite-v1:0.
    # Vector store (QuestionVectorStore) – used to search for similar questions to provide context.
    # Model ID – points to a  LLM.
    def __init__(self):
        """Initialize Ollama client and vector store"""
        self.ollama_client = ollama.Client() if ollama else None
        self.vector_store = QuestionVectorStore() if QuestionVectorStore else None
        self.model_id = "llama3.2:1b"
        self.stored_questions_path = Path(__file__).resolve().parents[1] / "data" / "stored_questions.json"
        self.seen_questions: dict[str, set[str]] = {}

    # Sends a prompt to  and returns the generated text.
    # Uses converse API (  LLM) with a temperature of 0.7 (creativity).
    # Returns the generated question as a string.
    # Catches exceptions and prints them.
    def _invoke_ollama(self, prompt: str) -> Optional[str]:
        """Invoke local Ollama LLaMA model with the given prompt"""
        if not ollama:
            print("Ollama package is not installed; using local stored-question fallback.")
            return None
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

    def _question_signature(self, question: Dict) -> str:
        parts = [
            str(question.get("Introduction", "")),
            str(question.get("Situation", "")),
            str(question.get("Conversation", "")),
            str(question.get("Question", "")),
            "|".join(str(option) for option in question.get("Options", [])),
        ]
        return " ".join(parts).strip().lower()

    def _topic_key(self, topic: str = "general") -> str:
        return str(topic or "general").strip().lower()

    def _remember_question(self, topic: str, question: Dict) -> Dict:
        signature = self._question_signature(question)
        if signature:
            self.seen_questions.setdefault(self._topic_key(topic), set()).add(signature)
        return deepcopy(question)

    def _first_unseen_question(self, topic: str, questions: list[Dict]) -> Optional[Dict]:
        if not questions:
            return None

        topic_key = self._topic_key(topic)
        seen = self.seen_questions.setdefault(topic_key, set())
        for question in questions:
            signature = self._question_signature(question)
            if signature and signature not in seen:
                return self._remember_question(topic, question)

        seen.clear()
        return self._remember_question(topic, questions[0])

    def _load_stored_questions(self, topic: str = "general") -> list[Dict]:
        """Load locally saved questions when vector search or Ollama are unavailable."""
        if not self.stored_questions_path.exists():
            return []

        try:
            data = json.loads(self.stored_questions_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error loading stored questions: {e}")
            return []

        topic_lower = str(topic or "").lower()
        questions = []
        for item in data.values():
            question = item.get("question") if isinstance(item, dict) else None
            if not isinstance(question, dict):
                continue

            item_topic = str(item.get("topic", "")).lower()
            if topic_lower and topic_lower != "general" and topic_lower not in item_topic:
                continue

            if isinstance(question.get("Question"), dict):
                inner = question["Question"]
                question["Options"] = list(inner.values())
                question["Question"] = "¿Cuál es la respuesta correcta?"

            if "Options" in question and len(question["Options"]) == 4:
                questions.append(deepcopy(question))

        return questions

    def _fallback_question(self, topic: str = "general") -> Optional[Dict]:
        topic_key = str(topic or "").strip().lower()
        questions = self._load_stored_questions(topic)
        if topic_key in FALLBACK_QUESTIONS:
            questions.extend(FALLBACK_QUESTION_BANK.get(topic_key, [FALLBACK_QUESTIONS[topic_key]]))
        picked = self._first_unseen_question(topic, questions)
        if picked:
            return picked

        questions = self._load_stored_questions("general")
        picked = self._first_unseen_question(topic, questions)
        if picked:
            return picked

        return self._remember_question(topic, FALLBACK_QUESTIONS["restaurant"])

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
        if not self.vector_store:
            return self._fallback_question(topic)

        similar_questions = self.vector_store.search_similar_questions(section_num, topic, n_results=3)
        if not similar_questions:
            return self._fallback_question(topic)
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
        for _ in range(3):
            response = self._invoke_ollama(prompt)
            if not response:
                return self._fallback_question(topic)
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
                if self._question_signature(question) not in self.seen_questions.setdefault(self._topic_key(topic), set()):
                    print("[DEBUG] Cleaned parsed question:", json.dumps(question, ensure_ascii=False, indent=2))
                    return self._remember_question(topic, question)
            except Exception as e:
                print(f"Error parsing question JSON: {e}")
                print("Raw model response:\n", response)
                return self._fallback_question(topic)

        return self._fallback_question(topic)


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
