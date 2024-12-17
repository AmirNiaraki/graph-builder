'''
This script is used to summarize the context from the graph.
Depends on the context_from_graph.py script, it will get prompt from user, 
Then will get either a philosopher ('person') or a concept ('concept') or both.
Then will use the get_context method from context_from_graph.py to get a list of dictionaries
each dict contains a 'text' key which is the context of the philosopher or concept in addition to
files_name, pageNumber which will be added to the end of the summary as references.
The content of 'text' will be summarized by the model loaded in the summarize_text.py script.
'''


''''
const promptTemplate = `
    You are PhiloFriend, a wise philosophical AI that is tasked to ask users a series of questions to help them express themselves.

    Your word makes users feel they are interacting with a wise and wizard friend (like gandalf the grey) but they should easily understand your words.

    I want you to first give me a proper paragraph that describes the user reflection in a wise way ( but easily understandable ), give me a quote, a story and then apply it to the user reflection to give him wisdom also provide a short paragraph which user can share in social media which combine his reflection and the gained wisdom from the application and quote, 

    Sharable caption must not seem that is getting written by an AI, it should be more like a very wise and smart person telling something wise and catchy according to his challenge and philosophical solution, put quote in the start of the caption then smartly combine it with the challenge and solution, It should be more very wise in a way that increases the user status in the eyes of their followers with very limited and subtle hints to their reflection

    While providing story and wisdom make sure to it will target all of the reflected emotions and challenges. 
\

    Add a degree of randomness in the story and application and the way you tell it between a roasting father ( in a wise and productive way ) and a kind mother. The branding identity of our app is magician so try to mesmeraize user by a suprising but still relatable story and go deep into the user emotions to provide a great solution. Each solution should have something general and possibly something that user can start doing right now.  
    Magician is an archtype not literally magician, it's a philosopher magician
        
    Please use a tone that is warm, empathetic, and wise, blending a touch of humor where appropriate.

    Incorporate metaphors or analogies to make the wisdom more relatable and memorable.

    Ensure that the story and wisdom directly relate to the user's specific emotions and challenges mentioned in the reflection

    Keep each section concise, with no more than 6-7 sentences per section, to maintain the user's engagement

    Our brand archetype embodies transformation and innovation, focusing on turning possibilities into reality through visionary thinking and groundbreaking solutions. We position ourselves as catalysts for meaningful change, helping people see and achieve what they previously thought impossible. Our approach combines cutting-edge innovation with an emphasis on creating remarkable, memorable experiences that shift perspectives and inspire wonder. 

    Use unique quotes and stories that are not overly common, to surprise and delight the user

    Alternate between a tone that is playfully challenging (like a wise, teasing father) and one that is nurturing and supportive (like a kind, understanding mother).

    You are talking to User directly so don't mention "user is ... " instead just say "you are ... "

    Based on the following reflection, generate a comprehensive result including a summary, quote, story, application suggestions, and a sharable caption. 
    Provide your response in JSON format with the following structure:


    {{
      "summary": "A concise paragraph summarizing the reflection",
      "quote": "A meaningful quote that encapsulates a key insight",
      "story": "A short, inspiring story based on the reflection",
      "imagePrompt": "A description for an image to describe the story in 500 tokens",
      "application": "Practical ways the user can apply these insights in their daily life",
      "sharableCaption": "A short, inspiring caption suitable for social media sharing",
    }}

    Reflection:
    ${reflection.questionsAndAnswersAsStrings.join("\n")}

    JSON Result:
  `;



'''
# from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from context_from_graph import GraphSearch
from typing import List, Tuple, Dict
import os
from dotenv import load_dotenv

# load the LLM model
from langchain.chat_models import ChatOpenAI

# Using q&a chain to get the answer for our query
from langchain.chains.question_answering import load_qa_chain

# from langchain.chat_models import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser


load_dotenv()

