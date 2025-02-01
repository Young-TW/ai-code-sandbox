from typing import Optional, Dict, Literal
from pydantic import BaseModel
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

class AIResponse(BaseModel):
    response: str
    code: Optional[str] = None
    language: Optional[str] = None

class AIConfig:
    """AI 模型配置"""
    def __init__(self):
        # 從環境變數讀取配置
        self.provider: Literal["ollama", "lmstudio"] = os.getenv("AI_PROVIDER", "ollama")
        self.model_name: str = os.getenv("AI_MODEL_NAME", "codellama")
        
        # API 端點
        self.ollama_url: str = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        self.lmstudio_url: str = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1/chat/completions")

class AIClient:
    """AI 客戶端"""
    def __init__(self):
        self.config = AIConfig()

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """生成 AI 回應"""
        if self.config.provider == "ollama":
            return await self._ollama_generate(prompt, context)
        else:
            return await self._lmstudio_generate(prompt, context)

    async def _ollama_generate(self, prompt: str, context: Optional[str] = None) -> str:
        """使用 Ollama API 生成回應"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "context": context if context else [],
                "stream": False
            }
            
            async with session.post(self.config.ollama_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API 錯誤: {await response.text()}")
                
                result = await response.json()
                return result.get("response", "")

    async def _lmstudio_generate(self, prompt: str, context: Optional[str] = None) -> str:
        """使用 LM Studio API 生成回應"""
        async with aiohttp.ClientSession() as session:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "messages": messages,
                "model": self.config.model_name,
                "temperature": 0.7,
                "stream": False
            }
            
            async with session.post(self.config.lmstudio_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"LM Studio API 錯誤: {await response.text()}")
                
                result = await response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")

async def process_ai_response(prompt: str, context: Optional[str] = None) -> Dict:
    """
    處理 AI 回應的核心邏輯
    
    Args:
        prompt: 使用者提示
        context: 對話上下文（選擇性）
    
    Returns:
        包含 AI 回應的字典
    """
    try:
        ai_client = AIClient()
        response_text = await ai_client.generate_response(prompt, context)
        
        # 解析回應中的程式碼
        code = None
        language = None
        
        # 尋找程式碼區塊
        if "```" in response_text:
            code_blocks = response_text.split("```")
            for i in range(1, len(code_blocks), 2):
                if i < len(code_blocks):
                    block = code_blocks[i].strip()
                    if block:
                        # 提取語言（如果有指定）
                        first_line = block.split('\n')[0].strip()
                        if first_line in ["python", "cpp", "rust", "haskell", "lean4"]:
                            language = first_line
                            code = '\n'.join(block.split('\n')[1:])
                        else:
                            code = block
                            # 嘗試推測語言
                            if "print" in block:
                                language = "python"
                            elif "std::" in block:
                                language = "cpp"
                            elif "fn main" in block:
                                language = "rust"
                        break

        return {
            "response": response_text,
            "code": code,
            "language": language
        }
        
    except Exception as e:
        raise Exception(f"AI 處理錯誤: {str(e)}")

# 可以添加更多 AI 相關的功能
# 例如：記憶對話歷史、程式碼生成、程式碼解釋等 