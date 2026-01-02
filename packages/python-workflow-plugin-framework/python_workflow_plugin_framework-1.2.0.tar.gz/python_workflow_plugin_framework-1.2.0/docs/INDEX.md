# Python Workflow Plugin Framework - 文件索引

## 📚 文档

| 文件 | 描述 | 适合人群 |
|------|------|----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | 🌟 **从这里开始** - 5 分钟入门教程 | 新手 |
| [README.md](README.md) | 完整的框架文档和 API 参考 | 所有开发者 |
| [QUICKSTART.md](QUICKSTART.md) | 快速参考和代码片段 | 有经验的开发者 |
| [GLOG_USAGE.md](GLOG_USAGE.md) | glog-python 日志使用指南 | 所有开发者 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计和实现细节 | 高级开发者 |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | 从原始代码迁移到框架 | 现有插件开发者 |
| [SUMMARY.md](SUMMARY.md) | 项目总结和统计 | 管理者 |
| [INDEX.md](INDEX.md) | 本文件 - 文件索引 | 所有人 |

## 🔧 核心文件

| 文件 | 描述 | 用途 |
|------|------|------|
| [base_plugin.py](base_plugin.py) | 框架核心 - 基础插件类 | 所有插件的基类 |
| [__init__.py](__init__.py) | Python 包初始化 | 导入框架 |
| [requirements.txt](requirements.txt) | 框架依赖 | 安装依赖 |

## 📝 示例插件

| 文件 | 描述 | 复杂度 | 展示特性 |
|------|------|--------|----------|
| [example_plugin.py](example_plugin.py) | 简单文本处理插件 | ⭐ 简单 | 基础用法 |
| [http_api_plugin.py](http_api_plugin.py) | HTTP API 调用插件 | ⭐⭐ 中等 | 外部 API、凭证、健康检查 |
| [langchain_ollama_plugin.py](langchain_ollama_plugin.py) | LangChain + Ollama 集成 | ⭐⭐⭐ 复杂 | 流式输出、LLM 集成 |

## 🧪 测试

| 文件 | 描述 | 用途 |
|------|------|------|
| [test_framework.py](test_framework.py) | 框架测试套件 | 验证框架功能 |

## 🚀 快速导航

### 我想...

#### 🌟 第一次使用框架
→ 阅读 [GETTING_STARTED.md](GETTING_STARTED.md) - **从这里开始！**

#### 创建第一个插件
→ 阅读 [QUICKSTART.md](QUICKSTART.md)

#### 了解框架 API
→ 阅读 [README.md](README.md) 的 "核心概念" 部分

#### 查看示例代码
→ 查看 [example_plugin.py](example_plugin.py)

#### 创建 HTTP API 插件
→ 参考 [http_api_plugin.py](http_api_plugin.py)

#### 集成 LLM
→ 参考 [langchain_ollama_plugin.py](langchain_ollama_plugin.py)

#### 迁移现有插件
→ 阅读 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

#### 理解框架设计
→ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)

#### 查看项目统计
→ 阅读 [SUMMARY.md](SUMMARY.md)

#### 测试框架
→ 运行 `python test_framework.py`

## 📦 安装

```bash
# 从 PyPI 安装
pip install python-workflow-plugin-framework

# 或从源码安装
cd grpc-base-plugin-python
pip install -r requirements.txt
```

## 🎯 推荐学习流程

```
1. 阅读 GETTING_STARTED.md (5 分钟)
   ↓
2. 运行 example_plugin.py
   ↓
3. 创建自己的插件
   ↓
4. 阅读 QUICKSTART.md 学习更多技巧
   ↓
5. 参考 README.md 了解高级特性
   ↓
6. 查看 ARCHITECTURE.md 理解内部机制
```

## 🔍 代码结构

```
grpc-base-plugin-python/
├── 📄 文档
│   ├── GETTING_STARTED.md  # 🌟 入门教程
│   ├── README.md           # 主文档
│   ├── QUICKSTART.md       # 快速参考
│   ├── ARCHITECTURE.md     # 架构设计
│   ├── MIGRATION_GUIDE.md  # 迁移指南
│   ├── SUMMARY.md          # 项目总结
│   └── INDEX.md            # 本文件
│
├── 🔧 核心
│   ├── base_plugin.py      # 框架核心
│   ├── __init__.py         # 包初始化
│   └── requirements.txt    # 依赖
│
├── 📝 示例
│   ├── example_plugin.py           # 简单示例
│   ├── http_api_plugin.py          # HTTP API
│   └── langchain_ollama_plugin.py  # LLM 集成
│
└── 🧪 测试
    ├── test_framework.py   # 测试套件
    └── Makefile            # 便捷命令
```

## 💡 学习路径

### 🌱 初学者（第一次使用）
1. **GETTING_STARTED.md** - 5 分钟入门教程
2. **example_plugin.py** - 运行第一个插件
3. **创建自己的插件** - 动手实践
4. **README.md** - 学习更多特性

### 🌿 中级开发者（有 Python 经验）
1. **QUICKSTART.md** - 快速浏览
2. **http_api_plugin.py** - 学习最佳实践
3. **README.md** - 掌握高级特性
4. **创建复杂插件** - 实际应用

### 🌳 高级开发者（深入理解）
1. **ARCHITECTURE.md** - 理解设计
2. **base_plugin.py** - 阅读源码
3. **MIGRATION_GUIDE.md** - 迁移现有代码
4. **扩展框架功能** - 贡献代码

### 🔄 现有插件开发者（迁移）
1. **MIGRATION_GUIDE.md** - 迁移步骤
2. **langchain_ollama_plugin.py** - 迁移示例
3. **测试迁移后的插件**
4. **部署新版本**

## 🎓 示例对比

| 特性 | example_plugin | http_api_plugin | langchain_ollama_plugin |
|------|----------------|-----------------|-------------------------|
| 参数数量 | 3 | 6 | 9 |
| 健康检查 | 默认 | 自定义 | 自定义 |
| 凭证验证 | 默认 | 自定义 | 默认 |
| 流式输出 | ❌ | ❌ | ✅ |
| 外部依赖 | ❌ | requests | langchain, ollama |
| 错误处理 | 基础 | 完整 | 完整 |
| 代码行数 | ~60 | ~150 | ~180 |

## 📊 功能矩阵

| 功能 | base_plugin | 需要实现 | 可选覆盖 |
|------|-------------|----------|----------|
| gRPC 服务 | ✅ | - | - |
| 参数解析 | ✅ | - | - |
| 日志管理 | ✅ | - | ✅ |
| 错误处理 | ✅ | - | - |
| 元数据 | - | ✅ | - |
| 执行逻辑 | - | ✅ | - |
| 健康检查 | ✅ | - | ✅ |
| 凭证验证 | ✅ | - | ✅ |
| 初始化钩子 | ✅ | - | ✅ |

## 🔗 相关资源

- gRPC Python: https://grpc.io/docs/languages/python/
- Protobuf: https://developers.google.com/protocol-buffers
- LangChain: https://python.langchain.com/

## 📝 版本历史

- v1.0.0 (2024) - 初始版本
  - 基础框架
  - 三个示例插件
  - 完整文档

## 🤝 贡献

欢迎贡献！可以：
- 添加新的示例插件
- 改进文档
- 报告 Bug
- 提出新功能

## 📮 反馈

如有问题或建议，请：
1. 查看文档
2. 查看示例代码
3. 运行测试
4. 提交 Issue
