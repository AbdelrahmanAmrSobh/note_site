from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.add import router as add_router
from controllers.auth import router as auth_router
from controllers.create import router as create_router
from controllers.delete import router as delete_router
from controllers.remove import router as remove_router
from controllers.update import router as update_router
from controllers.view import router as view_router

app = FastAPI()

# Define allowed origins (you can specify the frontend URL here)
origins = [
    "http://localhost:5173",  # your frontend's URL
]

# Add CORS middleware with configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(add_router)
app.include_router(auth_router)
app.include_router(create_router)
app.include_router(delete_router)
app.include_router(remove_router)
app.include_router(update_router)
app.include_router(view_router)


@app.get("/")
def root():
    return {"Server status": "Running"}
