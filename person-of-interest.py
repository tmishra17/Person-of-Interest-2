# import streamlit as st
from re import L
from turtle import onclick, title
from PIL import Image
import os
from dotenv import load_dotenv
# from backend.backend import search
from backend.PersonOfInterest import PersonOfInterest
from nicegui import ui
from functools import lru_cache

load_dotenv()  # reads .env file into os.environ
# st.title("Person of Interest")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
dark = ui.dark_mode()
dark.enable()

ui.switch('Dark Mode', value=True).bind_value(dark)

@lru_cache(maxsize=1)
def get_poi():
    poi = PersonOfInterest()
    poi.get_embeddings()
    return poi
def main():
    def do_search():
        if not query.value or not str(query.value).strip():
            ui.notify('Enter a search description.', type='warning')
            return
        results_container.clear()
        with results_container:
            ui.spinner(size='lg')
            ui.label('Loading model and embeddings (first time may take 10–15 min)...')
        # Force UI update; then block on get_poi()
        POI = get_poi()
        search_results = POI.semantic_search(
            query=query.value, 
            sim_score=float(sim_score.value),
            results=int(results.value)
        ) # semantic search on database
        for res in search_results:
            with ui.grid(columns=3).classes("w-full-w-4xl gap-4"):
                ui.image(res.payload["image_path"]).classes('rounded-xl max-w-xl')
                ui.markdown(f"**Score: {res.score:.2f}**")

    POI = get_poi()
    ui.markdown("**Person of Interest**").classes('text-2xl')

    # with ui.left_drawer().classes('p-4 border r-2').props('show-if-above breakpoint=md'):
    #     ui.label('Parameters').classes('text-h6')
    #     ui.label('Number of results')
    #     results = ui.slider(min=1, max=50, value=10).props('label-always')
    #     ui.label('Similarity threshold')
    #     sim_score = ui.slider(min=0, max=1, value=0.2, step=0.05).props('label-always')

    with ui.splitter(value=25).classes('w-full h-full') as splitter:
        with splitter.before:
            # Sidebar (left panel) – drag right edge to widen/narrow
            ui.label('Parameters').classes('text-h6')
            results = ui.slider(min=1, max=50, value=10).props('label-always')
            ui.label('Similarity threshold')
            sim_score = ui.slider(min=0, max=1, value=0.2, step=0.05).props('label-always')

        with splitter.after:
            # Main content (search bar + results)
            ui.markdown('**Person of Interest**')
            with ui.row().classes('items-center gap-2'):
                query = ui.input(
                label='Search',
            placeholder='Enter description (e.g. handsome man in a suit)'). \
            props('rounded outlined size=50 clearable').classes('max-w-xl')
                ui.button("Search", icon='search', on_click=do_search)
            results_container = ui.column().classes('w-full p-4')
            
    # with ui.row().classes("items-center gap-2"):
    #     query = ui.input(label='Search', placeholder='Enter description (e.g. handsome man in a suit)').props(
    #         'rounded outlined '
    #         'size=50 '
    #         'clearable'
    #     ).classes('max-w-xl')
    #     ui.button("Search", icon='search', on_click=do_search)
    #     results_container = ui.column().classes('w-full p-4') 
    #     print(query)
        # ui.run(host="localhost", port=5000)
        # st.sidebar.title("Parameters")
        # results = st.sidebar.slider(
        #         "Number of results",
        #         min_value=1,
        #         max_value=50,
        #         value=10,
        #         step=1
        #     )
        # sim_score = st.sidebar.slider(
        #         "Similarity Score",
        #         min_value=0.0,
        #         max_value=1.0,
        #         value=0.2,
        #         step=0.05
        # )

        # query = st.text_input("Enter Description here", placeholder="e.g. beautiful blonde girl with glasses, handsome guy in a suit")

        # if st.button("Search") and query:
        #     with st.spinner("Searching for similar images..."):
    print(query.value)


if __name__ in ('__main__', '__mp_main__'):
    ui.run(host="localhost", title="Person of Interest")
    main()
