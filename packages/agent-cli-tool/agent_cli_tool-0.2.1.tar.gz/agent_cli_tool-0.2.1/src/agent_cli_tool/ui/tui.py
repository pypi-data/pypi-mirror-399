import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

from dotenv import dotenv_values
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Markdown,
    Static,
    TextArea,
    Tree,
)

from ..agents.ai import BaseAI
from .base import BaseRenderer


# ================= 数据模型 =================
@dataclass
class History:
    id: str = field(default_factory=lambda: str(uuid4()))
    prompt: str = ""
    reply: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model: str = ""


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    histories: list[History] = field(default_factory=list)


# ================= 配置编辑弹窗 =================
class ConfigEditor(ModalScreen):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
    ]

    CSS = """
    #dialog {padding: 0 2;margin: 2 4;border: round $primary;background: $surface;}
    #title {content-align: center middle;text-style: bold;height: 1;}
    #config_input {height: 1fr;border: solid $secondary;}
    #button_bar {content-align: center middle;height: 3;}
    #button_bar Button {width: 50%;}
    #save {margin: 0 1 0 0;}
    #cancel {margin: 0 0 0 1;}
    """

    def compose(self) -> ComposeResult:
        # 获取 .env 文件的原始内容
        config_text = self.app._get_config_text()

        yield Vertical(
            Static("编辑配置文件", id="title"),
            (
                text_area := TextArea(
                    config_text,
                    id="config_input",
                )
            ),
            Horizontal(
                Button("保存(Ctrl+s)", id="save", variant="success", flat=True),
                Button("取消(ESC/Ctrl+g)", id="cancel", variant="error", flat=True),
                id="button_bar",
            ),
            id="dialog",
        )
        text_area.border_title = "Config (.env)"

    # ---------- Actions ----------
    def action_save(self):
        try:
            text = self.query_one("#config_input", TextArea).text.strip()

            # 使用 dotenv 解析并更新 config_data
            import os
            import tempfile

            from dotenv import dotenv_values

            # 创建临时文件来解析 .env 内容
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".env"
            ) as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            try:
                app: ChatApp = self.app  # ty:ignore[invalid-assignment]
                app.config_data = dotenv_values(tmp_path)

                # 调用 hook callback 让外部处理保存
                if callable(app.config_edited_hook):
                    app.config_edited_hook(text)

                self.notify("配置已保存", timeout=1)
                self.dismiss(text)
            finally:
                os.unlink(tmp_path)

        except Exception as e:
            self.notify(f"保存失败: {e}", severity="error", timeout=2)

    def action_close(self):
        self.dismiss()

    # ---------- Button ----------
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            self.action_save()
        elif event.button.id == "cancel":
            self.action_close()

    def on_key(self, event):
        if event.key in ["ctrl+g", "escape"]:
            event.stop()
            self.action_close()


