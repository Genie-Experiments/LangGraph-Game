from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from APIs.number_game.ng_api import router as number_game_router
from APIs.word_game.wg_api import router as word_game_router
from langgraph_core.graph.graph import app as langgraph_app

app = FastAPI(title="LangGraph Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from different game APIs
app.include_router(number_game_router)
app.include_router(word_game_router)


@app.get("/")
def welcome():
    return {"message": "Welcome to the LangGraph Game API!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)