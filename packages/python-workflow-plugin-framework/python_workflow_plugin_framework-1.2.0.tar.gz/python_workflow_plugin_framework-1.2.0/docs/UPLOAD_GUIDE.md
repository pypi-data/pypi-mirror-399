# PyPI 包上传指南

本指南将帮助你将 Python Workflow Plugin Framework 上传到 PyPI 官方源。

## 项目链接

- **GitHub**: [https://github.com/mytoolzone/python-workflow-plugin-framework](https://github.com/mytoolzone/python-workflow-plugin-framework)
- **PyPI**: [https://pypi.org/project/python-workflow-plugin-framework](https://pypi.org/project/python-workflow-plugin-framework)

## 准备工作

1. **创建 PyPI 账号**：
   - 访问 https://pypi.org/account/register/ 注册账号

2. **获取 API 令牌**（推荐）：
   - 登录后，进入 https://pypi.org/manage/account/token/ 
   - 创建一个新的 API 令牌，选择 "Entire account" 权限
   - 保存好令牌，只显示一次

## 上传包

使用 `twine` 工具上传构建好的包：

```bash
# 使用用户名和密码上传
twine upload dist/*

# 或使用 API 令牌上传（推荐）
twine upload dist/* -u __token__ -p <your-api-token>
```

## 验证上传

上传成功后，可以访问 https://pypi.org/project/python-workflow-plugin-framework/ 查看你的包。

## 使用上传的包

其他用户可以使用 pip 安装你的包：

```bash
pip install python-workflow-plugin-framework
```

## 注意事项

1. 每次更新包时，需要修改 `setup.py` 中的 `version` 字段
2. 上传前确保所有测试通过
3. 保持 README.md 和其他文档的更新
4. 考虑创建一个 .pypirc 文件来存储 PyPI 凭据，避免每次输入

## 后续维护

- 定期更新包版本
- 响应 bug 报告和功能请求
- 保持与最新 Python 版本的兼容性