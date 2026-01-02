from typing import Any, Callable, Dict, List, Optional, TextIO

from ..config import config_dir
from ..ui import TUIRenderer, create_renderer
from .ai import BaseAI


class Agent:
    def __init__(
        self,
        cli_args,
        model: str,
        env_config: Dict[str, str | None],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        before_ai_ask_hook: Optional[Callable] = None,
        after_ai_ask_hook: Optional[Callable] = None,
    ) -> None:
        """
        初始化Agent类。

        :param cli_args: 命令行参数
        :param model: 使用的AI模型名称
        :param env_config: 环境配置字典，包含API_KEY、BASE_URL等
        :param output_io: 用于输出的TextIO对象
        :param tools: 可选，传递给AI的工具
        :param system_prompt: 可选，系统提示信息
        :param messages: 可选，初始消息列表
        :param before_ai_ask_hook: 可选，在向AI提问前执行的钩子函数
        :param after_ai_ask_hook: 可选，在AI回答后执行的钩子函数
        """
        self.cli_args = cli_args
        self.before_ai_ask_hook = before_ai_ask_hook
        self.after_ask_ai_hook = after_ai_ask_hook

        # 根据命令行参数和环境配置确定运行模式
        self.mode = self._determine_mode(cli_args, env_config, system_prompt)

        # 初始化AI对象
        self.ai = self._initialize_ai(model, env_config, tools, messages)

        # 确定 UI 模式 (命令行参数 > 环境配置 > 默认值)
        ui_mode = getattr(cli_args, "ui_mode", None) or env_config.get(
            "UI_MODE", "stdout"
        )
        assert ui_mode in ["stdout", "rich", "tui"], f"Invalid ui_mode: {ui_mode}"

        self.renderer = create_renderer(
            mode=ui_mode,
            config=env_config,
            config_file_path=config_dir / ".env",
            history_dir_path=config_dir / "history",
            config_edited_hook=self._on_config_edited,
            history_deleted_hook=self._on_history_deleted,
            session_deleted_hook=self._on_session_deleted,
        )

        # 如果命令行参数中指定了输出文件，打开文件
        if self.cli_args.output:
            self.output_file = open(cli_args.output, "w", encoding="utf-8")

        self._last_ai_reply: str | None = None

    def _determine_mode(
        self,
        cli_args,
        env_config: Dict[str, str | None],
        system_prompt: Optional[str],
    ) -> str:
        """
        根据命令行参数和环境配置确定运行模式。

        :param cli_args: 命令行参数
        :param env_config: 环境配置字典
        :param system_prompt: 可选，系统提示信息
        :return: 运行模式字符串，如"shell"、"code"或"default"
        """
        if cli_args.shell and cli_args.code:
            raise RuntimeError(
                "Only one of `shell mode` or `code mode` can be active at a time."
            )

        if cli_args.shell:
            from os import getenv as os_getenv
            from platform import system as os_name

            # 如果命令行参数中启用了shell模式，设置系统提示为SHELL_PROMPT
            prompt = env_config.get("SHELL_PROMPT")
            if isinstance(prompt, str) and "{os}" in prompt and "{shell}" in prompt:
                prompt = prompt.format_map(
                    {"os": os_name(), "shell": os_getenv("SHELL")}
                )
            mode = "shell"
            cli_args.ignore_user = cli_args.ignore_ai = True
        elif cli_args.code:
            # 如果命令行参数中启用了code模式，设置系统提示为CODE_PROMPT
            prompt = env_config.get("CODE_PROMPT")
            mode = "code"
            cli_args.ignore_user = cli_args.ignore_ai = True
        else:
            # 否则使用默认提示
            prompt = env_config.get("DEFAULT_PROMPT")
            mode = "default"

        self.system_prompt = prompt if system_prompt is None else system_prompt
        return mode

    def _initialize_ai(
        self,
        model: str,
        env_config: Dict[str, str | None],
        tools: Optional[List[Dict[str, Any]]],
        messages: Optional[List[Dict[str, str]]],
    ) -> BaseAI:
        """
        初始化AI对象。

        :param model: 使用的AI模型名称
        :param env_config: 环境配置字典
        :param tools: 传递给AI的工具
        :param messages: 初始消息列表
        :return: 初始化的BaseAI对象
        """
        api_key = env_config.get("API_KEY")
        base_url = env_config.get("BASE_URL")

        assert api_key, "API_KEY environment variable is required"
        assert base_url, "BASE_URL environment variable is required"

        timeout = int(env_config.get("TIMEOUT") or 60)
        stream = (env_config.get("STREAM") or "true").lower() == "true"
        return BaseAI(
            api_key,
            base_url,
            model,
            timeout,
            stream,
            tools,
            self.system_prompt,
            messages,
        )

    # ================= TUI Hook Callbacks =================
    def _on_config_edited(self, config_text: str) -> None:
        """配置编辑后的回调"""
        from ..config import save_config

        save_config(config_text)
        self._reload_ai_config()

    def _reload_ai_config(self) -> None:
        """重新加载 AI 配置（从 config 模块读取新配置并更新 BaseAI 实例）"""
        from ..config import reload_config

        env_config = reload_config()

        # 读取新的配置值
        api_key = env_config.get("API_KEY")
        base_url = env_config.get("BASE_URL")
        model = env_config.get("DEFAULT_MODEL")
        timeout = int(env_config.get("TIMEOUT") or 60)
        stream = (env_config.get("STREAM") or "true").lower() == "true"

        if not api_key or not base_url:
            return

        # 更新 AI 实例的属性
        self.ai.model = model
        self.ai.stream = stream

        # 重新创建 OpenAI 客户端（因为 timeout/api_key/base_url 可能改变）
        from openai import OpenAI, AsyncOpenAI

        self.ai.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
        self.ai.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def _on_history_deleted(self, session_id: str, history_id: str) -> None:
        """历史记录删除后的回调"""
        pass  # 可以添加额外的处理逻辑

    def _on_session_deleted(self, session_id: str) -> None:
        """会话删除后的回调"""
        pass  # 可以添加额外的处理逻辑

    # ================= AI Ask Hooks =================
    def before_ask_ai(self, user_input: str) -> str:
        """
        在向AI提问前执行的操作。

        :param user_input: 用户输入
        :return: 处理后的用户输入
        """
        if not self.cli_args.ignore_ai:
            self.renderer.render_ai_info(self.ai.model)

        # 如果定义了before_ai_ask_hook，执行钩子函数
        if self.before_ai_ask_hook:
            return self.before_ai_ask_hook(user_input, self.mode)

        return user_input

    def after_ask_ai(self, ai_reply: str) -> str:
        """
        在AI回答后执行的操作。

        :param ai_reply: AI的回答
        :return: 处理后的AI回答
        """

        # 如果指定了输出文件，将AI回答写入文件
        if self.cli_args.output:
            self.output_file.write(f"{ai_reply}\n")

        # 如果定义了after_ask_ai_hook，执行钩子函数
        if self.after_ask_ai_hook:
            return self.after_ask_ai_hook(ai_reply, self.mode)

        return ai_reply

    def ask_ai(self, user_input: str) -> str:
        """
        向AI提问并获取回答。

        :param user_input: 用户输入
        :return: AI的回答
        """
        # 将处理后的用户输入添加到消息列表中
        self.ai.messages.append(self.ai.user_message(self.before_ask_ai(user_input)))
        # 发送消息并获取响应
        response = self.ai.send_messages()
        if isinstance(response, str):
            # 输出错误信息
            return response

        # 使用渲染器流式输出响应
        ai_reply = self.renderer.stream_response(response, self.cli_args.ignore_think)

        # 将AI回答添加到消息列表中
        self.ai.messages.append(self.ai.ai_message(ai_reply))

        ai_reply = self.after_ask_ai(ai_reply)

        self._last_ai_reply = ai_reply
        return ai_reply

    async def ask_ai_async(self, user_input: str) -> str:
        """
        向AI提问并获取回答（异步版本，用于TUI模式）。

        :param user_input: 用户输入
        :return: AI的回答
        """
        # 将处理后的用户输入添加到消息列表中
        self.ai.messages.append(self.ai.user_message(self.before_ask_ai(user_input)))
        # 发送消息并获取响应（异步）
        response = await self.ai.send_messages_async()
        if isinstance(response, str):
            # 输出错误信息
            return response

        # TUI 模式：使用 ChatApp 的异步流式处理
        if isinstance(self.renderer, TUIRenderer):
            app = self.renderer.app
            ai_reply = await app.stream_ai(response, self.cli_args.ignore_think)
        else:
            # 其他渲染器：使用同步方式
            ai_reply = self.renderer.stream_response(
                response, self.cli_args.ignore_think
            )

        # 将AI回答添加到消息列表中
        self.ai.messages.append(self.ai.ai_message(ai_reply))

        ai_reply = self.after_ask_ai(ai_reply)

        self._last_ai_reply = ai_reply
        return ai_reply

    def run(self) -> None:
        """
        运行Agent，处理用户输入和AI交互。
        """
        # TUI 模式直接运行 TUI 应用
        if isinstance(self.renderer, TUIRenderer):
            self.renderer.run(
                (self.cli_args.prompt or "").strip(),
                ask_ai_async=self.ask_ai_async,
                ai=self.ai,
            )
            return

        # 非 TUI 模式，使用 renderer 处理用户输入
        if self.cli_args.prompt:
            args_prompt = self.cli_args.prompt
            pipe_prompt = self.renderer.get_user_input(
                self.cli_args,
                need_user_input=False,
            )
            show_pipe = bool(pipe_prompt)
            prompt_show = "Arg Prompt"
            if self.cli_args.ahead:
                prompt = args_prompt + pipe_prompt
                prompt_show = "Arg+Pipe Prompt" if show_pipe else prompt_show
            else:
                prompt = pipe_prompt + args_prompt
                prompt_show = "Pipe+Arg Prompt" if show_pipe else prompt_show

            prompt = prompt.strip()
            if not self.cli_args.ignore_user:
                self.renderer.render_user_info(prompt_show)

            if self.mode == "default":
                self.renderer.render_user_input(prompt)
            self.ask_ai(prompt)

        if self.cli_args.conversation or not self.cli_args.prompt:
            while user_input := self.renderer.get_user_input(self.cli_args):
                self.ask_ai(user_input)
                if not self.cli_args.conversation:
                    break

    def __del__(self):
        """
        在Agent退出时执行的操作，如关闭输出文件。
        """
        if self.cli_args.output and not self.output_file.closed:
            self.output_file.close()

        self.renderer.close()
