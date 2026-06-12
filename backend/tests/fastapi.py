from FastAPI import FastAPI
import os
import json
import requests

app = FastAPI()

@app.get("/" )
async def root():
    return {"message": "Welcome to the FastApi Backend"}

@app.post("/service/{user_id}/send_message")
async def send_message(user_id: str):
    return {"message": "Message sent to user", "user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

user_json = {
    "user_id": "1",
    "message": "Hello"
}

response = requests.post("http://localhost:8000/service/1/send_message", json=user_json)
print(response.json())