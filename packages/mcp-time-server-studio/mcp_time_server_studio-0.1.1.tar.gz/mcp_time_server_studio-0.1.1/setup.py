from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-time-server-studio",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于 Model Context Protocol (MCP) 的时间服务器，支持通过 StreamableHTTP 传输协议提供当前时间查询服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-time-server-studio",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords=["time-server", "mcp", "json-rpc", "fastapi", "timezone", "streamable-http"],
    python_requires=">=3.7",
    install_requires=[
        "mcp>=0.1.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "pytz>=2023.3",
        "anyio>=3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "mcp-time-server-studio=time_server_pkg.main:main",
        ],
    },
    package_data={
        "time_server_pkg": ["py.typed"],
    },
)