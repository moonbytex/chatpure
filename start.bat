@echo off
REM ChatPure 一键启动脚本 (Windows)
REM 使用方法：双击 start.bat 或在命令行运行 start.bat

echo 🚀 启动 ChatPure...
echo.

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend

REM 检查 Python 是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION%

REM 检查后端目录
if not exist "%BACKEND_DIR%" (
    echo ❌ 错误：后端目录不存在：%BACKEND_DIR%
    pause
    exit /b 1
)

REM 检查前端目录
if not exist "%SCRIPT_DIR%frontend" (
    echo ❌ 错误：前端目录不存在：%SCRIPT_DIR%frontend
    pause
    exit /b 1
)

echo ✅ 前端目录：%SCRIPT_DIR%frontend
echo ✅ 后端目录：%BACKEND_DIR%
echo.

REM 提示配置
echo 📝 配置说明：
echo    - API Key: 设置环境变量 LLM_API_KEY
echo    - 端口：默认 8000，可设置 PORT 环境变量
echo.

REM 启动服务
echo 🌐 服务地址：http://localhost:8000
echo 💡 提示：按 Ctrl+C 停止服务
echo.

cd /d "%BACKEND_DIR%"
python server.py

pause
