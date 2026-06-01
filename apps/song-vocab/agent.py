try:
    import ollama
except ImportError:
    ollama = None
from typing import List, Dict, Any, Optional
import json
import logging
import re
import asyncio
from pathlib import Path
from functools import partial
try:
    from .tools.search_web_serp import search_web_serp
    from .tools.get_page_content import get_page_content
    from .tools.extract_vocabulary import extract_vocabulary, extract_vocabulary_locally
    from .tools.generate_song_id import generate_song_id
    from .tools.save_results import save_results
except ImportError:
    from tools.search_web_serp import search_web_serp
    from tools.get_page_content import get_page_content
    from tools.extract_vocabulary import extract_vocabulary, extract_vocabulary_locally
    from tools.generate_song_id import generate_song_id
    from tools.save_results import save_results
import math

# Get the app's root logger
logger = logging.getLogger('song_vocab')

class ToolRegistry:
    def __init__(self, lyrics_path: Path, vocabulary_path: Path):
        self.lyrics_path = lyrics_path
        self.vocabulary_path = vocabulary_path
        self.tools = {
            'search_web_serp': search_web_serp,
            'get_page_content': get_page_content,
            'extract_vocabulary': extract_vocabulary,
            'generate_song_id': generate_song_id,
            'save_results': partial(save_results, lyrics_path=lyrics_path, vocabulary_path=vocabulary_path)
        }
    
    def get_tool(self, name: str):
        return self.tools.get(name)

def calculate_safe_context_window(available_ram_gb: float, safety_factor: float = 0.8) -> int:
    """
    Calculate a safe context window size based on available RAM.
    
    Args:
        available_ram_gb (float): Available RAM in gigabytes
        safety_factor (float): Factor to multiply by for safety margin (default 0.8)
        
    Returns:
        int: Recommended context window size in tokens
        
    Note:
        Based on observation that 128K tokens requires ~58GB RAM
        Ratio is approximately 0.45MB per token (58GB/131072 tokens)
    """
    # Known ratio from our testing
    GB_PER_128K_TOKENS = 58.0
    TOKENS_128K = 131072
    
    # Calculate tokens per GB
    tokens_per_gb = TOKENS_128K / GB_PER_128K_TOKENS
    
    # Calculate safe token count
    safe_tokens = math.floor(available_ram_gb * tokens_per_gb * safety_factor)
    
    # Round down to nearest power of 2 for good measure
    power_of_2 = 2 ** math.floor(math.log2(safe_tokens))
    
    # Cap at 128K tokens
    final_tokens = min(power_of_2, TOKENS_128K)
    
    logger.debug(f"Context window calculation:")
    logger.debug(f"  Available RAM: {available_ram_gb}GB")
    logger.debug(f"  Tokens per GB: {tokens_per_gb}")
    logger.debug(f"  Raw safe tokens: {safe_tokens}")
    logger.debug(f"  Power of 2: {power_of_2}")
    logger.debug(f"  Final tokens: {final_tokens}")
    
    return final_tokens

