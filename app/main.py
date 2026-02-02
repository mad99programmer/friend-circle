from fastapi import FastAPI
from app.router import vents
from app.router import comments


app = FastAPI()



@app.get("/")
def health():
    return {"message":"firend-circle health check"}

app.include_router(vents.router)
app.include_router(comments.router)
