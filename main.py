# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from routes.auth import router as auth_router
# from db.init_db import init_db

# app = FastAPI(title="Workflow.AI Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register routes
# app.include_router(auth_router)


# @app.on_event("startup")
# def startup():
#     init_db()


# @app.get("/")
# def root():
#     return {"status": "Backend running"}
# from dotenv import load_dotenv
# load_dotenv()

from dotenv import load_dotenv


from fastapi import FastAPI
from routes.auth import router as auth_router
load_dotenv()
app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "Backend running"}