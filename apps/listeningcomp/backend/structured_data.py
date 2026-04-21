from typing import Optional, Dict, List
import os
import requests

# Model ID
#MODEL_ID = "amazon.nova-micro-v1:0"
MODEL_ID = "llama3.2:1b"

class TranscriptStructurer:

    # Sets the default model to amazon.nova-lite-v1:0.
    # Stores prompts for each section (1, 2, 3). Each prompt defines:
    # What to extract from the transcript
    # Which questions to include/exclude
    # Format for output <question>...</question>
    # Rules (no translation, ignore examples, etc.)
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Ollama client"""
        self.MODEL_ID = model_id
        self.ollama_url = "http://localhost:11434/api/generate"

        self.prompts = {
            1: """Extrae preguntas de la sección Sección 1 de esta transcripción de JLPT donde la respuesta pueda determinarse únicamente a partir de la conversación sin necesitar ayudas visuales.

            SOLO incluye preguntas que cumplan estos criterios:
            - La respuesta puede determinarse únicamente a partir del diálogo hablado
            - No se necesita información espacial/visual (como ubicaciones, planos o apariencias físicas)
            - No se deben comparar objetos físicos ni opciones visuales

            Por ejemplo, INCLUYE preguntas sobre:
            - Horarios y fechas
            - Números y cantidades
            - Elecciones o decisiones habladas
            - Indicaciones verbales claras

            NO incluyas preguntas sobre:
            - Ubicaciones físicas que requieran un mapa o diagrama
            - Elecciones visuales entre objetos
            - Distribuciones espaciales o planos
            - Apariencias físicas de personas o cosas

            Formatea cada pregunta exactamente así:

            <question>
            Introducción:
            [la situación planteada]

            Conversación:
            [el diálogo]

            Pregunta:
            [la pregunta a responder]

            Opciones:
            1. [primera opción]
            2. [segunda opción]
            3. [tercera opción]
            4. [cuarta opción]
            </question>

            Reglas:
            - Solo extrae preguntas de la Sección 1
            - Solo incluye preguntas cuyas respuestas puedan determinarse a partir del diálogo
            - Ignora cualquier ejemplo de práctica (marcado con Ej.)
            - No traduzcas el contenido de las preguntas
            - No incluyas descripciones de sección ni otro texto
            - Salida: preguntas una tras otra, sin texto adicional
            """,

            2: """Extrae preguntas de la sección Sección 2 de esta transcripción de JLPT donde la respuesta pueda determinarse únicamente a partir de la conversación sin necesitar ayudas visuales.

            SOLO incluye preguntas que cumplan estos criterios:
            - La respuesta puede determinarse únicamente a partir del diálogo hablado
            - No se necesita información espacial/visual (como ubicaciones, planos o apariencias físicas)
            - No se deben comparar objetos físicos ni opciones visuales

            Por ejemplo, INCLUYE preguntas sobre:
            - Horarios y fechas
            - Números y cantidades
            - Elecciones o decisiones habladas
            - Indicaciones verbales claras

            NO incluyas preguntas sobre:
            - Ubicaciones físicas que requieran un mapa o diagrama
            - Elecciones visuales entre objetos
            - Distribuciones espaciales o planos
            - Apariencias físicas de personas o cosas

            Formatea cada pregunta exactamente así:

            <question>
            Introducción:
            [la situación planteada]

            Conversación:
            [el diálogo]

            Pregunta:
            [la pregunta a responder]
            </question>

            Reglas:
            - Solo extrae preguntas de la Sección 2
            - Solo incluye preguntas cuyas respuestas puedan determinarse a partir del diálogo
            - Ignora cualquier ejemplo de práctica (marcado con Ej.)
            - No traduzcas el contenido de las preguntas
            - No incluyas descripciones de sección ni otro texto
            - Salida: preguntas una tras otra, sin texto adicional
            """,

            3: """Extrae todas las preguntas de la sección Sección 3 de esta transcripción de JLPT.

            Formatea cada pregunta exactamente así:

            <question>
            Situación:
            [la situación donde se necesita una frase]

            Pregunta:
            ¿Qué se dice?
            </question>

            Reglas:
            - Solo extrae preguntas de la Sección 3
            - Ignora cualquier ejemplo de práctica (marcado con Ej.)
            - No traduzcas el contenido de las preguntas
            - No incluyas descripciones de sección ni otro texto
            - Salida: preguntas una tras otra, sin texto adicional
            """
        }


    # Sends the transcript along with a section-specific prompt to Ollama.
    # Uses temperature=0 for deterministic output.
    # Returns Ollama's output as a string
    def _invoke_ollama(self, prompt: str, transcript: str) -> Optional[str]:
        """Make a single call to Ollama local API with the given prompt"""
        full_prompt = f"{prompt}\n\nHere's the transcript:\n{transcript}"

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_id,    # e.g., "llama3.2:1b"
                    "prompt": full_prompt,
                    "temperature": 0,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            data = response.json()
            # Ollama returns 'completion' instead of AWS's output.message.content
            return data.get("completion", None)
        except Exception as e:
            print(f"Error invoking Ollama: {str(e)}")
            return None


    # Iterates over sections 2 and 3 (skipping section 1).
    # Calls _invoke_ollama to generate questions for each section.
    # Stores each section’s output as a dictionary: {2: "...", 3: "..."}
    def structure_transcript(self, transcript: str) -> Dict[int, str]:
        """Structure the transcript into three sections using separate prompts (Ollama version)"""
        results = {}
        # Skipping section 1 for now
        for section_num in range(2, 4):
            result = self._invoke_ollama(self.prompts[section_num], transcript)
            if result:
                results[section_num] = result
        return results


    # Saves structured questions into files named *_section2.txt and *_section3.txt.
    # Automatically creates directories if they don’t exist.
    def save_questions(self, structured_sections: Dict[int, str], base_filename: str) -> bool:
        """Save each section to a separate file"""
        try:
            # Create questions directory if it doesn't exist
            os.makedirs(os.path.dirname(base_filename), exist_ok=True)
            
            # Save each section
            for section_num, content in structured_sections.items():
                filename = f"{os.path.splitext(base_filename)[0]}_section{section_num}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False

# Reads a transcript file and returns it as a string. 
    def load_transcript(self, filename: str) -> Optional[str]:
        """Load transcript from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None

if __name__ == "__main__":
    structurer = TranscriptStructurer()
    transcript = structurer.load_transcript("backend/data/transcripts/sY7L5cfCWno.txt")
    if transcript:
        structured_sections = structurer.structure_transcript(transcript)
        structurer.save_questions(structured_sections, "backend/data/questions/sY7L5cfCWno.txt")