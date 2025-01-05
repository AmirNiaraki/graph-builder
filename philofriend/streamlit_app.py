'''
python3  -m streamlit run streamlit_app.py
nohup python3  -m streamlit run streamlit_app.py &
'''

import streamlit as st
from wisdom_engine import WisdomEngine
import random


st.set_page_config(page_title="Philofriend", page_icon=":speech_balloon:")
st.title("Ask a Stoic")
st.write("I am Seneca, reflect on your day and tpye in your dilemma")
# # Add a button to initiate an instance of WisdomEngine
# if st.sidebar.button("Initialize WisdomEngine"):
#     # Create an instance of WisdomEngine
#     engine = WisdomEngine()
#     st.session_state['wisdom_engine'] = engine
#     st.write("WisdomEngine has been initialized!")

reflection_summary=st.text_input("ask me anything")

if reflection_summary:
        # Find relevant discoveries
    engine = WisdomEngine() 
    discoveries = engine.find_relevant_discoveries(number_of_concepts=3, input_summary=reflection_summary)
    # logger.info(f"Most relevant discoveries: {discoveries}")
    st.write("Here are some Stoic discoveries based on your reflection: ", str(discoveries))
    # Find relevant story
    random_index = random.randint(0, len(discoveries) - 1)
    story, book_name, page_number = engine.find_relevant_story(discovery=discoveries[random_index], input_summary=reflection_summary)
    
    st.write(story+"... \n")
    st.write("Read more in: "+book_name+" \n")
    st.write("page: ")
    st.write(page_number)
    