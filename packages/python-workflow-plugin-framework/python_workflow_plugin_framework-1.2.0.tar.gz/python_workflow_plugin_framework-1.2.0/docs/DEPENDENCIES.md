# 插件依赖版本说明

## Python 插件依赖

### LangChain Ollama Python 插件

**测试通过的版本组合（LangChain v1.0）：**

```txt
grpcio==1.68.1
grpcio-tools==1.68.1
protobuf==5.29.2
langchain==1.0.0
langchain-core==1.0.0
langchain-ollama==1.0.0
requests==2.32.3
```

**版本说明：**

1. **LangChain 1.0.0** 🎉
   - **重大里程碑** - 首个稳定的 v1.0 版本
   - **API 稳定** - 向后兼容保证
   - **生产就绪** - 经过充分测试
   - **改进的 LCEL** - 更强大的链式调用
   - **更好的类型提示** - 完整的类型支持
   - **性能优化** - 更快的执行速度

2. **langchain-core 1.0.0**
   - 核心 Runnable 接口
   - 统一的抽象层
   - 改进的流式支持
   - 更好的错误处理

3. **langchain-ollama 1.0.0**
   - 官方 Ollama 集成包 v1.0
   - 与 LangChain v1.0 完全兼容
   - 替代了旧的 `langchain-community.llms.Ollama`
   - 更好的性能和稳定性
   - 支持最新的 Ollama 特性
   - 完整的类型提示

**已知兼容性问题：**

❌ **不兼容的版本组合：**

```txt
# 旧版本组合（不推荐）
langchain==0.1.0
langchain-core==0.1.23
langchain-community==0.0.10
ollama==0.1.6
```

**问题：**
- `langchain-core 0.1.x` 与 `langgraph` 等新包不兼容
- `ollama 0.1.x` 缺少新特性
- 缺少 `langchain-ollama` 官方集成
- API 不稳定，可能有破坏性变更

```txt
# 0.3.x 版本（已过时）
langchain==0.3.x
langchain-core==0.3.x
langchain-ollama==0.2.x
```

**问题：**
- 已被 v1.0 取代
- 缺少 v1.0 的新特性和优化
- 建议升级到 v1.0

## Node.js 插件依赖

### LangChain Ollama Node.js 插件

**测试通过的版本组合：**

```json
{
  "@grpc/grpc-js": "^1.9.14",
  "@grpc/proto-loader": "^0.7.10",
  "@langchain/community": "^0.0.20",
  "@langchain/core": "^0.1.10",
  "langchain": "^0.1.0"
}
```

**版本说明：**

1. **@langchain/community 0.0.20+**
   - 包含 Ollama 集成
   - 模块化设计
   - 更小的包体积

2. **@grpc/grpc-js 1.9.x**
   - 纯 JavaScript 实现
   - 无需编译
   - 跨平台兼容

**Node.js 版本要求：**
- Node.js >= 18.0.0
- 推荐使用 LTS 版本

## 依赖安装指南

### Python 插件

#### 方法 1：使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 方法 2：使用 conda

```bash
# 创建 conda 环境
conda create -n langchain-plugin python=3.11

# 激活环境
conda activate langchain-plugin

# 安装依赖
pip install -r requirements.txt
```

#### 方法 3：使用 pipenv

```bash
# 安装 pipenv
pip install pipenv

# 安装依赖
pipenv install -r requirements.txt

# 激活环境
pipenv shell
```

### Node.js 插件

#### 方法 1：使用 npm

```bash
npm install
```

#### 方法 2：使用 yarn

```bash
yarn install
```

#### 方法 3：使用 pnpm

```bash
pnpm install
```

## 依赖冲突解决

### Python 依赖冲突

#### 问题 1：langchain-core 版本冲突

**错误信息：**
```
langgraph-prebuilt requires langchain-core>=1.0.0, but you have langchain-core 0.1.23
```

