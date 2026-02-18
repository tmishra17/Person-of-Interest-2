
import os
from dotenv import load_dotenv
from backend.PersonOfInterest import PersonOfInterest
from nicegui import ui
from functools import lru_cache

load_dotenv()  # reads .env file into os.environ

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"

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
        poi = get_poi()
        search_results = poi.semantic_search(
            query=query.value, 
            sim_score=float(sim_score.value),
            results=int(results.value)
        ) # semantic search on database
        for res in search_results:
            with ui.grid(columns=3).classes("w-full-w-4xl gap-4"):
                ui.image(res.payload["image_path"]).classes('rounded-xl max-w-xl')
                ui.markdown(f"**Score: {res.score:.2f}**")

    with ui.splitter(value=25).classes('w-full h-full') as splitter:
        with splitter.before:
            # Sidebar (left panel) – drag right edge to widen/narrow
            with ui.column().classes("w-full p-4 pr-6"):
                ui.label('Parameters').classes('text-h6')
                results = ui.slider(min=1, max=50, value=10).props('label-always')
                ui.label('Similarity threshold').classes('text-h6')
                sim_score = ui.slider(min=0, max=1, value=0.2, step=0.05).props('label-always')

        with splitter.after:
            # Main content (search bar + results)
            results_container = ui.column().classes('w-full p-4 pr-6 m-10')
            with results_container:
                ui.markdown('**Person of Interest**').classes('text-6xl items-center md-10')
                with ui.row().classes('items-center'):
                    query = ui.input(
                    label='Search',
                placeholder='Enter description (e.g. handsome man in a suit)'). \
                props('rounded outlined size=80 clearable').classes('max-w-xl ')
                    ui.button("Search", icon='search', on_click=do_search)
                
    print(query.value)
@ui.page('/')
def index():
    dark = ui.dark_mode()
    dark.enable()
    ui.switch('Dark Mode', value=True).bind_value(dark)

    main()
if __name__ in ('__main__', '__mp_main__'):
    ui.run(host="localhost", title="Person of Interest")
