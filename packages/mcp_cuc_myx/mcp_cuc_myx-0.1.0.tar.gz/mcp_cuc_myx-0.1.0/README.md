# MCP Time Server

[![PyPI version](https://badge.fury.io/py/mcp-time-server.svg)](https://badge.fury.io/py/mcp-time-server)
[![Python Support](https://img.shields.io/pypi/pyversions/mcp-time-server.svg)](https://pypi.org/project/mcp-time-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于 MCP (Model Context Protocol) 的时间服务器，提供当前时间获取功能。

## 特性

- 🎯 基于 MCP 协议的时间服务
- 🌍 支持全球时区查询
- 🚀 基于 FastMCP 的高性能实现
- 📦 易于安装和集成
- 🔧 支持命令行和编程接口

## 安装

### 使用 pip 安装

```bash
pip install mcp-time-server
```

### 开发环境安装

```bash
git clone https://github.com/example/mcp-time-server.git
cd mcp-time-server
pip install -e .
```

## 快速开始

### 命令行使用

```bash
# 启动服务器（使用默认时区）
mcp-time-server

# 服务器将通过 stdio 启动，等待 MCP 客户端连接
```

### Python 编程接口

```python
from mcp_time_server import get_current_time

# 获取当前时间（使用系统默认时区）
current_time = get_current_time()
print(current_time)

# 获取指定时区的当前时间
beijing_time = get_current_time("Asia/Shanghai")
print(beijing_time)

# 获取纽约时间
ny_time = get_current_time("America/New_York")
print(ny_time)
```

## MCP 工具

### `get_current_time`

获取当前时间的 MCP 工具函数。

**参数:**
- `timezone` (可选): 时区字符串，例如 "Asia/Shanghai"、"America/New_York"
  - 如果不提供，将使用系统默认时区

**返回值:**
- 格式化的当前时间字符串，格式：YYYY-MM-DD HH:MM:SS.SSSSSS 时区名称

**支持的时区示例:**
- `Asia/Shanghai` - 中国标准时间
- `America/New_York` - 纽约时间
- `Europe/London` - 伦敦时间
- `UTC` - 协调世界时
- `Asia/Tokyo` - 日本标准时间

## 示例输出

```
2025-12-30 19:54:32.123456 CST
2025-12-30 07:54:32.123456 EST
2025-12-30 12:54:32.123456 UTC
```

## 依赖项

- `pytz` - 时区处理库
- `mcp` - Model Context Protocol 库

## 兼容性

- Python 3.8+
- 支持所有主要操作系统（Windows、macOS、Linux）

## 开发

### 本地开发设置

```bash
# 克隆仓库
git clone https://github.com/example/mcp-time-server.git
cd mcp-time-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest
```

### 构建包

```bash
# 构建分发包
python -m build

# 检查构建结果
python -m twine check dist/*
```

## 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v0.1.0
- 初始版本发布
- 支持基本的时间获取功能
- 支持时区参数
- MCP 协议集成