**解决方案：**
```bash
# 升级到兼容版本
pip install --upgrade langchain==0.3.0 langchain-core==0.3.0
```

#### 问题 2：ollama 版本冲突

**错误信息：**
```
langchain-ollama requires ollama<1.0.0,>=0.6.0, but you have ollama 0.1.6
```

**解决方案：**
```bash
# 升级 ollama
pip install --upgrade ollama==0.3.0
```

#### 问题 3：numpy 版本冲突

**错误信息：**
```
opencv-python requires numpy<2.3.0,>=2, but you have numpy 1.26.4
```

**解决方案：**
```bash
# 升级 numpy（如果需要 opencv）
pip install --upgrade numpy>=2.0.0

# 或者卸载 opencv（如果不需要）
pip uninstall opencv-python
```

### 完全重装依赖

如果遇到复杂的依赖冲突，建议完全重装：

```bash
# 1. 删除虚拟环境
rm -rf venv

# 2. 创建新的虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 升级 pip
pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements.txt
```

## 依赖版本锁定

### Python - requirements-lock.txt

为了确保可重现的构建，可以生成锁定文件：

```bash
# 生成锁定文件
pip freeze > requirements-lock.txt

# 使用锁定文件安装
pip install -r requirements-lock.txt
```

### Node.js - package-lock.json

Node.js 会自动生成 `package-lock.json`：

```bash
# 使用锁定文件安装
npm ci  # 比 npm install 更严格
```

## 最小依赖版本

如果需要最小化依赖，可以只安装核心包：

### Python 最小依赖

```txt
grpcio>=1.60.0
grpcio-tools>=1.60.0
protobuf>=4.25.0
langchain-ollama>=0.2.0
```

### Node.js 最小依赖

```json
{
  "@grpc/grpc-js": "^1.9.0",
  "@grpc/proto-loader": "^0.7.0",
  "@langchain/community": "^0.0.20"
}
```

## 测试依赖安装

### Python

```bash
# 测试导入
python -c "from langchain_ollama import OllamaLLM; print('✅ OK')"

# 测试 gRPC
python -c "import grpc; print('✅ OK')"
```

### Node.js

```bash
# 测试导入
node -e "require('@langchain/community'); console.log('✅ OK')"

# 测试 gRPC
node -e "require('@grpc/grpc-js'); console.log('✅ OK')"
```

## 更新依赖

### 检查过期的包

**Python:**
```bash
pip list --outdated
```

**Node.js:**
```bash
npm outdated
```

### 安全更新

**Python:**
```bash
# 检查安全漏洞
pip-audit

# 或使用 safety
pip install safety
safety check
```

**Node.js:**
```bash
# 检查安全漏洞
npm audit

# 自动修复
npm audit fix
```

## 生产环境建议

1. **使用虚拟环境**
   - Python: venv 或 conda
   - Node.js: 使用 package-lock.json

2. **锁定版本**
   - 使用精确版本号
   - 定期更新和测试

3. **安全扫描**
   - 定期运行安全审计
   - 及时更新有漏洞的包

4. **文档化**
   - 记录依赖变更
   - 说明版本选择原因

## 常见问题

### Q: 为什么不使用最新版本？

A: 我们使用经过测试的稳定版本组合，确保兼容性。

### Q: 如何升级到最新版本？

A: 
```bash
# Python
pip install --upgrade -r requirements.txt

# Node.js
npm update
```

### Q: 依赖冲突怎么办？

A: 参考上面的"依赖冲突解决"部分，或创建新的虚拟环境。

### Q: 可以使用其他版本吗？

A: 可以，但需要自行测试兼容性。建议使用推荐的版本组合。

## 相关资源

- [LangChain 文档](https://python.langchain.com/)
- [LangChain.js 文档](https://js.langchain.com/)
- [Ollama 文档](https://ollama.com/)
- [gRPC Python 文档](https://grpc.io/docs/languages/python/)
- [gRPC Node.js 文档](https://grpc.io/docs/languages/node/)