class SongLyricsAgent:
    def __init__(self, stream_llm=True, available_ram_gb=32):
        logger.info("Initializing SongLyricsAgent")
        self.base_path = Path(__file__).parent
        self.prompt_path = self.base_path / "prompts" / "Lyrics-Agent.md"
        if not self.prompt_path.exists():
            self.prompt_path = self.base_path / "prompts" / "Lyrics-Angent.md"
        self.lyrics_path = self.base_path / "outputs" / "lyrics"
        self.vocabulary_path = self.base_path / "outputs" / "vocabulary"
        self.stream_llm = stream_llm
        self.context_window = calculate_safe_context_window(available_ram_gb)
        logger.info(f"Calculated safe context window size: {self.context_window} tokens for {available_ram_gb}GB RAM")
        
        # Create output directories
        self.lyrics_path.mkdir(parents=True, exist_ok=True)
        self.vocabulary_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directories created: {self.lyrics_path}, {self.vocabulary_path}")
        
        # Initialize Ollama client and tool registry
        logger.info("Initializing Ollama client and tool registry")
        try:
            self.client = ollama.Client() if ollama else None
            self.tools = ToolRegistry(self.lyrics_path, self.vocabulary_path)
            logger.info("Initialization successful")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def parse_llm_action(self, content: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Parse the LLM's response to extract tool name and arguments.

        Supports two argument formats:
        - JSON object inside parentheses: Tool: name({"arg": "value"})
        - simple assignments: Tool: name(arg1="value1", arg2=123)
        """
        match = re.search(r'Tool:\s*(\w+)\((.*?)\)', content, re.DOTALL)
        if not match:
            return None

        tool_name = match.group(1)
        args_str = match.group(2).strip()

        # Try JSON parsing first
        if args_str.startswith('{') and args_str.endswith('}'):
            try:
                args = json.loads(args_str)
                return tool_name, args
            except Exception:
                pass

        # Fallback: parse simple assignments like key="value", key=123
        args = {}
        import ast
        # Use double-quoted raw string to avoid quoting issues
        for m in re.finditer(r"(\w+)\s*=\s*(\"[^\"]*\"|'[^']*'|[^,]+)", args_str):
            key = m.group(1)
            val_raw = m.group(2).strip()
            # Try literal eval to handle numbers, booleans, strings
            try:
                val = ast.literal_eval(val_raw)
            except Exception:
                # Fallback: strip surrounding quotes if present
                if (val_raw.startswith('"') and val_raw.endswith('"')) or (val_raw.startswith("'") and val_raw.endswith("'")):
                    val = val_raw[1:-1]
                else:
                    val = val_raw
            args[key] = val

        return tool_name, args
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        tool = self.tools.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool Unknown: {tool_name}")
        
        logger.info(f"Tool Execute: {tool_name} with args: {args}")
        try:
            result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
            logger.info(f"Tool Succeeded: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Tool Failed: {tool_name} - {e}")
            raise

    def _get_llm_response(self, conversation):
        """Get response from LLM with optional streaming.
        
        Args:
            conversation (list): List of conversation messages
            
        Returns:
            dict: Response object with 'content' key
        """
        if self.stream_llm:
            # Stream response and collect tokens
            full_response = ""
            logger.info("Streaming tokens:")
            for chunk in self.client.chat(
                model="llama3.2:3b",
                messages=conversation,
                stream=True
            ):
                content = chunk.get('message', {}).get('content', '')
                if content:
                    logger.info(f"Token: {content}")
                    full_response += content

            # Normalize to the same structure returned by non-streaming
            return {'message': {'role': 'assistant', 'content': full_response}}
        else:
            # Non-streaming response
            try:
                response = self.client.chat(
                    model="llama3.2:3b",
                    messages=conversation,
                    options={
                        "num_ctx": self.context_window
                    }
                )
                # Log context window usage
                prompt_tokens = response.get('prompt_eval_count', 0)
                total_tokens = prompt_tokens + response.get('eval_count', 0)
                logger.info(f"Context window usage: {prompt_tokens}/{2048} tokens (prompt), {total_tokens} total tokens")
                
                logger.info(f"  Message ({response['message']['role']}): {response['message']['content'][:300]}...")
                # Ensure the response is in the expected dict format
                return response
            except Exception as e:
                logger.error(f"LLM response error: {e}")
                # Return a minimal response to prevent crashes
                return {'message': {'role': 'assistant', 'content': 'Error: Context too large. Please try with less context.'}}
    
    async def process_request(self, message: str) -> str:
        """Process a user request using the ReAct framework."""
        logger.info("-"*20)

        if not self.client:
            return await self.process_request_locally(message)
        
        # Initialize conversation with system prompt and user message
        conversation = [
            {"role": "system", "content": self.prompt_path.read_text()},
            {"role": "user", "content": message}
        ]
        
        max_turns = 10
        current_turn = 0
        
        while current_turn < max_turns:
            try:
                logger.info(f"[Turn {current_turn + 1}/{max_turns}]")
                try:
                    # Log the request payload
                    logger.info(f"Request:")
                    for msg in conversation[-2:]:  # Show last 2 messages for context
                        logger.info(f"  Message ({msg['role']}): {msg['content'][:300]}...")

                    response = self._get_llm_response(conversation)

                    #breakpoint()
                    
                    if not isinstance(response, dict) or 'message' not in response or 'content' not in response['message']:
                        raise ValueError(f"Unexpected response format from LLM: {response}")
                    
                    # Extract content from the message
                    content = response.get('message', {}).get('content', '')
                    if content.startswith('Error:'):
                        logger.warning("LLM unavailable; using local fallback")
                        return await self.process_request_locally(message)

                    if not content or not content.strip():
                        breakpoint()
                        logger.warning("Received empty response from LLM")
                        conversation.append({"role": "system", "content": "Your last response was empty. Please process the previous result and specify the next tool to use, or indicate FINISHED if done."})
                        continue

                    response = {'content': content}
                    
                    # Parse the action
                    action = self.parse_llm_action(response['content'])
                    
                    if not action:
                        if 'FINISHED' in response['content']:
                            logger.info("LLM indicated task is complete")
                            return response['content']
                        else:
                            logger.warning("No tool call found in LLM response")
                            conversation.append({"role": "system", "content": "Please specify a tool to use or indicate FINISHED if done."})
                            continue
                except Exception as e:
                    logger.error(f"Error getting LLM response: {e}")
                    logger.debug("Last conversation state:", exc_info=True)
                    for msg in conversation[-2:]:
                        logger.debug(f"Message ({msg['role']}): {msg['content']}")
                    raise
                
                # Execute the tool
                tool_name, tool_args = action
                logger.info(f"Executing tool: {tool_name}")
                logger.info(f"Arguments: {tool_args}")
                result = await self.execute_tool(tool_name, tool_args)
                logger.info(f"Tool execution complete")

                # If we've just saved results, return the song_id immediately
                if tool_name == 'save_results':
                    logger.info("save_results completed — returning song_id")
                    return result
                
                # Add the interaction to conversation
                conversation.extend([
                    {"role": "assistant", "content": response['content']},
                    {"role": "system", "content": f"Tool {tool_name} result: {json.dumps(result)}"}
                ])
                
                current_turn += 1
                
            except Exception as e:
                logger.error(f"❌ Error in turn {current_turn + 1}: {e}")
                logger.error(f"Stack trace:", exc_info=True)
                conversation.append({"role": "system", "content": f"Error: {str(e)}. Please try a different approach."})
        
        logger.warning("Reached maximum turns; using local fallback")
        return await self.process_request_locally(message)

    async def process_request_locally(self, message: str) -> str:
        """Offline fallback for pasted lyrics or demos when Ollama/search are unavailable."""
        title, artist = self._guess_song_details(message)
        song_id = generate_song_id(artist=artist, title=title)["song_id"]
        lyrics = self._extract_pasted_lyrics(message)
        vocabulary = extract_vocabulary_locally(lyrics)
        save_results(
            song_id=song_id,
            lyrics=lyrics,
            vocabulary=vocabulary,
            lyrics_path=self.lyrics_path,
            vocabulary_path=self.vocabulary_path,
        )
        return song_id

    def _guess_song_details(self, message: str) -> tuple[str, str]:
        by_match = re.search(r"(?P<title>.+?)\s+by\s+(?P<artist>.+)", message, re.I)
        if by_match:
            return by_match.group("title").strip(), by_match.group("artist").strip()

        for prefix in ("find lyrics for", "lyrics for", "song"):
            if message.lower().startswith(prefix):
                return message[len(prefix):].strip() or "sample song", "unknown artist"

        return "sample song", "unknown artist"

    def _extract_pasted_lyrics(self, message: str) -> str:
        markers = ["lyrics:", "letra:"]
        lower = message.lower()
        for marker in markers:
            if marker in lower:
                index = lower.index(marker) + len(marker)
                lyrics = message[index:].strip()
                if lyrics:
                    return lyrics

        return (
            "Estas son letras de ejemplo para probar la aplicación.\n"
            "Canto con mi corazón en la noche.\n"
            "La vida sigue con luz y amor."
        )
        if not self.client:
            return {'message': {'role': 'assistant', 'content': 'Error: Ollama Python package is not installed.'}}
