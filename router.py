from fastapi import FastAPI
from controller.get_link_data import process_metadata
from controller.generate_quiz import generate_quiz_desktop

def init_routes (app: FastAPI):
    app.router.post("/processdata", operation_id="get_meta")(process_metadata)
    app.router.post("/generatequiz", operation_id="makequiz")(generate_quiz_desktop)