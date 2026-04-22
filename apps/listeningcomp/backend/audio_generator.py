import os
from typing import Dict, List
import tempfile
import subprocess
from datetime import datetime
import asyncio
import edge_tts

class AudioGenerator:
    def __init__(self):
        # Local Ollama LLM configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.2"
        # Voice configuration (local TTS voices)
        self.voices = {
            "male": "es-ES-ElviraNeural",
            "female": "es-ES-ElviraNeural",
            "announcer": "es-ES-ElviraNeural"
        }
        # Create audio output directory
        self.audio_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs/listening/audio"
        )
        os.makedirs(self.audio_dir, exist_ok=True)

    def get_voice_for_gender(self, gender: str) -> str:
        """Get an appropriate voice id for the given gender/role.
        Falls back to the configured female voice when unknown.
        """
        if not gender:
            return self.voices.get("female")
        key = str(gender).lower()
        return self.voices.get(key, self.voices.get("female"))

    def generate_audio_part(self, text: str, voice_name: str) -> str:
        """
        Generate audio using edge-tts (free, no credentials).
        Returns path to mp3 file.
        """
        if not text or not text.strip():
            raise ValueError("Text for audio generation cannot be empty.")
        async def _generate():
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_file.close()
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(temp_file.name)
            return temp_file.name
        return asyncio.run(_generate())

    def combine_audio_files(self, audio_files: List[str], output_file: str):
        """Combine multiple audio files using ffmpeg"""
        file_list = None
        try:
            # Create file list for ffmpeg
            with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
                file_list = f.name
            # Combine audio files
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', file_list,
                '-c', 'copy',
                output_file
            ], check=True)
            return True
        except Exception as e:
            print(f"Error combining audio files: {str(e)}")
            if os.path.exists(output_file):
                os.unlink(output_file)
            return False
        finally:
            # Clean up temporary files
            if file_list and os.path.exists(file_list):
                os.unlink(file_list)
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    try:
                        os.unlink(audio_file)
                    except Exception as e:
                        print(f"Error cleaning up {audio_file}: {str(e)}")

    def generate_silence(self, duration_ms: int) -> str:
        """Generate a silent audio file of specified duration"""
        output_file = os.path.join(self.audio_dir, f'silence_{duration_ms}ms.mp3')
        if not os.path.exists(output_file):
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i',
                f'anullsrc=r=24000:cl=mono:d={duration_ms/1000}',
                '-c:a', 'libmp3lame', '-b:a', '48k',
                output_file
            ])
        return output_file

    def generate_audio(self, question: Dict) -> str:
        """Generate audio for the entire question - SIMPLIFIED"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.audio_dir, f"question_{timestamp}.mp3")
        try:
            # Handle a plain string payload
            if isinstance(question, str):
                text_to_speak = question
                voice = self.get_voice_for_gender(None)
                audio_file = self.generate_audio_part(text_to_speak, voice)
                import shutil
                shutil.copy2(audio_file, output_file)
                if os.path.exists(audio_file):
                    os.unlink(audio_file)
                return output_file
            # Handle single-text dict payloads
            if isinstance(question, dict) and ('Conversation' in question or 'Situation' in question or 'text' in question):
                text_to_speak = question.get('Conversation') or question.get('Situation') or question.get('text')
                gender = question.get('gender')
                voice = self.get_voice_for_gender(gender)
                audio_file = self.generate_audio_part(text_to_speak, voice)
                import shutil
                shutil.copy2(audio_file, output_file)
                if os.path.exists(audio_file):
                    os.unlink(audio_file)
                return output_file
            # Handle structured 'parts' payload (list of speaker parts)
            if isinstance(question, dict) and 'parts' in question and isinstance(question['parts'], list):
                parts = question['parts']
                audio_files = []
                pause_ms = int(question.get('pause_ms', 250))
                for part in parts:
                    if isinstance(part, dict):
                        text = part.get('text') or part.get('Conversation') or part.get('Situation')
                        gender = part.get('gender')
                    else:
                        text = str(part)
                        gender = None

                    if not text or not str(text).strip():
                        continue

                    voice = self.get_voice_for_gender(gender)
                    part_file = self.generate_audio_part(text, voice)
                    audio_files.append(part_file)
                    if pause_ms > 0:
                        audio_files.append(self.generate_silence(pause_ms))
                if not audio_files:
                    raise Exception("No valid parts to generate audio from")
                success = self.combine_audio_files(audio_files, output_file)
                if not success:
                    raise Exception("Failed to combine audio parts")
                return output_file
            # Nothing matched
            raise Exception("No conversation, situation, text, or parts found in question payload")
        except Exception as e:
            # Clean up the output file if it exists
            if os.path.exists(output_file):
                os.unlink(output_file)
            raise Exception(f"Audio generation failed: {str(e)}")



    # def _invoke_llm(self, prompt: str) -> str:
    #     """Invoke local Ollama model with the given prompt"""
    #     try:
    #         payload = {
    #             "model": self.model_name,
    #             "prompt": prompt,
    #             "stream": False,
    #             "options": {
    #                 "temperature": 0.3,
    #                 "top_p": 0.95,
    #                 "num_predict": 2000
    #             }
    #         }
    #         response = requests.post(self.ollama_url, json=payload)
    #         response.raise_for_status()
    #         result = response.json()
    #         return result["response"]
    #     except Exception as e:
    #         print(f"Error calling Ollama: {str(e)}")
    #         raise e

    # def validate_conversation_parts(self, parts: List[Tuple[str, str, str]]) -> bool:
    #     """
    #     Validate that the conversation parts are properly formatted.
    #     Returns True if valid, False otherwise.
    #     """
    #     if not parts:
    #         print("Error: No conversation parts generated")
    #         return False
            
    #     # Check that we have an announcer for intro
    #     if not parts[0][0].lower() == 'announcer':
    #         print("Error: First speaker must be Announcer")
    #         return False
            
    #     # Check that each part has valid content
    #     for i, (speaker, text, gender) in enumerate(parts):
    #         # Check speaker
    #         if not speaker or not isinstance(speaker, str):
    #             print(f"Error: Invalid speaker in part {i+1}")
    #             return False
                
    #         # Check text
    #         if not text or not isinstance(text, str):
    #             print(f"Error: Invalid text in part {i+1}")
    #             return False
                
    #         # Check gender
    #         if gender not in ['male', 'female']:
    #             print(f"Error: Invalid gender in part {i+1}: {gender}")
    #             return False
                
    #         # Check text contains Japanese characters
    #         if not any(c.isalpha() for c in text):
    #             print(f"Error: Text does not contain valid Spanish letters in part {i+1}")
    #             return False

        
    #     return True
    # def parse_conversation(self, question: Dict) -> List[Tuple[str, str, str]]:
    #     """
    #     Convert question into a format for audio generation.
    #     Returns a list of (speaker, text, gender) tuples.
    #     """
    #     max_retries = 3
    #     for attempt in range(max_retries):
    #         try:
    #             # Ask Nova to parse the conversation and assign speakers and genders
    #             prompt = f"""
    #             You are a Spanish listening comprehension audio script generator. Format the following question for audio generation.
    #             Rules:
    #             1. Introduction and Question parts:
    #             - Must start with 'Speaker: Announcer (Gender: male)'
    #             - Keep as separate parts
    #             2. Conversation parts:
    #             - Name speakers based on their role (Estudiante, Profesor, etc.)
    #             - Must specify gender EXACTLY as either 'Gender: male' or 'Gender: female'
    #             - Use consistent names for the same speaker
    #             - Split long speeches at natural pauses
    #             Example format:
    #             Speaker: Announcer (Gender: male)
    #             Text: Escucha la siguiente conversación y responde la pregunta.
    #             ---
    #             Speaker: Estudiante (Gender: female)
    #             Text: Disculpe, ¿este tren se detiene en la estación de Atocha?
    #             ---
    #             Question to format:
    #             {json.dumps(question, ensure_ascii=False, indent=2)}
    #             Output ONLY the formatted parts in order: introduction, conversation, question.
    #             Make sure to specify gender EXACTLY as shown in the example.
    #             """
                
    #             response = self._invoke_llm(prompt)
                
    #             # Parse the response into speaker parts
    #             parts = []
    #             current_speaker = None
    #             current_gender = None
    #             current_text = None
                
    #             # Track speakers to maintain consistent gender
    #             speaker_genders = {}
                
    #             for line in response.split('\n'):
    #                 line = line.strip()
    #                 if not line:
    #                     continue
                        
    #                 if line.startswith('Speaker:'):
    #                     # Save previous speaker's part if exists
    #                     if current_speaker and current_text:
    #                         parts.append((current_speaker, current_text, current_gender))
                        
    #                     # Parse new speaker and gender
    #                     try:
    #                         speaker_part = line.split('Speaker:')[1].strip()
    #                         current_speaker = speaker_part.split('(')[0].strip()
    #                         gender_part = speaker_part.split('Gender:')[1].split(')')[0].strip().lower()
                            
    #                         # Normalize gender
    #                         if 'masculino' in gender_part.lower() or 'hombre' in gender_part.lower() or 'male' in gender_part.lower():
    #                             current_gender = 'male'
    #                         elif 'femenino' in gender_part.lower() or 'mujer' in gender_part.lower() or 'female' in gender_part.lower():
    #                             current_gender = 'female'
    #                         else:
    #                             raise ValueError(f"Invalid gender format: {gender_part}")
                            
    #                         # Infer gender from speaker name for consistency
    #                         if current_speaker.lower() in ['female', 'woman', 'girl', 'lady', '女性']:
    #                             current_gender = 'female'
    #                         elif current_speaker.lower() in ['male', 'man', 'boy', '男性']:
    #                             current_gender = 'male'
                            
    #                         # Check for gender consistency
    #                         if current_speaker in speaker_genders:
    #                             if current_gender != speaker_genders[current_speaker]:
    #                                 print(f"Warning: Gender mismatch for {current_speaker}. Using previously assigned gender {speaker_genders[current_speaker]}")
    #                             current_gender = speaker_genders[current_speaker]
    #                         else:
    #                             speaker_genders[current_speaker] = current_gender
    #                     except Exception as e:
    #                         print(f"Error parsing speaker/gender: {line}")
    #                         raise e
                            
    #                 elif line.startswith('Text:'):
    #                     current_text = line.split('Text:')[1].strip()
                        
    #                 elif line == '---' and current_speaker and current_text:
    #                     parts.append((current_speaker, current_text, current_gender))
    #                     current_speaker = None
    #                     current_gender = None
    #                     current_text = None
                
    #             # Add final part if exists
    #             if current_speaker and current_text:
    #                 parts.append((current_speaker, current_text, current_gender))
                
    #             # Validate the parsed parts
    #             if self.validate_conversation_parts(parts):
    #                 return parts
                    
    #             print(f"Attempt {attempt + 1}: Invalid conversation format, retrying...")
                
    #         except Exception as e:
    #             print(f"Attempt {attempt + 1} failed: {str(e)}")
    #             if attempt == max_retries - 1:
    #                 raise Exception("Failed to parse conversation after multiple attempts")
        
    #     raise Exception("Failed to generate valid conversation format")
