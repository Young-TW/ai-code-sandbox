from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sandbox import CodeExecutor

app = FastAPI()
code_executor = CodeExecutor()

# 定義 JSON 主體資料模型
class CodeRequest(BaseModel):
    language: str = Field(..., description="程式語言 (python/cpp/rust/haskell/lean4)")
    code: str = Field(..., description="要執行的程式碼")
    input_data: Optional[str] = Field(None, description="程式的輸入資料（選擇性）")

class CodeResponse(BaseModel):
    output: str = Field(..., description="程式執行輸出")
    error: Optional[str] = Field(None, description="錯誤訊息（如果有）")

@app.post("/execute/", response_model=CodeResponse)
async def execute_code(request: CodeRequest):
    """
    執行程式碼並返回結果
    """
    try:
        # 檢查是否支援該程式語言
        if request.language not in code_executor.language_configs:
            raise HTTPException(
                status_code=400,
                detail=f"不支援的程式語言: {request.language}"
            )

        # 執行程式碼
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

@app.get("/supported-languages/")
async def get_supported_languages():
    """
    獲取支援的程式語言列表
    """
    return {"languages": list(code_executor.language_configs.keys())}

# 基本的健康檢查端點
@app.get("/health/")
async def health_check():
    return {"status": "healthy"}
