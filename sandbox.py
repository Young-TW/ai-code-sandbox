import subprocess
import tempfile
import os
from typing import Dict, Optional
import resource  # 僅支援 Unix 系統

class CodeExecutor:
    """程式碼執行器，支援多種程式語言"""
    
    def __init__(self):
        self.language_configs: Dict[str, dict] = {
            'python': {
                'file_extension': '.py',
                'command': 'python'
            },
            'cpp': {
                'file_extension': '.cpp',
                'compile_command': 'g++',
                'run_command': './{}'
            },
            'rust': {
                'file_extension': '.rs',
                'compile_command': 'rustc',
                'run_command': './{}'
            },
            'haskell': {
                'file_extension': '.hs',
                'compile_command': 'ghc',
                'run_command': './{}'
            },
            'lean4': {
                'file_extension': '.lean',
                'compile_command': 'lake build',
                'run_command': './build/bin/{}'
            }
        }

    def set_memory_limit(self, size_mb: int):
        """設定記憶體限制（僅支援 Unix 系統）"""
        resource.setrlimit(
            resource.RLIMIT_AS,  # 虛擬記憶體限制
            (size_mb * 1024 * 1024, resource.RLIM_INFINITY)
        )

    def execute_code(self, code: str, language: str, input_data: Optional[str] = None) -> Dict[str, str]:
        """
        執行指定語言的程式碼
        
        Args:
            code: 要執行的程式碼
            language: 程式語言（python/cpp/rust/haskell/lean4）
            input_data: 程式的輸入資料（選擇性）
            
        Returns:
            包含執行結果的字典：
            {
                'output': 程式輸出,
                'error': 錯誤訊息（如果有的話）
            }
        """
        if language not in self.language_configs:
            return {'output': '', 'error': f'不支援的程式語言: {language}'}

        config = self.language_configs[language]
        
        # 建立暫存檔案
        with tempfile.NamedTemporaryFile(
            suffix=config['file_extension'],
            mode='w',
            delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            if language == 'python':
                # 直接執行 Python
                process = subprocess.run(
                    [config['command'], temp_file_path],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=resource_limits['timeout'],
                    preexec_fn=lambda: self.set_memory_limit(resource_limits['memory_mb'])
                )
                return {
                    'output': process.stdout,
                    'error': process.stderr
                }
            
            # 需要編譯的語言
            executable = temp_file_path.replace(config['file_extension'], '')
            
            # 編譯程式碼
            if language == 'lean4':
                # Lean4 需要特殊處理，因為它使用 lake 建構系統
                compile_process = subprocess.run(
                    config['compile_command'].split(),
                    cwd=os.path.dirname(temp_file_path),
                    capture_output=True,
                    text=True
                )
            else:
                compile_process = subprocess.run(
                    [config['compile_command'], temp_file_path, '-o', executable],
                    capture_output=True,
                    text=True
                )
            
            if compile_process.returncode != 0:
                return {'output': '', 'error': compile_process.stderr}
            
            # 執行編譯後的程式
            run_command = config['run_command'].format(
                os.path.basename(executable)
            )
            process = subprocess.run(
                run_command.split(),
                input=input_data,
                capture_output=True,
                text=True
            )

            return {
                'output': process.stdout,
                'error': process.stderr
            }

        finally:
            # 清理暫存檔案
            os.unlink(temp_file_path)
            if language != 'python':
                executable_path = temp_file_path.replace(config['file_extension'], '')
                if os.path.exists(executable_path):
                    os.unlink(executable_path)

# 使用範例
if __name__ == '__main__':
    executor = CodeExecutor()
    
    # Python 程式碼範例
    python_code = '''
print("Hello from Python!")
'''
    result = executor.execute_code(python_code, 'python')
    print("Python 執行結果:", result)

    # Rust 程式碼範例
    rust_code = '''
fn main() {
    println!("Hello from Rust!");
}
'''
    result = executor.execute_code(rust_code, 'rust')
    print("Rust 執行結果:", result)

    # Haskell 程式碼範例
    haskell_code = '''
main :: IO ()
main = putStrLn "Hello from Haskell!"
'''
    result = executor.execute_code(haskell_code, 'haskell')
    print("Haskell 執行結果:", result)

    # Lean4 程式碼範例
    lean4_code = '''
def main : IO Unit := do
  IO.println "Hello from Lean4!"
'''
    result = executor.execute_code(lean4_code, 'lean4')
    print("Lean4 執行結果:", result)
