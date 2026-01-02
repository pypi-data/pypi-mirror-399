from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-workflow-plugin-framework",
    version="1.2.0",
    author="gw123",
    author_email="963383840@qq.com",
    description="一个简化 Python 插件开发的通用框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python-plugin-framework",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    package_data={
        "": ["*.py"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=[
        "grpcio>=1.60.0",
        "glog-python==1.0.1",
        "requests>=2.31.0",
        "langchain>=0.1.0",
        "ollama>=0.1.0",
    ],
)