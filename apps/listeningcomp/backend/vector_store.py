import chromadb
from chromadb.utils import embedding_functions
import json
import os
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer

class LlamaEmbeddingFunction(embedding_functions.EmbeddingFunction):

    # Initializes a client to  for embeddings.
    # Sets the embedding model ID (Titan).
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):  # ✅ Valid embedding model
        """Initialize local embedding function"""
        self.model = SentenceTransformer(model_name)


    # Generates vector embeddings for a list of texts.
    # Uses invoke_model to send text to Titan embedder.
    # Returns a list of embedding vectors.
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using local model"""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return embeddings.tolist()  # Ensure output is list of lists
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * self.model.get_sentence_embedding_dimension() for _ in texts]

class QuestionVectorStore:

    # Generates vector embeddings for a list of texts.
    # Uses invoke_model to send text to  Titan embedder.
    # Returns a list of embedding vectors.
    def __init__(self, persist_directory: str = "backend/data/vectorstore"):
        """Initialize the vector store for Spanish listening questions"""
        self.persist_directory = persist_directory
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Use 's Titan embedding model
        self.embedding_fn = LlamaEmbeddingFunction()
        # Create or get collections for each section type
        self.collections = {
            "section2": self.client.get_or_create_collection(
                name="section2_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "Spanish listening comprehension questions - Section 2"}
            ),
            "section3": self.client.get_or_create_collection(
                name="section3_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "Spanish phrase matching questions - Section 3"}
            )
        }

    # Adds multiple questions to a collection.
    # Converts question content to a "document" string for embedding.
    # Stores full question structure as metadata.
    def add_questions(self, section_num: int, questions: List[Dict], video_id: str):
        """Add questions to the vector store"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, question in enumerate(questions):
            # Create a unique ID for each question
            question_id = f"{video_id}_{section_num}_{idx}"
            ids.append(question_id)
            
            # Store the full question structure as metadata
            metadatas.append({
                "video_id": video_id,
                "section": section_num,
                "question_index": idx,
                "full_structure": json.dumps(question)
            })
            
            # Create a searchable document from the question content
            if section_num == 2:
                document = f"""
                Situation: {question['Introduction']}
                Dialogue: {question['Conversation']}
                Question: {question['Question']}
                """
            else:  # section 3
                document = f"""
                Situation: {question['Situation']}
                Question: {question['Question']}
                """
            documents.append(document)
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    # Uses ChromaDB to retrieve the most similar questions given a query.
    # Returns list of question dictionaries with similarity_score.
    def search_similar_questions(
        self, 
        section_num: int, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar questions in the vector store"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # ✅ FIXED: Safe parsing with error handling
        questions = []
        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            for idx, metadata in enumerate(results['metadatas'][0]):
                try:
                    if 'full_structure' in metadata:
                        question_data = json.loads(metadata['full_structure'])
                        question_data['similarity_score'] = results['distances'][0][idx] if idx < len(results['distances'][0]) else 0.0
                        questions.append(question_data)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing metadata: {e}")
                    continue
        
        return questions  # Always return list, even empty


    # Retrieves a question by its unique ID from the collection
    def get_question_by_id(self, section_num: int, question_id: str) -> Optional[Dict]:
        """Retrieve a specific question by its ID"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        result = collection.get(
            ids=[question_id],
            include=['metadatas']
        )
        
        if result['metadatas']:
            return json.loads(result['metadatas'][0]['full_structure'])
    
# check the above line 
# if result['metadatas'] and result['metadatas'][0]:
    #return json.loads(result['metadatas'][0][0]['full_structure'])

    # Reads a text file with structured questions.
    # Converts it into a list of dictionaries with keys: Introduction, Conversation, Situation, Question, Options.
    def parse_questions_from_file(self, filename: str) -> List[Dict]:
        """Parse questions from a structured text file"""
        questions = []
        current_question = {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('<question>'):
                    current_question = {}
                elif line.startswith('Introduction:'):
                    i += 1
                    if i < len(lines):
                        current_question['Introduction'] = lines[i].strip()
                elif line.startswith('Conversation:'):
                    i += 1
                    if i < len(lines):
                        current_question['Conversation'] = lines[i].strip()
                elif line.startswith('Situation:'):
                    i += 1
                    if i < len(lines):
                        current_question['Situation'] = lines[i].strip()
                elif line.startswith('Question:'):
                    i += 1
                    if i < len(lines):
                        current_question['Question'] = lines[i].strip()
                elif line.startswith('Options:'):
                    options = []
                    for _ in range(4):
                        i += 1
                        if i < len(lines):
                            option = lines[i].strip()
                            if option.startswith('1.') or option.startswith('2.') or option.startswith('3.') or option.startswith('4.'):
                                options.append(option[2:].strip())
                    current_question['Options'] = options
                elif line.startswith('</question>'):
                    if current_question:
                        questions.append(current_question)
                        current_question = {}
                i += 1
            return questions
        except Exception as e:
            print(f"Error parsing questions from {filename}: {str(e)}")
            return []


    # Takes a question file → parses it → adds it to vector store
    def index_questions_file(self, filename: str, section_num: int):
        """Index all questions from a file into the vector store"""
        # Extract video ID from filename
        video_id = os.path.basename(filename).split('_section')[0]
        
        # Parse questions from file
        questions = self.parse_questions_from_file(filename)
        
        # Add to vector store
        if questions:
            self.add_questions(section_num, questions, video_id)
            print(f"Indexed {len(questions)} questions from {filename}")

if __name__ == "__main__":
    # Example usage
    store = QuestionVectorStore()
    
    # Index questions from files
    question_files = [
        ("backend/data/questions/sY7L5cfCWno_section2.txt", 2),
        ("backend/data/questions/sY7L5cfCWno_section3.txt", 3)
    ]
    
    for filename, section_num in question_files:
        if os.path.exists(filename):
            store.index_questions_file(filename, section_num)
    
    # Search for similar questions
    similar = store.search_similar_questions(2, "Pregunta sobre cumpleaños", n_results=1)
