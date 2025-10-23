@echo off
echo =====================================================
echo 启动 EduAgent 后端服务器
echo =====================================================
echo.

echo [1/3] 清除 Python 缓存...
python clear_cache.py
echo.

echo [2/3] 验证配置...
python verify_integration.py
echo.

echo [3/3] 启动服务器...
echo 服务器将在 http://localhost:8000 运行
echo 按 Ctrl+C 停止服务器
echo.
python main.py
