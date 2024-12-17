from neo4j import GraphDatabase
from typing import Optional

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query: str, parameters: Optional[dict] = None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)

def initialize_philosophy_schema(neo4j_connection):
    # Define all your constraints
    constraints = [
        """CREATE CONSTRAINT IF NOT EXISTS FOR (p:Philosopher) 
           REQUIRE p.name IS UNIQUE""",
        """CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) 
           REQUIRE c.name IS UNIQUE""",
        """CREATE CONSTRAINT IF NOT EXISTS FOR (s:School) 
           REQUIRE s.name IS UNIQUE""",
        """CREATE CONSTRAINT IF NOT EXISTS FOR (w:Work) 
           REQUIRE w.title IS UNIQUE""",
    ]

    # Define your indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS FOR (p:Philosopher) ON (p.era)",
        "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.domain)",
        "CREATE INDEX IF NOT EXISTS FOR (s:School) ON (s.period)"
    ]

        # Define relationship types
    relationship_types = [
        "FOUNDED",
        "INFLUENCED",
        "CRITICIZED",
        "DEVELOPED",
        "TAUGHT",
        "WROTE",
        "BELONGS_TO",
        "PRECURSOR_TO"
    ]

    # Create relationship type constraints
    for rel_type in relationship_types:
        constraint_query = f"""
        CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:{rel_type}]->() 
        REQUIRE r.type IS NOT NULL
        """
        neo4j_connection.execute_query(constraint_query)

    # Execute all constraints and indexes
    for constraint in constraints:
        neo4j_connection.execute_query(constraint)
    
    for index in indexes:
        neo4j_connection.execute_query(index)

def main():
    # Replace these with your actual Neo4j credentials

    URI="neo4j+s://3ea576a5.databases.neo4j.io"
    USER="neo4j"
    PASSWORD="xiPxi9m3cIZBDkTb6_n4ncdgPqODiGzdGFSdN0c8aI0"

    try:
        # Create connection
        connection = Neo4jConnection(URI, USER, PASSWORD)
        print("Successfully connected to Neo4j database!")

        # Initialize schema
        initialize_philosophy_schema(connection)
        print("Successfully initialized schema!")

        # Example of adding a philosopher
        add_philosopher_query = """
        MERGE (p:Philosopher {
            name: $name,
            era: $era,
            birth_year: $birth_year,
            death_year: $death_year,
            nationality: $nationality
        })
        """
        
        philosopher_data = {
            "name": "Plato",
            "era": "Ancient Greek",
            "birth_year": -428,
            "death_year": -348,
            "nationality": "Greek"
        }

        connection.execute_query(add_philosopher_query, philosopher_data)
        print("Successfully added example philosopher!")

                # Example of adding a concept
        add_concept_query = """
        MERGE (c:Concept {
            name: $name,
            domain: $domain,
            definition: $definition,
            origin_era: $origin_era,
            related_fields: $related_fields
        })
        """
        
        concept_data = {
            "name": "Theory of Forms",
            "domain": "Metaphysics",
            "definition": "The philosophical idea that non-physical forms represent the most accurate reality.",
            "origin_era": "Ancient Greek",
            "related_fields": ["Epistemology", "Ontology"]
        }

        connection.execute_query(add_concept_query, concept_data)
        print("Successfully added example concept!")

        # Example of adding a relationship between a philosopher and a concept
        add_relationship_query = """
        MATCH (p:Philosopher {name: $philosopher_name})
        MATCH (c:Concept {name: $concept_name})
        MERGE (p)-[r:DEVELOPED {
            type: $relationship_type,
            year: $year,
            description: $description
        }]->(c)
        """
        
        relationship_data = {
            "philosopher_name": "Plato",
            "concept_name": "Theory of Forms",
            "relationship_type": "developed",
            "year": -380,
            "description": "Plato developed the Theory of Forms as a central concept in his philosophy."
        }

        connection.execute_query(add_relationship_query, relationship_data)
        print("Successfully added example relationship!")



    except Exception as e:
        print(f"An error occurred: {str(e)}")




    finally:
        # Always close the connection
        if 'connection' in locals():
            connection.close()
            print("Connection closed!")

if __name__ == "__main__":
    main()