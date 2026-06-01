from typing import List, Union, Optional
try:
    import instructor
except Exception:
    instructor = None
try:
    import ollama
except ImportError:
    ollama = None
import logging
from pydantic import BaseModel, ValidationError
from pathlib import Path
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

class Part(BaseModel):
    original: Optional[str]
    pronunciation: Union[List[str], str, None]

class VocabularyItem(BaseModel):
    original: Optional[str]
    pronunciation: Union[List[str], str, None]
    english: Optional[str]
    parts: Optional[List[Part]]

class VocabularyResponse(BaseModel):
    vocabulary: List[VocabularyItem]

async def extract_vocabulary(text: str) -> List[dict]:
    """
    Extract ALL vocabulary from Spanish text using LLM with structured output.
    
    Args:
        text (str): The text to extract vocabulary from
        
    Returns:
        List[dict]: Complete list of vocabulary items in Spanish format with original, pronunciation, and parts
    """
    logger.info("Starting vocabulary extraction")
    logger.debug(f"Input text length: {len(text)} characters")
    
    try:
        # Initialize Ollama client (use instructor.patch if available)
        logger.debug("Initializing Ollama client")
        if ollama is None:
            logger.warning("Ollama package is not installed; using local vocabulary fallback")
            return extract_vocabulary_locally(text)

        if instructor is not None:
            client = instructor.patch(ollama.Client())
        else:
            client = ollama.Client()
        
        # Load the prompt from the prompts directory
        prompt_path = Path(__file__).parent.parent / "prompts" / "Extract-Vocabulary.md"
        logger.debug(f"Loading prompt from {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Construct the full prompt with the text to analyze
        prompt = f"{prompt_template}\n\nText to analyze:\n{text}"
        logger.debug(f"Constructed prompt of length {len(prompt)}")
        
        # We'll use multiple calls to ensure we get all vocabulary
        # Use a set of JSON strings for safe deduplication (handles lists/dicts)
        all_vocabulary = set()
        max_attempts = 3
        
        for attempt in range(max_attempts):
            logger.info(f"Making LLM call attempt {attempt + 1}/{max_attempts}")
            try:
                # Try structured response first when Instructor is available.
                try:
                    if instructor is None:
                        raise RuntimeError("Instructor is not installed; using raw JSON fallback")

                    response = client.chat(
                        model="mistral",
                        messages=[{"role": "user", "content": prompt}],
                        response_model=VocabularyResponse
                    )

                    # Add new vocabulary items to our set
                    for item in response.vocabulary:
                        item_dict = item.dict()
                        item_json = json.dumps(item_dict, ensure_ascii=False, sort_keys=True)
                        all_vocabulary.add(item_json)

                    logger.info(f"Attempt {attempt + 1} added {len(response.vocabulary)} items")
                    continue
                except Exception as primary_err:
                    logger.warning("Structured response parsing failed, attempting raw fallback", exc_info=True)

                # Fallback: call without response_model and try to extract JSON manually
                raw = client.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
                content = ''
                if isinstance(raw, dict):
                    content = raw.get('message', {}).get('content', '') or raw.get('content', '')
                else:
                    content = str(raw)

                # Try to extract JSON array/object from content
                m = re.search(r'(\[.*\]|\{.*\})', content, re.DOTALL)
                if not m:
                    logger.error("No JSON found in LLM raw content during fallback")
                    # If we're on the last attempt, surface the original error
                    if attempt == max_attempts - 1:
                        raise primary_err
                    else:
                        continue

                parsed = json.loads(m.group(1))
                items = parsed if isinstance(parsed, list) else parsed.get('vocabulary', [])
                for item in items:
                    # Normalize fields somewhat defensively
                    item_dict = {
                        'original': item.get('original'),
                        'pronunciation': item.get('pronunciation'),
                        'english': item.get('english'),
                        'parts': item.get('parts')
                    }
                    item_json = json.dumps(item_dict, ensure_ascii=False, sort_keys=True)
                    all_vocabulary.add(item_json)
                logger.info(f"Fallback parsing added {len(items)} items")
            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt == max_attempts - 1:
                    raise  # Re-raise on last attempt
        
        # Convert back to list of dicts
        result = [json.loads(item_json) for item_json in all_vocabulary]
        logger.info(f"Extracted {len(result)} unique vocabulary items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to extract vocabulary: {str(e)}", exc_info=True)
        logger.warning("Using local vocabulary fallback")
        return extract_vocabulary_locally(text)


def extract_vocabulary_locally(text: str, limit: int = 40) -> List[dict]:
    """Small offline fallback so the app remains usable without Ollama."""
    translations = {
        "amor": "love",
        "corazon": "heart",
        "corazón": "heart",
        "vida": "life",
        "noche": "night",
        "dia": "day",
        "día": "day",
        "cancion": "song",
        "canción": "song",
        "bailar": "to dance",
        "quiero": "I want",
        "quieres": "you want",
        "siento": "I feel",
        "mundo": "world",
        "luz": "light",
        "sol": "sun",
        "luna": "moon",
        "mar": "sea",
        "ojos": "eyes",
        "voz": "voice",
        "tiempo": "time",
        "siempre": "always",
        "nunca": "never",
        "aqui": "here",
        "aquí": "here",
        "contigo": "with you",
        "sin": "without",
        "con": "with",
        "para": "for",
    }
    stopwords = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
        "que", "y", "o", "en", "a", "por", "mi", "tu", "su", "me", "te",
        "se", "lo", "es", "soy", "eres", "como", "más", "mas", "no", "sí",
        "si", "al", "todo", "toda", "ya",
    }
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿñÑáéíóúÁÉÍÓÚüÜ]+", text.lower())
    seen = set()
    vocabulary = []
    for word in words:
        if len(word) < 3 or word in stopwords or word in seen:
            continue
        seen.add(word)
        vocabulary.append({
            "original": word,
            "pronunciation": word,
            "english": translations.get(word, ""),
            "parts": [],
        })
        if len(vocabulary) >= limit:
            break
    return vocabulary
