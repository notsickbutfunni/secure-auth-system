from fastapi import FastAPI

app = FastAPI(title="Secure Auth System (Base App)")

@app.get("/")
def root():
    return {"message": "FastAPI server running!"}

@app.get("/auth/test")
def test_auth():
    return {"status": "auth endpoint works"}
