from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAI
from langchain.chains.summarize import load_summarize_chain
import logging
from vertexai.generative_models import GenerativeModel
from langchain.prompts import PromptTemplate
from tqdm import tqdm
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiProcessor:
    def __init__(self, model_name, project):
        self.model = VertexAI(model_name=model_name, project=project)
    
    def generate_document_summary(self, documents: list, **args):
        chain_type = "map_reduce" if len(documents) > 10 else "stuff"
        
        chain = load_summarize_chain(llm=self.model, chain_type=chain_type, **args)
        return chain.run(documents)
    
    def get_model(self):
        return self.model
        
    def count_total_tokens(self, docs: list):
        temp_model = GenerativeModel("gemini-1.0-pro")
        total = 0
        logger.info("Counting total tokens...")
        for doc in tqdm(docs):
            total += temp_model.count_tokens(doc.page_content).total_billable_characters
        return total

class YoutubeProcessor:
    def __init__(self, genai_processor: GeminiProcessor):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.GeminiProcessor = genai_processor
    
    def retrieve_youtube_documents(self, video_url: str, verbose=False):
        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        docs = loader.load()
        result = self.text_splitter.split_documents(docs)
        
        author = result[0].metadata['author']
        length = result[0].metadata['length']
        title = result[0].metadata['title']
        total_size = len(result)
        total_billable_characters = self.GeminiProcessor.count_total_tokens(result)
        
        if verbose:
            logger.info(f"{author}\n{length}\n{title}\n{total_size}\n{total_billable_characters}")
        return result
        
    def find_key_concepts(self, documents: list, group_size: int = 0, verbose=True):
        #iterate through all documents of group size N and find key concepts
        if group_size > len(documents):
            raise ValueError("Group size is larger than number of documents")
            
        #optimize group size with no input
        if group_size == 0:
            group_size = len(documents)//5
            if verbose:
                logging.info(f"No group size specified. getting number of documents per sample as 5 group_size : {group_size}")
        #find number of documents in each group
        
        num_docs_per_group = len(documents) // group_size + (len(documents) % group_size > 0)
        if num_docs_per_group > 10:
            raise ValueError("Each group has more than 10 documents and output quality will be degraded significantly. Increase the group_size parameter to reduce the number of documents per group.")
        elif num_docs_per_group > 5:
            logging.warn("Each group has more than 5 documents and output quality is likely to be degraded consider increasing the group size")
        groups = [documents[i: i + num_docs_per_group] for i in range(0, len(documents), num_docs_per_group)]
        
        batch_concepts = []
        batch_cost = 0
        formatted_concepts = []  # Initialize formatted_concepts here
        
        logger.info("Finding key concepts...")
        
        for group in tqdm(groups):
            group_content = ""
            for doc in group:
                group_content += doc.page_content
            
            prompt = PromptTemplate(
                template="""
                Find and define key concepts of terms found in the text: {text}
                
                Respond in the following format as a Json object without any backticks, separating each concept with a comma:
                {{"concept": "definition", "concept": "definition", "concept": "definition",...}}
                """,
                input_variables=["text"]
            )
            chain = prompt | self.GeminiProcessor.model
            
            concept = chain.invoke({"text": group_content})
            concept = concept.replace("```json\n", "").replace("\n```", "") 
            batch_concepts.append(concept)
            
            if verbose:
                total_input_char = len(group_content)
                total_input_cost = (total_input_char / 1000) * 0.000125
                total_output_char = len(concept)
                total_output_cost = (total_output_char / 1000) * 0.000375
                
                logging.info(f"Running chain on {len(group)} documents")
                logging.info(f"Total input characters: {total_input_char}")
                logging.info(f"Total input cost: {total_input_cost}")
                logging.info(f"Total output characters: {total_output_char}")
                logging.info(f"Total output cost: {total_output_cost}")
                
                batch_cost += total_input_cost + total_output_cost
                logging.info(f"Total Group Cost: {total_input_cost + total_output_cost}\n")
            
        for concept in batch_concepts:
            # Remove triple backticks and newlines from JSON data
            concept = concept.replace("```json\n", "").replace("\n```", "")
            try:
                concept_dict = json.loads(concept)
                formatted_concepts.extend(self.format_concept_dict(concept_dict))
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse JSON: {concept}")
        
        logging.info(f"Total Analysis cost: ${batch_cost}")
        
        return formatted_concepts

    def format_concept_dict(self, concept_dict):
        formatted_concepts = []
        for concept, definition in concept_dict.items():
            formatted_concepts.append({"concept": concept, "definition": definition})
        return formatted_concepts

