# Colors for output
YELLOW=\033[1;33m
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

# Package information
PACKAGE_NAME=python-plugin-framework

.PHONY: help install test run-example run-http run-langchain run-glog build upload-test publish clean

help:
	@echo "Python Plugin Framework - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run framework tests"
	@echo "  make run-example      - Run example plugin (port 50052)"
	@echo "  make run-http         - Run HTTP API plugin (port 50053)"
	@echo "  make run-langchain    - Run LangChain Ollama plugin (port 50054)"
	@echo "  make run-glog         - Run glog example plugin (port 50055)"
	@echo "  make run-custom-plugins - Run all custom plugins in separate terminals"
	@echo "  make run-langchain-memory - Run LangChain Memory plugin (port 50055)"
	@echo "  make run-mobile-adb   - Run Mobile ADB plugin (port 50056)"
	@echo "  make run-desktop-screenshot - Run Desktop Screenshot plugin (port 50057)"
	@echo "  make run-playwright   - Run Playwright Browser plugin (port 50058)"
	@echo "  make build            - Build package for PyPI"
	@echo "  make upload-test      - Upload to test PyPI (test.pypi.org)"
	@echo "  make publish          - Publish to PyPI (pypi.org) with confirmation"
	@echo "  make clean            - Clean Python cache files"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

test:
	@echo "🧪 Running framework tests..."
	python test_framework.py

run-example:
	@echo "🚀 Starting example plugin on port 50052..."
	python examples/example_plugin.py 50052

run-http:
	@echo "🚀 Starting HTTP API plugin on port 50053..."
	python examples/http_api_plugin.py 50053

run-langchain:
	@echo "🚀 Starting LangChain Ollama plugin on port 50054..."
	python examples/langchain_ollama_plugin.py 50054


run-custom-plugins:
	@echo "🚀 Starting all custom plugins..."
	@echo "Note: This will open multiple terminal windows/tabs"
	@echo "Press Enter to continue or Ctrl+C to cancel..."
	@read
	@echo "Starting LangChain Memory plugin..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD)/my_plugins/langchain_memory && make run"'
	@sleep 1
	@echo "Starting Mobile ADB plugin..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD)/my_plugins/mobile_adb && make run"'
	@sleep 1
	@echo "Starting Desktop Screenshot plugin..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD)/my_plugins/desktop_screenshot && make run"'
	@sleep 1
	@echo "Starting Playwright Browser plugin..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD)/my_plugins/playwright_browser && make run"'
	@echo "✅ All custom plugins started in separate terminal windows"

run-langchain-memory:
	@echo "🚀 Starting LangChain Memory plugin on port 50055..."
	cd my_plugins/langchain_memory && python langchain_memory_plugin.py 50055

run-mobile-adb:
	@echo "🚀 Starting Mobile ADB plugin on port 50056..."
	cd my_plugins/mobile_adb && python mobile_adb_plugin.py 50056

run-desktop-screenshot:
	@echo "🚀 Starting Desktop Screenshot plugin on port 50057..."
	cd my_plugins/desktop_screenshot && python desktop_screenshot_plugin.py 50057

run-playwright:
	@echo "🚀 Starting Playwright Browser plugin on port 50058..."
	cd my_plugins/playwright_browser && python playwright_browser_plugin.py 50058

build:
	@echo "📦 Building package for PyPI..."
	python setup.py sdist bdist_wheel
	@echo "✅ Package built successfully!"
	@echo "📁 Output in 'dist/' directory"

upload-test:
	@echo "🚀 Uploading to test PyPI (test.pypi.org)..."
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@echo "✅ Upload to test PyPI completed!"

publish: build
	@echo "$(YELLOW)警告: 即将发布到正式 PyPI$(NC)"
	@read -p "确认继续? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
	   echo "$(BLUE)上传到 PyPI...$(NC)"; \
	   twine upload dist/*; \
	   echo "$(GREEN)✓ 上传到 PyPI 成功$(NC)"; \
	   echo ""; \
	   echo "安装命令:"; \
	   echo "  pip install $(PACKAGE_NAME)"; \
	else \
	   echo "$(RED)✗ 取消发布$(NC)"; \
	fi

clean:
	@echo "🧹 Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleaned"