# ================= 删除确认弹窗 =================
class DeleteConfirmDialog(ModalScreen):
    """删除 session 时的确认对话框"""

    CSS = """
    #dialog {
        padding: 1 2;
        margin: 2 4;
        border: round $error;
        background: $surface;
    }
    #title {
        content-align: center middle;
        text-style: bold;
        height: 1;
        color: $error;
    }
    #message {
        content-align: center middle;
        height: 1fr;
    }
    #button_bar {content-align: center middle;height: 3;}
    #button_bar Button {width: 50%;}
    #confirm { margin: 0 1 0 0; }
    #cancel { margin: 0 0 0 1; }
    """

    def __init__(self, session_title: str):
        super().__init__()
        self.session_title = session_title

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("确认删除", id="title"),
            Static(
                f"确定要删除会话「{self.session_title}」吗？\n这将删除该会话的所有历史记录！",
                id="message",
            ),
            Horizontal(
                Button("确认删除(Y/y)", id="confirm", variant="error", flat=True),
                Button("取消(ESC)", id="cancel", variant="default", flat=True),
                id="button_bar",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(True)
        elif event.button.id == "cancel":
            self.dismiss(False)

    def on_key(self, event):
        if event.key == "escape":
            event.stop()
            self.dismiss(False)
        elif event.key in ["Y", "y"]:
            event.stop()
            self.dismiss(True)


# ================= 主应用 =================
class ChatApp(App):
    CSS = """
    #history_tree { width: 25; border-right: solid gray; }
    #chat_panel { width: 1fr; }
    #ai_scroll { height: 1fr; border: solid green; }
    #user_input { height: 5; border: solid blue; }
    #ai_output {padding: 0 1; }
    """

    BINDINGS = [
        Binding("ctrl+t", "new_session", "New Session", priority=True),
        Binding("ctrl+b", "toggle_markdown", "Markdown/Raw", priority=True),
        Binding("ctrl+e", "toggle_history", "Toggle History", priority=True),
        Binding("ctrl+g", "edit_config", "Edit Config"),
        Binding("ctrl+q", "noop", show=False, priority=True),
    ]

    def __init__(
        self,
        config_file_path: Path | str,
        history_file_path: Path | str,
        config_edited_hook: Callable,
        history_deleted_hook: Callable,
        session_deleted_hook: Callable,
        stream_response: Callable,
        ask_ai_async: Callable,
        ai: BaseAI,  # BaseAI 实例，用于访问 AI 上下文和发送消息
        think_start_emoji: str,
        think_end_emoji: str,
        use_markdown: bool = True,
    ):
        super().__init__()

        # ===== 初始化配置 =====
        self.use_markdown = use_markdown
        self.config_data = {}
        self.config_edited_hook = config_edited_hook
        self.history_deleted_hook = history_deleted_hook
        self.session_deleted_hook = session_deleted_hook
        self.stream_response = stream_response
        self.ai = ai  # 保存 BaseAI 引用
        self.ask_ai_async = ask_ai_async
        self.think_start_emoji = think_start_emoji
        self.think_end_emoji = think_end_emoji

        # ===== 配置和历史文件路径（使用 config 模块的路径） =====
        self._config_file = (
            config_file_path
            if isinstance(config_file_path, Path)
            else Path(config_file_path)
        )
        self._history_dir = (
            history_file_path
            if isinstance(history_file_path, Path)
            else Path(history_file_path)
        )

        # ===== UI 状态 =====
        self._hide_history = False
        self._hide_config = True

        # ===== 对话历史 =====
        self.sessions: list[Session] = []
        self.current_session: Session | None = None
        self.current_history: History | None = None
        self.current_node = None

        # ===== streaming =====
        self._streaming = False
        self._ai_buffer = ""

        # ===== Ctrl+C 双击退出 =====
        self._last_ctrl_c = 0.0
        self._ctrl_c_count = 0
        self._ctrl_c_timeout = 1

    # ---------- UI ----------
    def compose(self) -> ComposeResult:
        self.main_panel = Horizontal(id="main_panel")
        with self.main_panel:
            self.history_tree = Tree("「Chat History」", id="history_tree")
            yield self.history_tree
            self.chat_panel = Vertical(id="chat_panel")
            with self.chat_panel:
                self.ai_scroll = VerticalScroll(id="ai_scroll")
                with self.ai_scroll:
                    self.ai_output = self.get_content_render_clz()("", id="ai_output")
                    yield self.ai_output
                self.user_input = TextArea(
                    placeholder="Enter 换行 | Ctrl+L 清空 | Ctrl+D 发送 | Ctrl+C 停止/退出",
                    id="user_input",
                )
                yield self.user_input
        yield Footer()

        self.history_tree.border_title = "Chat History"
        self.ai_scroll.border_title = "AI Output"
        self.user_input.border_title = "User Input"

    # ---------- 键盘事件 ----------
    async def on_key(self, event: Key) -> None:
        if event.key == "ctrl+c":
            await self._handle_ctrl_c(event)
        elif event.key == "ctrl+d":
            event.stop()
            await self._send_current_input()
        elif event.key == "ctrl+g":
            event.stop()
            self.action_edit_config()
        elif event.key == "ctrl+e":
            event.stop()
            self.action_toggle_history()
        elif event.key == "ctrl+l":
            event.stop()
            self.set_user_input("")
        elif event.key == "delete":
            event.stop()
            await self._handle_delete()

    def on_mount(self):
        self._load_config()
        self._load_history()
        self.set_focus(self.user_input)
        self.theme = "tokyo-night"

    def on_unmount(self):
        """程序退出时保存历史记录"""
        # 如果当前 session 是 "New Session" 且有历史记录，更新其 title
        if self.current_session and self.current_session.title == "New Session":
            if self.current_session.histories:
                first_prompt = self.current_session.histories[0].prompt
                new_title = (
                    first_prompt[:10] if len(first_prompt) >= 10 else first_prompt
                )
                self.current_session.title = new_title

        self._save_history()

    async def _stream_ai_worker(self, response, ignore_think: bool):
        """Async worker for streaming AI response using OpenAI async client."""
        has_thinking = False

        try:
            self.ai_output.loading = False
            if isinstance(response, str):
                # Error occurred
                self._ai_buffer = response
                self.notify(f"AI错误: {response}", severity="error", timeout=5.0)
                if self.current_history:
                    self.current_history.reply = self._ai_buffer
                self.ai_output.update(self._ai_buffer)
                return

            # Stream the response using async iteration
            async for chunk in response:
                if not self._streaming:
                    break

                delta = chunk.choices[0].delta

                # Regular content
                if hasattr(delta, "content") and delta.content:
                    if has_thinking:
                        self._ai_buffer += f"\n> {self.think_end_emoji}\n\n"

                    content = delta.content
                    self._ai_buffer += content

                    if self.current_history:
                        self.current_history.reply = self._ai_buffer

                    self.ai_output.update(self._ai_buffer)
                    self.ai_scroll.scroll_end(animate=False)

                # Thinking/reasoning content (for DeepSeek models)
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    if ignore_think:
                        continue
                    if not has_thinking:
                        has_thinking = True
                        self._ai_buffer += f"\n> {self.think_start_emoji}\n\n"

                    self._ai_buffer += delta.reasoning_content

                    if self.current_history:
                        self.current_history.reply = self._ai_buffer

                    self.ai_output.update(self._ai_buffer)
                    self.ai_scroll.scroll_end(animate=False)

            # 流结束后确保滚动到底部
            self.ai_scroll.scroll_end(animate=False)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            error_msg = f"请求失败: {e}"
            self._ai_buffer = error_msg
            self.notify(error_msg, severity="error", timeout=3.0)
            if self.current_history:
                self.current_history.reply = self._ai_buffer
            self.ai_output.update(self._ai_buffer)
        finally:
            self._streaming = False

    async def stream_ai(self, response, ignore_think: bool):
        """Stream AI response using async iteration.

        This method directly awaits the streaming worker without using run_worker().
        """
        self._streaming = True
        self._ai_buffer = ""
        self.run_worker(self._stream_ai_worker(response, ignore_think), exclusive=True)
        return self._ai_buffer

    # ---------- Ctrl+D 发送 ----------
    async def _send_current_input(self):
        if self._streaming:
            return

        prompt = self.user_input.text.strip()
        if not prompt:
            return

        # 获取当前模型
        model = self.ai.model

        history = History(prompt=prompt, model=model)
        self.current_history = history
        self.current_session.histories.append(history)

        session_node = self._find_session_node(self.current_session)
        session_node.add_leaf(
            history.prompt.splitlines()[0][:30],
            data=history,
        )

        if not session_node.is_expanded:
            session_node.expand()

        self.set_user_input("")
        self.ai_output.loading = True

        await self.ask_ai_async(prompt)

    # ---------- Ctrl+C ----------
    async def _handle_ctrl_c(self, event: Key):
        now = time.monotonic()
        if now - self._last_ctrl_c > self._ctrl_c_timeout:
            self._ctrl_c_count = 0

        self._ctrl_c_count += 1
        self._last_ctrl_c = now

        if self._streaming:
            event.stop()
            self._stop_streaming()
            self.notify("生成已停止 (Ctrl+C)", severity="error", timeout=1.0)
            return

        if self._ctrl_c_count == 1:
            event.stop()
            self.notify("再次按 Ctrl+C 退出程序", severity="warning", timeout=1.0)
            return

        self.on_unmount()
        self.exit()

    def _stop_streaming(self):
        self._streaming = False

    # ---------- Delete 处理 ----------
    async def _handle_delete(self):
        """处理 del 键，删除当前选中的 history 或 session"""
        if self._streaming:
            self.notify("生成中，无法删除", severity="warning", timeout=1.0)
            return

        selected_node = self.history_tree.cursor_node
        if selected_node is None:
            return

        if isinstance(selected_node.data, History):
            # 删除单个 history，无需确认
            await self._delete_history(selected_node)
        elif isinstance(selected_node.data, Session):
            # 删除 session 需要确认
            await self._delete_session(selected_node)

    async def _delete_history(self, history_node):
        """删除单个 history"""
        history: History = history_node.data
        session: Session = history_node.parent.data

        # 从 session 的 histories 中移除
        if history in session.histories:
            session.histories.remove(history)

        # 从 tree 中移除节点
        history_node.remove()

        # 清空当前显示
        if self.current_history == history:
            self.current_history = None
            self.set_ai_output("")
            self.set_user_input("")

        # 调用 hook callback
        if callable(self.history_deleted_hook):
            self.history_deleted_hook(session.id, history.id)

        # 动态更新历史文件
        self._save_history()

        self.notify("已删除历史记录", timeout=1.0)

    async def _delete_session(self, session_node):
        """删除整个 session（需要确认）"""
        session: Session = session_node.data

        def on_confirmed(confirmed: bool | None):
            if confirmed:
                # 从 sessions 列表中移除
                if session in self.sessions:
                    self.sessions.remove(session)

                # 从 tree 中移除节点
                session_node.remove()

                # 如果删除的是当前 session，清空显示
                if self.current_session == session:
                    self.current_session = None
                    self.current_history = None
                    self.set_ai_output("")
                    self.set_user_input("")

                # 如果还有其他 session，选中第一个
                if self.sessions and self.history_tree.root.children:
                    first_node = self.history_tree.root.children[0]
                    self.history_tree.select_node(first_node)
                else:
                    # 创建新 session
                    self.action_new_session()

                # 调用 hook callback
                if callable(self.session_deleted_hook):
                    self.session_deleted_hook(session.id)

                # 删除对应的历史文件
                history_file = self._history_dir / f"{session.id}.json"
                if history_file.exists():
                    history_file.unlink()

                # 动态更新历史文件
                self._save_history()

                self.notify(f"已删除会话「{session.title}」", timeout=1.0)

        self.push_screen(DeleteConfirmDialog(session.title), on_confirmed)

    # ---------- 配置文件读取（使用 config 模块） ----------
    def _get_config_text(self) -> str:
        """获取 .env 文件的原始文本内容"""
        return self._config_file.read_text().strip()

    # ---------- 加载 Config 和 History ----------
    def _load_config(self):
        """从配置文件加载 config（.env 格式，使用 dotenv 解析，只读）"""
        if self._config_file.exists():
            try:
                self.config_data = dotenv_values(self._config_file)
            except Exception as e:
                self.notify(f"加载配置文件失败: {e}", severity="error", timeout=2.0)
        else:
            self.notify("配置文件不存在", severity="warning", timeout=1.0)

    def _load_history(self):
        """从历史文件目录加载对话历史（按最后一次对话时间倒序）"""
        if not self._history_dir.exists():
            self._history_dir.mkdir()

        try:
            # 获取所有历史文件
            history_files = list(self._history_dir.glob("*.json"))

            for history_file in history_files:
                try:
                    with open(history_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 解析 session 数据
                    session = Session(
                        id=data.get("id", str(uuid4())),
                        title=data.get("title", "Untitled Session"),
                    )

                    # 解析 histories
                    for hist_data in data.get("histories", []):
                        history = History(
                            id=hist_data.get("id", str(uuid4())),
                            prompt=hist_data.get("prompt", ""),
                            reply=hist_data.get("reply"),
                            timestamp=hist_data.get(
                                "timestamp", datetime.now().isoformat()
                            ),
                            model=hist_data.get("model", ""),
                        )
                        session.histories.append(history)

                    # 如果没有有效的历史内容，删除文件
                    if not session.histories:
                        history_file.unlink()
                        continue

                    self.sessions.append(session)

                except (json.JSONDecodeError, IOError, KeyError) as e:
                    self.notify(
                        f"加载历史文件 {history_file.name} 失败: {e}",
                        severity="error",
                        timeout=2.0,
                    )
                    continue

            # 按最后一次对话时间倒序排序
            def get_last_timestamp(session: Session) -> str:
                if session.histories:
                    return session.histories[-1].timestamp
                return "1970-01-01T00:00:00"

            self.sessions.sort(key=get_last_timestamp, reverse=True)

            # 按排序后的顺序添加到 tree
            for session in self.sessions:
                node = self.history_tree.root.add(session.title, data=session)
                for history in session.histories:
                    node.add_leaf(history.prompt.splitlines()[0][:30], data=history)

            # 创建新 session
            self.action_new_session()

        except Exception as e:
            self.notify(f"加载历史记录失败: {e}", severity="error", timeout=2.0)

    def _save_history(self):
        """保存所有会话到历史文件"""
        if not self._history_dir.exists():
            self._history_dir.mkdir(parents=True, exist_ok=True)

        for session in self.sessions:
            try:
                if not session.histories:
                    continue

                # 构建保存数据
                data = {
                    "id": session.id,
                    "title": session.title,
                    "histories": [
                        {
                            "id": h.id,
                            "prompt": h.prompt,
                            "reply": h.reply,
                            "timestamp": h.timestamp,
                            "model": h.model,
                        }
                        for h in session.histories
                    ],
                }

                # 保存到文件
                history_file = self._history_dir / f"{session.id}.json"
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            except Exception as e:
                self.notify(
                    f"保存会话 {session.title} 失败: {e}", severity="error", timeout=2.0
                )

    def _find_session_node(self, session: Session | None):
        if not session:
            return self.current_node

        for node in self.history_tree.root.children:
            if node.data == session:
                return node

        return self.current_node

    def get_content_render_clz(self) -> type[Static | Markdown]:
        return Markdown if self.use_markdown else Static

    # ---------- Tree ----------
    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if self._streaming:
            return None

        node = event.node
        if isinstance(node.data, Session):
            # 切换到新 session
            self.current_session = node.data
            self.current_history = None
            self.set_ai_output("")
            self.set_user_input("")

        elif isinstance(node.data, History):
            # 切换到该 history 所属的 session
            self.current_session = node.parent.data
            self.current_history = node.data
            self.set_ai_output(node.data.reply)
            self.set_user_input(node.data.prompt)

        self._on_session_selected(self.current_session)

    def _on_session_selected(self, session: Session | None):
        if not self.ai or session is None:
            return None

        self.ai.messages = self.ai.get_init_messages()
        for history in session.histories:
            self.ai.messages.append(self.ai.user_message(history.prompt))
            self.ai.messages.append(self.ai.ai_message(history.reply or ""))

    def set_ai_output(self, content: str):
        self.ai_output.update(content)

    def set_user_input(self, content: str):
        self.user_input.load_text(content)

    # ---------- Actions ----------
    async def action_toggle_markdown(self):
        self.use_markdown = not self.use_markdown
        self.notify(
            f"markdown渲染已{'开启' if self.use_markdown else '关闭'}",
            timeout=1,
        )

        await self.ai_output.remove()
        self.ai_output = self.get_content_render_clz()(self._ai_buffer, id="ai_output")
        await self.ai_scroll.mount(self.ai_output)

    def action_toggle_history(self):
        if self._hide_history:
            self.main_panel.mount(self.history_tree, before=self.chat_panel)
        else:
            self.history_tree.remove()
        self._hide_history = not self._hide_history

    def action_new_session(self):
        if self._streaming:
            self._stop_streaming()

        if self.current_session and not self.current_session.histories:
            return None

        # 如果存在上一个 session，更新其 title
        if self.sessions and self.current_session:
            old_session = self.current_session
            # 如果有历史记录，用第一个 prompt 的前 10 个字符作为 title
            if old_session.histories:
                first_prompt = old_session.histories[0].prompt
                new_title = (
                    first_prompt[:10] if len(first_prompt) >= 10 else first_prompt
                )
                old_session.title = new_title
                # 更新 tree 中的节点标签
                old_node = self._find_session_node(old_session)
                if old_node:
                    old_node.set_label(new_title)
                    old_node.collapse()

        # 创建新 session，命名为 "New Session"
        session = Session(title="New Session")
        # 插入到列表开头
        self.sessions.insert(0, session)
        self.current_session = session
        self.current_history = None
        self.history_tree.root.expand()

        # 添加到 tree 开头（先添加，然后通过 _children 重新排序）
        node = self.history_tree.root.add(session.title, data=session)
        # 将新节点移到 _children 列表开头
        root_children = self.history_tree.root._children
        if len(root_children) > 1:
            # 将最后一个节点（刚添加的）移到第一个位置
            root_children.insert(0, root_children.pop())

        if self.current_node is not None:
            self.current_node.collapse()
        node.expand()

        self.history_tree.select_node(node)
        self.ai_output.update("")
        self.current_node = node

        # 清空 AI 上下文（新 session 从空白开始）
        if self.ai:
            self.ai.messages = self.ai.get_init_messages()

    def action_edit_config(self):
        def on_config_edited(args):
            if args is not None and callable(self.config_edited_hook):
                self.config_edited_hook(args)

        self.push_screen(ConfigEditor(), on_config_edited)

    def action_noop(self):
        return None


# ================= TUI Renderer =================
class TUIRenderer(BaseRenderer):
    """Interactive Textual-based TUI renderer.

    This renderer provides a full-featured terminal UI with:
    - Session management
    - History browsing
    - Markdown rendering
    - Config editing modal

    Note: TUI mode handles all user input internally, so get_user_input()
    returns None and should not be called.
    """

    def __init__(
        self,
        config_file_path: str,
        history_dir_path: str,
        config_edited_hook,
        history_deleted_hook,
        session_deleted_hook,
        use_markdown: bool = True,
        think_start_emoji: str = "🤔 [Start Thinking]",
        think_end_emoji: str = "💡 [End Thinking]",
        **kwargs,
    ):
        """Initialize TUI renderer.

        Args:
            config_file_path: Path to config file
            history_dir_path: Path to history directory
            config_edited_hook: Callback when config is edited
            history_deleted_hook: Callback when history is deleted
            session_deleted_hook: Callback when session is deleted
            agent: Agent instance (used for AI requests with hooks)
            use_markdown: Whether to use markdown rendering
            **kwargs: Additional arguments (ignored)
        """
        super().__init__(**kwargs)
        self.config_file_path = config_file_path
        self.history_dir_path = history_dir_path
        self.config_edited_hook = config_edited_hook
        self.history_deleted_hook = history_deleted_hook
        self.session_deleted_hook = session_deleted_hook
        self.use_markdown = use_markdown
        self.think_start_emoji = think_start_emoji
        self.think_end_emoji = think_end_emoji

    def render_ai_info(self, model: str) -> None:
        """TUI handles AI info internally."""
        pass

    def render_user_info(self, status: str) -> None:
        """TUI handles user info internally."""
        pass

    def render_user_input(self, user_input: str) -> None:
        """TUI handles user input internally."""
        pass

    def stream_response(self, response, ignore_think: bool) -> str:
        """Stream response (handled internally by TUI)."""
        # TUI handles streaming internally via async app.stream_ai
        # This is called from Agent.ask_ai which needs to be async-aware
        # The actual streaming is done by ChatApp.stream_ai
        return self.app._ai_buffer

    def get_user_input(self, cli_args, need_user_input: bool = True) -> str:
        """TUI handles user input internally - this should not be called."""
        raise NotImplementedError(
            "TUI mode handles user input internally. "
            "Do not call get_user_input() in TUI mode."
        )

    def run(self, ask_ai_async: Callable, ai: BaseAI) -> None:
        """Run the TUI application.

        Args:
            ai: BaseAI instance for AI context management
        """
        self.app = ChatApp(
            config_file_path=self.config_file_path,
            history_file_path=self.history_dir_path,
            config_edited_hook=self.config_edited_hook,
            history_deleted_hook=self.history_deleted_hook,
            session_deleted_hook=self.session_deleted_hook,
            use_markdown=self.use_markdown,
            stream_response=self.stream_response,
            ask_ai_async=ask_ai_async,
            ai=ai,
            think_start_emoji=self.think_start_emoji,
            think_end_emoji=self.think_end_emoji,
        )
        self.app.run()
