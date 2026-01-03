# NexAgent

[![PyPI version](https://img.shields.io/pypi/v/nex-agent.svg)](https://pypi.org/project/nex-agent/)
[![Python versions](https://img.shields.io/pypi/pyversions/nex-agent.svg)](https://pypi.org/project/nex-agent/)
[![License](https://img.shields.io/pypi/l/nex-agent.svg)](https://pypi.org/project/nex-agent/)

AI 对话框架，支持多模型、多会话、工具调用、MCP 协议、深度思考、记忆功能、角色卡。

## 特性

- 🔄 多模型切换 - 支持 OpenAI、DeepSeek 等兼容 API
- 💬 多会话管理 - 独立上下文，消息编辑/重新生成
- 🎭 角色卡 - 自定义 AI 人设和参数
- 🧠 记忆功能 - 基于向量的长期记忆
- 🔧 工具调用 - 内置 + 自定义 + MCP 工具
- 💭 深度思考 - 展示 AI 推理过程
- 📡 流式输出 - 实时返回内容
- 🌐 WebUI - 现代化界面，深色/浅色主题

## 快速开始

```bash
pip install nex-agent

nex init          # 初始化工作目录
nex serve         # 启动服务 (默认 8000 端口)
```

打开 http://localhost:8000，在设置中添加服务商和模型即可使用。

## 代码使用

```python
from nex_agent import NexFramework

nex = NexFramework("./my_project")

# 创建会话并对话
session_id = nex.create_session("测试", "user1")
reply = nex.chat("user1", "你好", session_id=session_id)

# 流式对话
for chunk in nex.chat_stream("user1", "讲个故事", session_id=session_id):
    print(chunk, end="", flush=True)
```

## 自定义工具

在 `tools/` 目录创建 Python 文件：

```python
# tools/calculator.py
TOOL_DEF = {
    "name": "calculator",
    "description": "计算器",
    "parameters": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"]
    }
}

def execute(args):
    return str(eval(args["expression"]))
```

## API

主要接口：

| 接口 | 说明 |
|------|------|
| `POST /nex/chat` | 对话（支持流式） |
| `GET/POST/DELETE /nex/sessions` | 会话管理 |
| `GET/POST/DELETE /nex/models` | 模型管理 |
| `GET/POST/DELETE /nex/providers` | 服务商管理 |
| `GET/POST/DELETE /nex/personas` | 角色卡管理 |
| `GET/POST/DELETE /nex/memories` | 记忆管理 |
| `GET/POST/DELETE /nex/mcp/servers` | MCP 服务器 |

## License

MIT
