'''
This is a python api that receives "Concept" and/or "Person" as input, 
connects to a neo4j knowledge graph and returns a context string (we have 
config object about this that includes the context length and other parameters)

It retrieves all the relationships for the concept and the person and also
relationships between those specific concepts and person. 

# Example usage
context = get_context(concept="Theory of Forms", person="Plato", context_type="all")
print(context)
'''
import os
import logging
from neo4j import GraphDatabase
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Neo4jConnection:
    def __init__(self):
        # uri = os.getenv("NEO4J_URI")
        # user = os.getenv("NEO4J_USERNAME")
        # password = os.getenv("NEO4J_PASSWORD")
        uri = "neo4j+s://06e4c224.databases.neo4j.io"
        user= "neo4j"
        password= "4G0Zho5qR74tXjkiSYOxu9B08jYvbt5quK1UqImIK90"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("Connected to Neo4j graph")

    def close(self):
        self.driver.close()
        logger.info("Disconnected from Neo4j graph")

    def execute_query(self, query: str, parameters: Optional[dict] = None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            # logger.debug(f"Executed query: {query}")
            return list(result)

class Config:
    CONTEXT_LENGTH = 1000  # Adjust as needed
    MAX_RELATIONSHIPS = 100  # Adjust as needed


class GraphSearch:
    def __init__(self):
        self.connection = Neo4jConnection()

    # def __del__(self):
    #     self.connection.close()
    def close(self):
        self.connection.close()

    def get_relationships(self, concept: Optional[str] = None, person: Optional[str] = None) -> str:
        try:
            context = []
            
            # Check if both concept and person exist
            if concept and person:
                concept_query = """
                MATCH (c:Concept)
                WHERE c.id = $concept
                RETURN count(c) > 0 AS concept_exists
                """
                concept_exists = self.connection.execute_query(concept_query, {"concept": concept})[0]['concept_exists']
                logger.info(f"Executed query to check if concept '{concept}' exists")
                
                person_query = """
                MATCH (p:Person)
                WHERE p.id = $person
                RETURN count(p) > 0 AS person_exists
                """
                person_exists = self.connection.execute_query(person_query, {"person": person})[0]['person_exists']
                logger.info(f"Executed query to check if person '{person}' exists")
                
                both_exist = concept_exists and person_exists
                if both_exist:
                    # Query for direct relationship between concept and person
                    direct_relation_query = """
                    MATCH (c:Concept {id: $concept})-[r]-(p:Person {id: $person})
                    RETURN c, r, p
                    LIMIT $limit
                    """
                    direct_results = self.connection.execute_query(direct_relation_query, {"concept": concept, "person": person, "limit": Config.MAX_RELATIONSHIPS})
                    logger.info(f"Executed query to find direct relationship between concept '{concept}' and person '{person}'")
                    
                    if direct_results:
                        context.extend(self.format_results(direct_results))
                        logger.info(f"Found direct relationship between concept '{concept}' and person '{person}'")
                        return f"Both '{concept}' and '{person}' are available in the graph. " + " ".join(context)[:Config.CONTEXT_LENGTH]
                    else:
                        logger.info(f"No direct relationship found between concept '{concept}' and person '{person}'")
            
            # If no direct relationship or not both exist, find general relationships for each
            if concept:
                concept_query = """
                MATCH (c:Concept)
                WHERE c.id = $concept
                OPTIONAL MATCH (c)-[r]-(related)
                RETURN c, r, related
                LIMIT $limit
                """
                concept_results = self.connection.execute_query(concept_query, {"concept": concept, "limit": Config.MAX_RELATIONSHIPS})
                logger.info(f"Executed query to find relationships for concept '{concept}'")
                context.extend(self.format_results(concept_results))
                logger.info(f"Found {len(concept_results)} relationships for concept '{concept}'")
            
            if person:
                person_query = """
                MATCH (p:Person)
                WHERE p.id = $person
                OPTIONAL MATCH (p)-[r]-(related)
                RETURN p, r, related
                LIMIT $limit
                """
                person_results = self.connection.execute_query(person_query, {"person": person, "limit": Config.MAX_RELATIONSHIPS})
                logger.info(f"Executed query to find relationships for person '{person}'")
                context.extend(self.format_results(person_results))
                logger.info(f"Found {len(person_results)} relationships for person '{person}'")
            
            if not context:
                logger.info("No information found for the given concept or person")
                return "No information found for the given concept or person."
            
            return " ".join(context)[:Config.CONTEXT_LENGTH]
        
        except Exception as e:
            logger.error(f"Error in get_relationships: {str(e)}")
            return f"An error occurred: {str(e)}"

    def get_details(self, concept: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            if concept:
                details_query = """
                MATCH (chunk:Chunk)-[r]-(concept:Concept) 
                WHERE concept.id = $concept
                RETURN properties(chunk) AS chunk_properties
                """
                details_results = self.connection.execute_query(details_query, {"concept": concept})
                logger.info(f"Executed query to get details for concept '{concept}'")
                
                useful_context_dict = []
   
                for result in details_results:
                    chunk_properties = result['chunk_properties']

                    useful_context_dict.append({
                        'text': chunk_properties.get('text', ''),
                        'fileName': chunk_properties.get('fileName', ''),
                        'page_number': chunk_properties.get('page_number', '')
                    })
                
                logger.info(f"Found {len(useful_context_dict)} chunks for concept '{concept}'")
                # print(useful_context_dict[0])
                return useful_context_dict
            else:
                logger.warning("No concept provided for details.")
                return []
        
        except Exception as e:
            logger.error(f"Error in get_details: {str(e)}")
            return []

    def get_context(self, concept: Optional[str] = None, person: Optional[str] = None, context_type: str = "all") -> str:
        if context_type == "relationships":
            relationships = self.get_relationships(concept, person)
            self.close()
            return relationships
        elif context_type == "details":
            details=self.get_details(concept)
            self.close()
            return details
        elif context_type == "all":
            relationships = self.get_relationships(concept, person)
            details = self.get_details(concept)
            self.close()
            return f"Relationships: {relationships}\n\nDetails: {details}"
        else:
            return "Invalid context type. Please use 'relationships', 'details', or 'all'."

    @staticmethod
    def format_results(results: List[Dict]) -> List[str]:
        formatted = []
        for record in results:
            for key, value in record.items():
                if hasattr(value, "type"):
                    formatted.append(f"{key}: {value.type}")
                elif isinstance(value, dict):
                    formatted.append(f"{key}: {', '.join([f'{k}: {v}' for k, v in value.items()])}")
        return formatted

# This context needs to be summarized by another model
graph=GraphSearch()
# contexts = graph.get_context(concept="Geist", person="Hegel", context_type="details")
contexts = graph.get_context(concept="Soul", person="Hegel", context_type="details")

print(contexts[0], contexts[10])