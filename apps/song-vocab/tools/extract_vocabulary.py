from typing import List, Union, Optional
try:
    import instructor
except Exception:
    instructor = None
import ollama
import logging
from pydantic import BaseModel, ValidationError
from pathlib import Path
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

class Part(BaseModel):
    kanji: Optional[str]
    romaji: Union[List[str], str, None]

class VocabularyItem(BaseModel):
    kanji: Optional[str]
    romaji: Union[List[str], str, None]
    english: Optional[str]
    parts: Optional[List[Part]]

class VocabularyResponse(BaseModel):
    vocabulary: List[VocabularyItem]

async def extract_vocabulary(text: str) -> List[dict]:
    """
    Extract ALL vocabulary from Japanese text using LLM with structured output.
    
    Args:
        text (str): The text to extract vocabulary from
        
    Returns:
        List[dict]: Complete list of vocabulary items in Japanese format with kanji, romaji, and parts
    """
    logger.info("Starting vocabulary extraction")
    logger.debug(f"Input text length: {len(text)} characters")
    
    try:
        # Initialize Ollama client (use instructor.patch if available)
        logger.debug("Initializing Ollama client")
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
        all_vocabulary = set()
        max_attempts = 3
        
        for attempt in range(max_attempts):
            logger.info(f"Making LLM call attempt {attempt + 1}/{max_attempts}")
            try:
                try:
                    response = await client.chat(
                        model="mistral",
                        messages=[{"role": "user", "content": prompt}],
                        response_model=VocabularyResponse
                    )

                    # Add new vocabulary items to our set
                    # Convert to tuple since dict is not hashable
                    for item in response.vocabulary:
                        item_dict = item.dict()
                        item_tuple = tuple(sorted(item_dict.items()))
                        all_vocabulary.add(item_tuple)

                    logger.info(f"Attempt {attempt + 1} added {len(response.vocabulary)} items")
                except ValidationError as ve:
                    logger.error("Validation error parsing LLM output", exc_info=True)
                    # Fallback: call without response_model and try to extract JSON manually
                    raw = await client.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
                    content = ''
                    if isinstance(raw, dict):
                        content = raw.get('message', {}).get('content', '') or raw.get('content', '')
                    else:
                        content = str(raw)

                    # Try to extract JSON array/object from content
                    m = re.search(r'(\[.*\]|\{.*\})', content, re.DOTALL)
                    if not m:
                        logger.error("No JSON found in LLM raw content during fallback")
                        raise ve
                    try:
                        parsed = json.loads(m.group(1))
                        items = parsed if isinstance(parsed, list) else parsed.get('vocabulary', [])
                        for item in items:
                            # Normalize fields somewhat defensively
                            item_dict = {
                                'kanji': item.get('kanji'),
                                'romaji': item.get('romaji'),
                                'english': item.get('english'),
                                'parts': item.get('parts')
                            }
                            item_tuple = tuple(sorted(item_dict.items()))
                            all_vocabulary.add(item_tuple)
                        logger.info(f"Fallback parsing added {len(items)} items")
                    except Exception as e:
                        logger.error(f"Failed to parse JSON fallback: {e}", exc_info=True)
                        if attempt == max_attempts - 1:
                            raise
                
            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt == max_attempts - 1:
                    raise  # Re-raise on last attempt
        
        # Convert back to list of dicts
        result = [dict(item) for item in all_vocabulary]
        logger.info(f"Extracted {len(result)} unique vocabulary items")
        return result
        
    except Exception as e:
        logger.error(f"Failed to extract vocabulary: {str(e)}", exc_info=True)
        raise