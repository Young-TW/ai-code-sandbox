from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sandbox import CodeExecutor
from language_model import process_ai_response

app = FastAPI()
code_executor = CodeExecutor()

class CodeRequest(BaseModel):
    language: str = Field(..., description="程式語言 (python/cpp/rust/haskell/lean4)")
    code: str = Field(..., description="要執行的程式碼")
    input_data: Optional[str] = Field(None, description="程式的輸入資料（選擇性）")

class AIRequest(BaseModel):
    prompt: str = Field(..., description="使用者提示")
    context: Optional[str] = Field(None, description="對話上下文")

class CodeResponse(BaseModel):
    output: str = Field(..., description="程式執行輸出")
    error: Optional[str] = Field(None, description="錯誤訊息（如果有）")

class AIResponse(BaseModel):
    response: str = Field(..., description="AI 回應")
    code: Optional[str] = Field(None, description="生成的程式碼")
    language: Optional[str] = Field(None, description="程式語言")

@app.post("/execute/", response_model=CodeResponse)
async def execute_code(request: CodeRequest):
    """執行程式碼並返回結果"""
    try:
        if request.language not in code_executor.language_configs:
            raise HTTPException(
                status_code=400,
                detail=f"不支援的程式語言: {request.language}"
            )

        result = code_executor.execute_code(
            code=request.code,
            language=request.language,
            input_data=request.input_data
        )

        return CodeResponse(
            output=result['output'],
            error=result['error'] if result['error'] else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"執行錯誤: {str(e)}"
        )

@app.post("/ai/chat/", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """與 AI 互動並獲取回應"""
    try:
        response = await process_ai_response(request.prompt, request.context)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 處理錯誤: {str(e)}"
        )

@app.get("/supported-languages/")
async def get_supported_languages():
    """獲取支援的程式語言列表"""
    return {"languages": list(code_executor.language_configs.keys())}

@app.get("/health/")
async def health_check():
    """基本的健康檢查端點"""
    return {"status": "healthy"} 