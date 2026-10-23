@echo off
rem Start Ollama server (CPU only, videocard disabled)
set CUDA_VISIBLE_DEVICES=-1
set OLLAMA_VULKAN=0
set GGML_VK_VISIBLE_DEVICES=-1
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