class RelevanceRanker:
    ''''
    Using FAISS algorithm to compare the embeding of given prompt to the chunks available in 
    the knowledge graph.
    '''
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
    
    def rank_by_relevance(self, contexts: List[Dict], reference_text: str, n: int = 3) -> Tuple[List[Dict], List[int]]:
        """
        Ranks context dictionaries by relevance to reference text and returns top n most relevant contexts
        along with their original indices
        
        Args:
            contexts: List of dictionaries containing 'text' and metadata
            reference_text: Query string to compare texts against
            n: Number of contexts to return (default: 3)
            
        Returns:
            Tuple containing:
            - List of most relevant context dictionaries
            - List of original indices of the selected contexts
        """
        try:
            # Extract text content from contexts
            texts = [context['text'] for context in contexts]
            
            # Create vector store from texts
            db = FAISS.from_texts(texts, self.embeddings)
            
            # Get relevance scores
            results = db.similarity_search_with_score(reference_text, k=min(n, len(texts)))
            
            # Map results back to original context dictionaries
            ranked_contexts = []
            selected_indices = []
            for doc, score in results:
                # Find original context dictionary and its index by matching text content
                for i, context in enumerate(contexts):
                    if context['text'] == doc.page_content:
                        ranked_contexts.append(context)
                        selected_indices.append(i)
                        break
                
            return ranked_contexts, selected_indices

        except Exception as e:
            print(f"Error ranking contexts: {str(e)}")
            return [], []

class BotRelevance:
    '''
    The objective is to receive 1. a user prompt 2. dictionary with each entry containing a 'text' value 
    that contains all the relavant text openai chatbot accessed via langchain.
    it then will return both exact text and interpretted text that is most relavant to the prompt 
    '''
    pass

def pre_process_contexts(contexts):
    '''
    This function will take the list of dictionaries and return a list of strings
    each string is a concatenation of 'text' from each dictionary.
    context is a list of dictionaries
    with an example of a dictionary inside the list:
    {'text': 'administrator of the universe thy existence is an efflux, and that a limit of time is fixed for thee, which if thou dost not use for clearing away the clouds from thy mind, it will go and thou wilt go, and it will never return. Every moment think steadily as a Roman and a man to do what thou hast in hand with perfect and simple dignity, and feeling of affection, and freedom, and justice; and to give thyself relief from all other thoughts. And thou wilt give thyself relief, if thou doest every act of thy life as if it were the last, laying aside all carelessness and passionate aversion from the commands of reason, and all hypocrisy, and self-love, and discontent with the portion which has been given to thee. Thou seest how few the things are, the which if a man lays hold of, he is able to live a life which flows in quiet, and is like the existence of the gods; for the', 'fileName': 'Stoic Six Pack_ Meditations of Marcus Aurelius, Golden Sayings, Fragments and Discourses of Epictetus, Letters From A Stoic and The Enchiridion, 2014.pdf', 'page_number': 21}
    '''
    all_texts_str = ' '.join([context['text'] for context in contexts]) #string

    return all_texts_str

def chat_bot(contexts):
    all_texts_str = pre_process_contexts(contexts)
    ##
    print('processed contexts', all_texts_str, type())



    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(model_name=model_name)



    chain = load_qa_chain(llm, chain_type="stuff",verbose=True)

    # write your query and perform similarity search to generate an answer
    query = "What are the emotional benefits of owning a pet?"
    matching_docs = db.similarity_search(query)
    answer =  chain.run(input_documents=matching_docs, question=query)
    answer
    # import streamlit as st
    import os
    from dotenv import load_dotenv

    os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
    ## Langmith tracking
    os.environ["LANGCHAIN_TRACING_V2"]="true"
    os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

    ## Prompt Template

    prompt=ChatPromptTemplate.from_messages(
        [
            ("system","You are a helpful assistant. Please response to the user queries, \
             it will contain areference prompt and then a list of dictionaries full of text you are supposed to return the reference \
             "),
            ("user","Question:{question}")
        ]
    )

    ## streamlit framework

    # st.title('Langchain Demo With OPENAI API')
    # input_text=st.text_input("Search the topic u want")

    # openAI LLm 
    llm=ChatOpenAI(model="gpt-3.5-turbo")
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    print(chain)

        # if input_text:
        #     st.write(chain.invoke({'question':input_text}))
        


ranker = RelevanceRanker()
graph = GraphSearch()
# contexts = graph.get_context(concept="Geist", person="Hegel", context_type="details")
contexts = graph.get_context(concept="God", context_type="details")

print('ALL CONTEXTS retrieved', len(contexts))
# for i, ctx in enumerate(contexts):
#     print(f"\nContext {i}:")
#     print(f"Text: {ctx['text']}")
#     print("-" * 80)

# relevant_contexts, selected_indices = ranker.rank_by_relevance(
#     contexts=contexts,  # List of dicts from graph.get_context()
#     reference_text="No matter how much I pray in god it appears that there is no sign or response. does god evn love me?",
#     n=3  # Number of contexts to return
# )
# print(f"Selected context indices: {selected_indices}")
# print("Relevant contexts:")
# for i, context in zip(selected_indices, relevant_contexts):
#     print(f"\nIndex {i}:")
#     print(context)

chat_bot(contexts)