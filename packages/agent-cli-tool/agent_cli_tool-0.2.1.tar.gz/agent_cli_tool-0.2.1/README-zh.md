# Agent CLI Tool

[![PyPI version](https://badge.fury.io/py/agent-cli-tool.svg)](https://badge.fury.io/py/agent-cli-tool)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个强大的命令行工具，可以直接在终端与 AI 模型（OpenAI、DeepSeek、Claude）进行交互。具有基于插件的架构、多种 UI 模式和可扩展的钩子系统。

## 特性

- **三种 UI 模式**：
  - `stdout` - 带 ANSI 颜色的纯文本输出
  - `rich` - 实时 Markdown 渲染和语法高亮
  - `tui` - 功能完整的交互式终端 UI，支持会话管理
- **AI 模式**：
  - `default` - 通用对话模式
  - `shell` - 仅生成 shell 命令
  - `code` - 仅生成代码
- **插件系统** - 基于钩子的可扩展架构
- **内置插件**：
  - `@file("path")` - 将文件内容注入到提示词中
  - `@fetch("url")` - 获取并注入网页内容
  - Shell 命令执行确认
- **多模态输入** - 支持命令行参数、管道或交互式 TTY
- **会话管理**（TUI 模式）- 历史记录浏览和持久化存储

## 安装

### 使用 pip

```bash
pip install agent-cli-tool
```

### 使用 uv

```bash
uv tool install agent-cli-tool
```

### 从源码安装

```bash
git clone https://github.com/Awoodwhale/agent-cli-tool.git
cd agent-cli-tool
uv pip install -e .
```

## 配置

在 `~/.config/agent-cli-tool/.env` 创建配置文件：

```bash
# 必需配置
API_KEY=your_api_key
BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=deepseek-chat

# 可选配置
UI_MODE=stdout              # stdout | rich | tui
DEFAULT_LANGUAGE=python3    # code 模式的默认语言
RICH_STYLE=github-dark      # rich 模式的 Pygments 样式
STREAM=true                 # 启用流式输出
TIMEOUT=60                  # 请求超时时间（秒）

# 自定义提示词
DEFAULT_PROMPT=你是一个有帮助的助手
SHELL_PROMPT=仅提供 shell 命令...
CODE_PROMPT=仅提供代码...

# UI 自定义（用于 stdout/rich 模式）
USER_EMOJI=👤
AI_EMOJI=🤖
THINK_START_EMOJI=🤔 [思考中]
THINK_END_EMOJI=💡 [完成]
```

## 使用方法

### 基本查询

```bash
agent-cli-tool "解释量子计算"
```

### UI 模式

```bash
# 纯文本输出（默认）
agent-cli-tool "什么是 AI？"

# Markdown 渲染
agent-cli-tool --ui-mode rich "解释机器学习"

# 交互式 TUI，支持会话管理
agent-cli-tool --ui-mode tui
```

### AI 模式

```bash
# Shell 模式 - 仅生成 shell 命令
agent-cli-tool --shell "列出所有 python 进程"

# Code 模式 - 仅生成代码
agent-cli-tool --code "python 斐波那契函数"
```

### 对话模式

```bash
# 多轮对话
agent-cli-tool --conversation
# 或
agent-cli-tool -c
```

### 模型选择

```bash
agent-cli-tool -m GPT-5 "解释量子计算"           # GPT-5
agent-cli-tool -m deepseek-r1 "解决这个数学问题"  # DeepSeek Reasoner
agent-cli-tool -m "claude sonnet 4.5" "写一首诗"  # Claude Sonnet 4.5
```

### 输出到文件

```bash
agent-cli-tool --code "python 网络爬虫" --output scraper.py
```

### 使用插件

```bash
# 注入文件内容
agent-cli-tool '审查这段代码: @file("src/main.py")'

# 获取网页内容
agent-cli-tool '总结这篇文章: @fetch("https://example.com/article")'
```

### 管道输入

```bash
echo "解释这个错误" | agent-cli-tool
cat error.log | agent-cli-tool "哪里出错了？"
```

## 命令行选项

```
usage: agent-cli-tool [-h] [-m MODEL] [-a] [-iu] [-ia] [-it] [-c] [-sh] [-co] [-o OUTPUT] [-u {stdout,rich,tui}] [prompt]

位置参数:
  prompt                 用户输入的提示词

选项:
  -h, --help             显示帮助信息
  -m, --model MODEL      使用的 AI 模型
  -a, --ahead            将参数提示词放在管道提示词之前（默认: true）
  -iu, --ignore_user     不显示用户输入
  -ia, --ignore_ai       不显示 AI 模型信息
  -it, --ignore_think    不显示 AI 思考/推理内容
  -c, --conversation     启用多轮对话模式
  -sh, --shell           Shell 模式 - 仅输出 shell 命令
  -co, --code            Code 模式 - 仅输出代码
  -o, --output OUTPUT    将输出写入文件
  -u, --ui-mode {stdout,rich,tui}
                         UI 渲染模式
```

## TUI 模式

TUI 模式提供功能完整的交互式终端界面：

### 快捷键

| 按键 | 操作 |
|-----|------|
| `Ctrl+D` | 发送输入 |
| `Ctrl+L` | 清空输入 |
| `Ctrl+E` | 切换历史面板 |
| `Ctrl+T` | 新建会话 |
| `Ctrl+B` | 切换 Markdown/纯文本渲染 |
| `Ctrl+G` | 编辑配置 |
| `Ctrl+C` | 停止生成（双击退出程序） |
| `Delete` | 删除选中的历史/会话 |
| `ESC` | 关闭弹窗对话框 |

### 功能特性

- 会话管理，自动生成标题
- 历史记录浏览和搜索
- 配置编辑弹窗
- 持久化聊天记录存储在 `~/.config/agent-cli-tool/history/`


## 开发

### 项目结构

```
src/agent_cli_tool/
├── __init__.py          # 入口点
├── agents/
│   ├── agent.py         # 中央协调器
│   └── ai.py            # OpenAI 客户端封装
├── cli/
│   └── cli.py           # 参数解析器
├── config/
│   └── config.py        # 配置管理
├── plugins/
│   ├── __init__.py      # 插件加载器
│   ├── fetch.py         # 网页内容获取
│   ├── file.py          # 文件内容注入
│   └── shell.py         # Shell 确认插件
└── ui/
    ├── base.py          # 基础渲染器
    ├── stdout.py        # 纯文本渲染器
    ├── rich.py          # Markdown 渲染器
    └── tui.py           # 交互式 TUI 渲染器
```

### 架构

```
main() → Agent → Renderer (stdout/rich/tui) → Output
         ↓
    CLI Args & Config
         ↓
    Plugin System (before/after hooks)
         ↓
    BaseAI → OpenAI API
```

### 创建插件

在 `src/agent_cli_tool/plugins/` 目录下创建 Python 文件：

```python
# my_plugin.py
def before_ai_ask_hook(user_input: str, mode: str) -> str:
    """在发送到 AI 之前处理用户输入"""
    # 根据需要修改 user_input
    return user_input

def after_ai_ask_hook(ai_reply: str, mode: str) -> str:
    """在接收 AI 响应后处理回复"""
    # 根据需要修改 ai_reply
    return ai_reply
```

插件会在运行时自动发现和加载。

### 依赖项

- `openai>=1.75.0` - OpenAI API 客户端
- `python-dotenv>=1.1.0` - 配置管理
- `requests>=2.32.3` - HTTP 请求
- `rich>=14.0.0` - 终端渲染
- `textual>=6.11.0` - TUI 框架
- `wcwidth>=0.2.14` - Unicode 宽度处理

## 许可证

MIT
