from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 定義 JSON 主體資料模型
class CodeRequest(BaseModel):
    language: str
    prompt: str

@app.post("/execute/")
async def execute_code(request: CodeRequest):
    # 從 JSON 主體提取參數
    language = request.language
    prompt = request.prompt

    # 模擬返回執行結果
    return {"message": "Code received", "language": language, "prompt": prompt}
