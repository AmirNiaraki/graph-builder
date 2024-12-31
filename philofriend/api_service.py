from context_from_graph import GraphSearch
from typing import List, Tuple, Dict
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import logging
import argparse
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d  - %(message)s ')
logger = logging.getLogger(__name__)
# load the LLM model
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
import json

load_dotenv('/mnt/c/Users/amire/Desktop/graph-builder/philofriend/ENV.env')

class WisdomEngine:
    def __init__(self, philosophy: str = 'stoic'):
        self.philosophy = philosophy
        self.graph = GraphSearch()
        self.chat_bot()

    
    def chat_bot(self, model: str = "gpt-4o"):
        '''
        loads the chatbot as class attribute and produces logging for successful connection to langchain and openai
        '''
        os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
        ## Langmith tracking
        os.environ["LANGCHAIN_TRACING_V2"]="true"
        os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
        self.bot=ChatOpenAI(model=model)
        logger.info(f"Chatbot is ready with model: {model}")



    def find_relevant_discoveries(self, number_of_concepts: int = 3, input_summary: str = "I'm lost"):
        #TODO: use the value which is number of relationships each concept has
        concepts_dict = self.graph.get_concepts(sort=True)
        print(concepts_dict)
        concepts_list = list(concepts_dict.keys())
        print(concepts_list)
        local_context = f"""
        Given the following concepts: {concepts_list}, which {number_of_concepts} 
        is most relevant to the user's query? {input_summary} 

        provide your answer in json format such that it has {number_of_concepts} keys and 
        each key is the index of the concept in the list of concepts and its value is the concept.    

        do not include any other text in your answer. so that I can use it as a json object. like this:
        json.loads(your_answer)
        """
        
        bot_answer = self.bot.invoke([HumanMessage(content=local_context)])
        logging.info(f"bot_answer on most relevant discoveries: {bot_answer.content}")
        
        #cleaning the answer such that we remove all characters until we reach a '{'
        bot_answer_content = bot_answer.content[bot_answer.content.find("{"):]
        bot_answer_content = bot_answer_content[:bot_answer_content.find("}")+1]
        logging.info(f'bot_answer_content \n{bot_answer_content}')
        bot_answer_dict = json.loads(bot_answer_content)
        
        # First try to find concepts by their names in the values
        relevant_concepts = []
        for _, concept_name in bot_answer_dict.items():
            # Check if the concept exists directly in concepts_dict
            if concept_name in concepts_dict:
                relevant_concepts.append(concept_name)
        
        # If we found any concepts by name, return them
        if relevant_concepts:
            logging.info(f'Found relevant concepts by name: {relevant_concepts}')
            return relevant_concepts
            
        # Fallback: use indices if no direct matches found
        logging.info('No direct concept matches found, falling back to index-based lookup')
        relevant_concepts = [concepts_list[int(key)] for key in bot_answer_dict.keys()]
        logging.info(f'relevant_concepts from index lookup: {relevant_concepts}')
        return relevant_concepts

    def find_relevant_story(self, discovery: str, input_summary: str):
        # Assuming `context` is a list of dictionaries with 'text', 'fileName', and 'page_number' keys
        context = self.graph.get_context(concept=discovery, context_type="details")
        for i, ctx in enumerate(context):
            logger.info(f"Context {i}: {ctx}")
        # Extract all 'text' values from the context
        text_list = [entry['text'] for entry in context if 'text' in entry]
        
        local_context = f"""
        Given the following reflection which member of this list and make sure it does not include the work Introduction or translation
        {text_list}
        is most relevant to the user's query? {input_summary} 

        provide your answer exactly in two lines, the first line is the index of the text in the list of texts
        and the second line is the text itself given that indexing starts from 0. like this:
        12
        text
        """
        bot_answer = self.bot.invoke([HumanMessage(content=local_context)])
        logging.info(f"bot_answer on most relevant story: {bot_answer.content}")

        # Extract the index from the bot's response
        relevant_story_index = int(bot_answer.content.split('\n')[0])
        
        # Retrieve the relevant story details using the index
        relevant_story = context[relevant_story_index]
        relevant_text = relevant_story['text']
        relevant_file = relevant_story['fileName']
        relevant_page = relevant_story['page_number']
        
        return relevant_text, relevant_file, relevant_page

# chat_bot(contexts)
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process reflection summary for WisdomEngine.")
    parser.add_argument('-rs', '--reflection_summary', type=str, default="What is the meaning of life?", 
                        help='The reflection summary to process. Defaults to an example if not provided.')

    # Parse arguments
    args = parser.parse_args()
    reflection_summary = args.reflection_summary

    # Log the reflection summary being used
    logger.info(f"Using reflection summary: {reflection_summary}")

    # Initialize the WisdomEngine
    engine = WisdomEngine()
    
    # Find relevant discoveries
    discoveries = engine.find_relevant_discoveries(number_of_concepts=3, input_summary=reflection_summary)
    logger.info(f"Most relevant discoveries: {discoveries}")
    
    # Find relevant story
    story, book_name, page_number = engine.find_relevant_story(discovery=discoveries[0], input_summary=reflection_summary)

    logging.info(f"For the reflection summary of:\n {reflection_summary} \n the relevant discoveries in 'stoic philosophy' are:\n {discoveries}.\
                  \n  \n the most relevant story is:\n {story}... , \n  read more in {book_name} at page {page_number}")



