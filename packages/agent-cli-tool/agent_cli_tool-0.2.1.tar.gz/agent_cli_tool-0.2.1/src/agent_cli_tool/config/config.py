from dotenv import dotenv_values
from pathlib import Path

# 配置文件路径
config_dir = Path.home() / ".config" / "agent-cli-tool"
config_file = config_dir / ".env"

# 加载配置文件
env_config = dotenv_values(
    stream=config_file.open("r", encoding="utf-8") if config_file.exists() else None
)

assert env_config, (
    f"environment config not found, please edit your config file: {config_file.absolute()}"
)

DEFAULT_PROMPT = "你是帮用户解决问题的AI,所有回复使用中文"
SHELL_PROMPT = """Provide only `{shell} `commands for `{os}` without any description.
If there is a lack of details, provide most logical solution.
Ensure the output is a valid shell command.
If multiple steps required try to combine them together using &&.
Provide only plain text without Markdown formatting.
Do not provide markdown formatting such as ``` or ```bash ."""
CODE_PROMPT = """Provide only code as output without any description.
Provide only code in plain text format without Markdown formatting.
Do not include symbols such as ``` or ```python.
If there is a lack of details, provide most logical solution.
The default code language is '{DEFAULT_LANGUAGE}'.
You are not allowed to ask for more details.
For example if the prompt is 'Hello world with Python', you should return 'print(\"Hello world\")'"""

defalut_config = {
    "DEFAULT_PROMPT": DEFAULT_PROMPT,
    "SHELL_PROMPT": SHELL_PROMPT,
    "DEFAULT_LANGUAGE": "python3",
    "CODE_PROMPT": CODE_PROMPT,
    "STREAM": "true",
    "DEFAULT_MODEL": "deepseek-chat",
    "RICH_STYLE": "github-dark",  # https://pygments.org/styles/
    "UI_MODE": "stdout",  # stdout, rich, tui
}

for key in defalut_config:
    if key not in env_config:
        env_config[key] = defalut_config[key]

env_config["CODE_PROMPT"] = env_config["CODE_PROMPT"].format(
    DEFAULT_LANGUAGE=env_config["DEFAULT_LANGUAGE"]
)


# ================= 配置管理函数 =================
def save_config(env_text: str) -> dict:
    """保存配置到文件并重新加载

    Args:
        env_text: .env 格式的配置文本

    Returns:
        重新加载后的配置字典
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(env_text, encoding="utf-8")
    return reload_config()


def reload_config() -> dict:
    """重新加载配置文件

    Returns:
        配置字典
    """
    global env_config
    env_config = dotenv_values(
        stream=config_file.open("r", encoding="utf-8") if config_file.exists() else None
    )

    # 填充默认值
    for key in defalut_config:
        if key not in env_config:
            env_config[key] = defalut_config[key]

    # 格式化 CODE_PROMPT
    code_prompt = env_config.get("CODE_PROMPT")
    if isinstance(code_prompt, str):
        env_config["CODE_PROMPT"] = code_prompt.format(
            DEFAULT_LANGUAGE=env_config.get("DEFAULT_LANGUAGE", "python3")
        )

    return env_config


def get_config_text() -> str:
    """获取配置文件的原始文本内容

    Returns:
        .env 文件的文本内容，文件不存在返回空字符串
    """
    if config_file.exists():
        return config_file.read_text(encoding="utf-8")
    return ""
