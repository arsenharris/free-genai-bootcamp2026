import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.audio_generator import AudioGenerator

# Test question data
    # This is your sample Spanish question.
    # It includes Japanese text for: Introduction, Conversation, Question, and Options.
test_question = {
    "Introduction": "Escucha la siguiente conversación y responde la pregunta.",
    "Conversation": """
    Hombre: Disculpe, ¿este tren se detiene en la estación de Sol?
    Mujer: Sí, la próxima estación es Sol.
    Hombre: Gracias. ¿Cuánto tiempo tarda en llegar?
    Mujer: Aproximadamente 5 minutos.
    """,
    "Question": "¿Cuánto tiempo tarda en llegar a la estación de Sol?",
    "Options": [
        "3 minutos",
        "5 minutos",
        "10 minutos",
        "15 minutos"
    ]
}
# Instantiates your AudioGenerator class.
# Calls parse_conversation → splits the conversation into speaker-text pairs with gender.
# Calls generate_audio → converts the question into a TTS audio file.
def test_audio_generation():
    print("Initializing audio generator...")
    generator = AudioGenerator()
    
    print("\nParsing conversation...")
    parts = generator.parse_conversation(test_question)
    
    print("\nParsed conversation parts:")
    for speaker, text, gender in parts:
        print(f"Speaker: {speaker} ({gender})")
        print(f"Text: {text}")
        print("---")
    
    print("\nGenerating audio file...")
    audio_file = generator.generate_audio(test_question)
    print(f"Audio file generated: {audio_file}")
    
    return audio_file

if __name__ == "__main__":
    try:
        audio_file = test_audio_generation()
        print("\nTest completed successfully!")
        print(f"You can find the audio file at: {audio_file}")
    except Exception as e:
        print(f"\nError during test: {str(e)}")
