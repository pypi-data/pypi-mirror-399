"""
LLM-powered code agent with:

- Hard global limit of 50 LLM messages
- In-memory conversation history
- Restricted sandbox for executing model-generated Python code
- Self-supervision (critic pass)
- Persistent "tools" that the model can define and call:
    - Tools are saved as separate Python files under ./tools
    - Tools are tracked in state['tools']
- Ability to REQUEST expanded access (filesystem/network/etc.) via a structured action

IMPORTANT SAFETY NOTES
----------------------
- This script itself performs LIMITED file I/O:
    - It creates a ./tools directory.
    - It saves tool code as .py files there.
- Model-generated Python is executed in a restricted sandbox:
    - No file I/O, no network, no OS or shell access.
    - Only a small set of harmless builtins is exposed.
- When the model decides it "needs more power", it uses action "request_access":
    - The agent records this request in an observation and stops.
    - YOU (the human / host app) are responsible for deciding whether and how to grant it.
- You should only give this agent SAFE, LEGAL tasks that don't require real-world side effects.
"""

import json
import os
import traceback
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

os.environ['OPENAI_API_KEY']='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'
"""
Interactive terminal LLM agent with:

- Hard global limit of 50 LLM messages
- In-memory conversation history across turns
- Shared `state` across all user commands
- Restricted sandbox for executing model-generated Python "snippets"
- Self-supervision (critic pass)
- Persistent "tools" that the model can define and call:
    - Tools are saved as separate Python files under ./tools
    - Tools are tracked in state['tools']
- READ-ONLY access to a user-mounted folder (default: C:\\Users\\tyler\\code\\EmbeddingAdapters) via:
    - Action 'list_files' (list files/dirs under a relative path)
    - Action 'open_file' + 'next_file_chunk' to read ENTIRE files in CHUNKS
- WRITE access to an `output` folder inside the mounted repo via:
    - Action 'write_file' (relative path under 'output')
- Ability to EXECUTE Python files in the `output` folder via:
    - Action 'run_python' (runs python on a relative path under output)
    - Captures stdout/stderr/exit code into state['exec']['last_run']
- Ability to REQUEST other expanded access via 'request_access'
- Simple terminal chat loop with color themes, typewriter text, and a spinner:
    - Type natural language tasks to talk to the agent
    - /mount <path>  - change the mounted folder (default is EmbeddingAdapters)
    - /theme <name>  - switch color theme
    - /state         - show current state preview
    - /tools         - list known tools
    - /exit or /quit - leave

You must set OPENAI_API_KEY in your environment for the OpenAI client.

NOTE: Running python files in the `output` folder can do anything normal Python
can do on your machine (network, filesystem, etc.). Review and monitor what
you ask the agent to generate and run.
"""

import json
import os
import sys
import time
import traceback
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from colorama import init as colorama_init, Fore, Style

# =========================
# Terminal themes & helpers
# =========================

colorama_init(autoreset=True)

THEMES: Dict[str, Dict[str, str]] = {
    "cyberpunk": {
        "title": Fore.MAGENTA + Style.BRIGHT,
        "thought": Fore.CYAN,
        "message": Fore.GREEN,
        "system": Fore.YELLOW,
        "error": Fore.RED + Style.BRIGHT,
        "spinner": Fore.MAGENTA,
        "user": Fore.WHITE + Style.BRIGHT,
    },
    "ocean": {
        "title": Fore.BLUE + Style.BRIGHT,
        "thought": Fore.CYAN,
        "message": Fore.GREEN,
        "system": Fore.WHITE,
        "error": Fore.RED + Style.BRIGHT,
        "spinner": Fore.CYAN,
        "user": Fore.WHITE + Style.BRIGHT,
    },
    "mono": {
        "title": Style.BRIGHT,
        "thought": Style.DIM,
        "message": Style.NORMAL,
        "system": Style.NORMAL,
        "error": Fore.RED + Style.BRIGHT,
        "spinner": Style.NORMAL,
        "user": Style.BRIGHT,
    },
}

DEFAULT_THEME = "cyberpunk"

# Default repo path you requested (you can still override with /mount)
DEFAULT_MOUNT = r"C:\Users\tyler\code\EmbeddingAdapters"


# =========================
# LLM CLIENT ABSTRACTION
# =========================

class BaseLLMClient:
    """Minimal interface the Agent expects."""

    def complete(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError


class OpenAIChatClient(BaseLLMClient):
    """
    Implementation using OpenAI's Python SDK.

    - Install: pip install openai
    - Set env var:  export OPENAI_API_KEY="sk-..."
    """

    def __init__(self, model: str = "gpt-4.1-mini"):
        from openai import OpenAI  # type: ignore
        self.client = OpenAI()
        self.model = model

    def complete(self, messages: List[Dict[str, str]]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content


# =========================
# AGENT CONFIG & MEMORY
# =========================

@dataclass
class AgentConfig:
    message_limit: int = 50  # hard cap on LLM calls (including critic)
    max_steps_per_task: int = 50
    tools_dir: str = "tools"
    # output_dir will be joined to mount_root at runtime; keep a relative name
    output_dir_name: str = "output"
    system_prompt: str = field(default_factory=lambda: """
You are a Python-coding assistant running inside a local agent.

CONSTRAINTS:
- You currently CANNOT access the internet, operating system, files, or shell
  directly from your Python *snippets* (the 'code' action).
- You may ONLY use pure Python and the pre-provided variables in your snippets.
- The host may optionally give you:
    - READ-ONLY access to a single mounted folder, via state['fs']['mount_root'].
    - WRITE access to an 'output' folder inside that mounted folder, via
      state['fs']['output_root'].
    - EXECUTION of Python files that live under that 'output' folder, via
      action 'run_python'.
- You do NOT call open() yourself in snippets. Instead, you use special actions
  that the host will fulfill:
    - 'list_files'
    - 'open_file' (start reading a file in chunks)
    - 'next_file_chunk' (get the next chunk of the same file)
    - 'write_file'
    - 'run_python'

FILE CHUNKING MODEL (NO TRUNCATION):
- Files can be arbitrarily large. The host will:
    - On 'open_file':
        * Read the ENTIRE file.
        * Split it into fixed-size CHUNKS internally (not exposed all at once).
        * Store chunks in its own memory.
        * Expose ONLY the FIRST chunk to you via:
              state['fs']['current_file'] = {
                  "path": <relative path>,
                  "chunk_index": 0,
                  "chunk": <string>,
                  "is_last": bool,
                  "total_chunks": int
              }
    - On 'next_file_chunk':
        * Advance to the next chunk for that same file.
        * Update state['fs']['current_file'] with the new chunk and indices.

- You will NEVER see truncated content: you can always walk through all
  chunks until 'is_last' is true.
- YOU are responsible for accumulating any summaries or analyses in the
  `state` as you go. For example:
    * Initialize state['analysis'][<file>] on the first chunk.
    * Update/refine it on each subsequent chunk.
    * Stop when state['fs']['current_file']['is_last'] is true.

PYTHON EXECUTION MODEL:
- You can ask the host to run Python files under the 'output' folder via:
    - action: 'run_python'
    - target_path: RELATIVE path under the 'output' root (e.g. "script.py")
- The host will run 'python <absolute_output_path/target_path>' and capture:
    - stdout
    - stderr
    - exit_code
  and store it under:
    state['exec']['last_run'] = {
        "path": <relative path>,
        "exit_code": int,
        "stdout": <string>,
        "stderr": <string>
    }
- You can then inspect this in subsequent steps (via state_summary) and
  attempt to "fix" the code by editing and rewriting the file via 'write_file'.

OUTPUT FORMAT:
You MUST respond in STRICT JSON with keys:
    - "thought": string
    - "action": one of [
          "code",
          "finish",
          "ask_user",
          "define_tool",
          "call_tool",
          "request_access",
          "list_files",
          "open_file",
          "next_file_chunk",
          "write_file",
          "run_python"
      ]
    - "code": string or null        (Python code to run for 'code' action)
    - "message_to_user": string
    - "tool_name": string or null   (for 'define_tool' / 'call_tool')
    - "tool_code": string or null   (for 'define_tool')
    - "requested_access": list or null      (for 'request_access')
    - "reason_for_access": string or null   (for 'request_access')
    - "target_path": string or null         (for file actions)
    - "file_content": string or null        (for 'write_file')

VALID ACCESS SCOPES for 'requested_access':
- "filesystem_read"
- "filesystem_write"
- "network"
- "shell"
- "external_api:<name>" (e.g. "external_api:github")

FOLDER ACCESS BEHAVIOR:
- When state['fs']['mount_root'] is set by the host, you may:
    - Use action "list_files" with "target_path" as a RELATIVE path
      (e.g. ".", "src", "data/logs").
      The host will return a listing under:
          state['fs']['last_listing'] = {
              "root": <relative path>,
              "entries": [{"name": ..., "is_dir": bool}, ...]
          }
    - Use "open_file" then repeated "next_file_chunk" to read ENTIRE files.
      Current chunk is always in state['fs']['current_file']['chunk'].

OUTPUT FOLDER BEHAVIOR:
- When state['fs']['output_root'] is set by the host, you may:
    - Use action "write_file" with:
        - "target_path": RELATIVE path under the output root (e.g. "report.md")
        - "file_content": the text content to write
      The host will store:
          state['fs']['last_written'] = {
              "path": <relative path>,
              "length": int,
          }

PYTHON RUN BEHAVIOR:
- When state['fs']['output_root'] is set, you may:
    - Use action "run_python" with:
        - "target_path": RELATIVE path under the output root (e.g. "script.py")
      The host will run the file with Python and store:
          state['exec']['last_run'] = {
              "path": <relative path>,
              "exit_code": int,
              "stdout": <string>,
              "stderr": <string>
          }

TOOL BEHAVIOR:
- When you want to create a reusable TOOL:
    - "action": "define_tool"
    - "tool_name": short snake_case identifier
    - "tool_code": full Python source for a module
    - The tool MUST define:

        def run_tool(state: dict) -> dict:
            \"\"\"Read and update the state dict; return the updated state.\"\"\"
            ...

    - Tool code MUST NOT do file I/O, networking, OS calls, or shell calls.
- When you want to call an existing TOOL:
    - "action": "call_tool"
    - Set "tool_name" to the name of a tool previously defined and registered
      in state['tools'].
    - "code": null.

GENERAL:
- Think step-by-step in "thought".
- Use the `state` dict (already defined) as your working memory. You may read and
  modify it in your code.
- When you want to run one-off code:
    - "action": "code"
    - Put Python in "code"
    - Your code MUST NOT attempt I/O or networking.
- When the overall task is done:
    - "action": "finish"
- When you need clarification from the user:
    - "action": "ask_user"
    - Put your question in "message_to_user"
- When you believe you need more capabilities:
    - "action": "request_access"
    - Set "requested_access" and "reason_for_access".
- Never generate shell commands, file I/O, or network calls in ANY snippet.
- Keep code small and focused on the next subtask.
""".strip())


@dataclass
class AgentMemory:
    """Simple in-memory conversational history."""
    messages: List[Dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def trimmed(self, limit: int) -> List[Dict[str, str]]:
        if len(self.messages) <= limit:
            return list(self.messages)
        return self.messages[-limit:]


# =========================
# AGENT IMPLEMENTATION
# =========================

class CodeAgent:
    def __init__(
        self,
        llm: BaseLLMClient,
        config: Optional[AgentConfig] = None,
        theme_name: str = DEFAULT_THEME,
    ):
        self.llm = llm
        self.config = config or AgentConfig()
        self.memory = AgentMemory()
        self.total_messages = 0  # counts LLM calls

        # Ensure tools directory exists (output dir is per-mount)
        os.makedirs(self.config.tools_dir, exist_ok=True)

        # File chunk store (not in state; only current chunk goes into state)
        # rel_path -> {"chunks": [...], "index": int}
        self.file_store: Dict[str, Dict[str, Any]] = {}

        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

    # ---------- Theme & UI helpers ----------

    def set_theme(self, name: str) -> bool:
        """Change color theme; returns True if applied."""
        name = name.lower()
        if name in THEMES:
            self.theme_name = name
            self.theme = THEMES[name]
            return True
        return False

    def _color(self, key: str) -> str:
        return self.theme.get(key, "")

    def _section_title(self, title: str) -> None:
        color = self._color("title")
        bar = "-" * len(title)
        print(color + title + Style.RESET_ALL)
        print(color + bar + Style.RESET_ALL)

    def _print_animated(self, text: str, key: str = "message", prefix: str = "") -> None:
        color = self._color(key)
        full = f"{color}{prefix}{text}{Style.RESET_ALL}"
        for ch in full:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.003)  # subtle typewriter effect
        print()

    def _spinner(self, label: str = "Working", cycles: int = 8, delay: float = 0.05) -> None:
        """Tiny spinner animation (just for vibes)."""
        color = self._color("spinner")
        frames = "|/-\\"
        for i in range(cycles):
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r{color}{label} {frame}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(delay)
        # clear line
        sys.stdout.write("\r" + " " * (len(label) + 4) + "\r")
        sys.stdout.flush()

    # ---------- Sandbox for snippets ----------

    def _safe_exec(self, code: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute model-generated Python snippet in a restricted environment.

        - No direct access to builtins except a small whitelist.
        - state: a dict shared across steps (self-"modification").
        """
        allowed_builtins = {
            "print": print,
            "range": range,
            "len": len,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "any": any,
            "all": all,
        }

        safe_globals = {
            "__builtins__": allowed_builtins,
        }

        safe_locals = {
            "state": state,
        }

        try:
            exec(code, safe_globals, safe_locals)
            return {
                "ok": True,
                "state": state,
                "error": None,
            }
        except Exception:
            return {
                "ok": False,
                "state": state,
                "error": traceback.format_exc(),
            }

    def _run_tool_code(self, tool_code: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the body of a tool (its Python source) in the same restricted sandbox.
        """
        wrapper_code = f"""
{tool_code}

# Call run_tool(state) defined above
state.update(run_tool(state))
"""
        return self._safe_exec(wrapper_code, state)

    # ---------- Filesystem helpers (host side) ----------

    @staticmethod
    def _safe_join(root: str, rel_path: str) -> Optional[str]:
        """
        Join root and rel_path safely, ensuring the result stays inside root.
        Returns absolute path or None if it would escape root.
        """
        if not rel_path:
            rel_path = "."
        root_real = os.path.realpath(root)
        target_real = os.path.realpath(os.path.join(root_real, rel_path))
        if os.path.commonpath([root_real, target_real]) != root_real:
            return None
        return target_real

    def _list_files(self, state: Dict[str, Any], rel_path: str) -> Dict[str, Any]:
        """
        List files/dirs under the mounted root at a relative path.
        Stores result in state['fs']['last_listing'].
        """
        fs = state.setdefault("fs", {})
        mount_root = fs.get("mount_root")
        if not mount_root:
            return {
                "ok": False,
                "error": "No mount_root set in state['fs']; cannot list files.",
            }

        target = self._safe_join(mount_root, rel_path)
        if target is None:
            return {
                "ok": False,
                "error": "Requested path escapes mounted root; denied.",
            }

        if not os.path.isdir(target):
            return {
                "ok": False,
                "error": f"Path is not a directory: {rel_path}",
            }

        try:
            entries = []
            for name in os.listdir(target):
                full = os.path.join(target, name)
                entries.append(
                    {
                        "name": name,
                        "is_dir": os.path.isdir(full),
                    }
                )

            fs["last_listing"] = {
                "root": rel_path,
                "entries": entries,
            }
            return {
                "ok": True,
                "error": None,
                "entries": entries,
            }
        except Exception:
            return {
                "ok": False,
                "error": traceback.format_exc(),
            }

    def _open_file_chunks(self, state: Dict[str, Any], rel_path: str, chunk_size: int = 8000) -> Dict[str, Any]:
        """
        Read entire file and split into chunks stored in self.file_store.
        Expose only the first chunk in state['fs']['current_file'].
        """
        fs = state.setdefault("fs", {})
        mount_root = fs.get("mount_root")
        if not mount_root:
            return {
                "ok": False,
                "error": "No mount_root set in state['fs']; cannot open files.",
            }

        target = self._safe_join(mount_root, rel_path)
        if target is None:
            return {
                "ok": False,
                "error": "Requested path escapes mounted root; denied.",
            }

        if not os.path.isfile(target):
            return {
                "ok": False,
                "error": f"Path is not a file: {rel_path}",
            }

        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if not content:
                chunks = [""]
            else:
                chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

            self.file_store[rel_path] = {
                "chunks": chunks,
                "index": 0,
            }

            current_chunk = chunks[0]
            total = len(chunks)
            fs["current_file"] = {
                "path": rel_path,
                "chunk_index": 0,
                "chunk": current_chunk,
                "is_last": (total == 1),
                "total_chunks": total,
            }

            return {
                "ok": True,
                "error": None,
                "chunk_index": 0,
                "total_chunks": total,
            }
        except Exception:
            return {
                "ok": False,
                "error": traceback.format_exc(),
            }

    def _next_file_chunk(self, state: Dict[str, Any], rel_path: str) -> Dict[str, Any]:
        """
        Advance to the next chunk for the given file, if any.
        Updates state['fs']['current_file'].
        """
        fs = state.setdefault("fs", {})
        store = self.file_store.get(rel_path)
        if not store:
            return {
                "ok": False,
                "error": f"File '{rel_path}' is not open. Use 'open_file' first.",
            }

        chunks = store["chunks"]
        index = store["index"]
        total = len(chunks)

        if index + 1 >= total:
            # already at last chunk; keep pointing at last
            fs["current_file"] = {
                "path": rel_path,
                "chunk_index": index,
                "chunk": chunks[index],
                "is_last": True,
                "total_chunks": total,
            }
            return {
                "ok": True,
                "error": None,
                "chunk_index": index,
                "is_last": True,
                "total_chunks": total,
            }

        index += 1
        store["index"] = index
        fs["current_file"] = {
            "path": rel_path,
            "chunk_index": index,
            "chunk": chunks[index],
            "is_last": (index == total - 1),
            "total_chunks": total,
        }
        return {
            "ok": True,
            "error": None,
            "chunk_index": index,
            "is_last": (index == total - 1),
            "total_chunks": total,
        }

    def _write_file(self, state: Dict[str, Any], rel_path: str, content: str) -> Dict[str, Any]:
        """
        Write a file under the dedicated output root at a relative path.
        Stores result in state['fs']['last_written'].
        """
        fs = state.setdefault("fs", {})
        output_root = fs.get("output_root")
        if not output_root:
            return {
                "ok": False,
                "error": "No output_root set in state['fs']; cannot write files.",
            }

        target = self._safe_join(output_root, rel_path)
        if target is None:
            return {
                "ok": False,
                "error": "Requested path escapes output root; denied.",
            }

        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)
            fs["last_written"] = {
                "path": rel_path,
                "length": len(content),
            }
            return {
                "ok": True,
                "error": None,
            }
        except Exception:
            return {
                "ok": False,
                "error": traceback.format_exc(),
            }

    def _run_python_file(self, state: Dict[str, Any], rel_path: str) -> Dict[str, Any]:
        """
        Run a Python file under the output root with the system Python.
        Stores result in state['exec']['last_run'].
        """
        fs = state.setdefault("fs", {})
        exec_state = state.setdefault("exec", {})
        output_root = fs.get("output_root")
        if not output_root:
            return {
                "ok": False,
                "error": "No output_root set in state['fs']; cannot run Python files.",
            }

        target = self._safe_join(output_root, rel_path)
        if target is None:
            return {
                "ok": False,
                "error": "Requested path escapes output root; denied.",
            }

        if not os.path.isfile(target):
            return {
                "ok": False,
                "error": f"Path is not a file: {rel_path}",
            }

        try:
            # Run python <target> and capture output
            proc = subprocess.run(
                [sys.executable, target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            exec_state["last_run"] = {
                "path": rel_path,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
            return {
                "ok": True,
                "error": None,
                "exit_code": proc.returncode,
            }
        except Exception:
            return {
                "ok": False,
                "error": traceback.format_exc(),
            }

    # ---------- LLM messaging ----------

    def _call_llm(self, task: str, state: Dict[str, Any], step: int) -> Dict[str, Any]:
        """
        Ask the model what to do next. Enforce strict JSON interface.
        """
        user_payload = {
            "task": task,
            "step": step,
            "state_summary": repr(state),
            "instruction": (
                "Decide the next action. "
                "Remember to return STRICT JSON as described in the system prompt."
            ),
        }
        user_prompt = {
            "role": "user",
            "content": json.dumps(user_payload, indent=2),
        }

        messages = [{"role": "system", "content": self.config.system_prompt}]
        messages.extend(self.memory.trimmed(self.config.message_limit - 2))
        messages.append(user_prompt)

        raw = self.llm.complete(messages)
        self.total_messages += 1

        self.memory.add("assistant", raw)

        try:
            parsed = json.loads(raw)

            parsed.setdefault("code", None)
            parsed.setdefault("tool_name", None)
            parsed.setdefault("tool_code", None)
            parsed.setdefault("message_to_user", "")
            parsed.setdefault("thought", "")
            parsed.setdefault("action", "finish")
            parsed.setdefault("requested_access", None)
            parsed.setdefault("reason_for_access", None)
            parsed.setdefault("target_path", None)
            parsed.setdefault("file_content", None)

            return parsed
        except Exception:
            return {
                "thought": "Failed to produce valid JSON; treating entire reply as message_to_user.",
                "action": "finish",
                "code": None,
                "tool_name": None,
                "tool_code": None,
                "message_to_user": raw,
                "requested_access": None,
                "reason_for_access": None,
                "target_path": None,
                "file_content": None,
            }

    def _critic_pass(self, task: str, last_step_info: Dict[str, Any]) -> str:
        """
        Simple self-supervision: ask the model to critique the previous step.
        """
        critic_payload = {
            "mode": "critic",
            "task": task,
            "last_step": last_step_info,
            "instruction": (
                "Briefly critique the previous step in <= 5 bullet points. "
                "Focus on correctness, safety, and suggested next improvement."
            ),
        }
        critic_prompt = {
            "role": "user",
            "content": json.dumps(critic_payload, indent=2),
        }

        messages = [
            {
                "role": "system",
                "content": "You are a strict critic analyzing the previous step of an agent.",
            }
        ]
        messages.extend(self.memory.trimmed(self.config.message_limit - 2))
        messages.append(critic_prompt)

        critique = self.llm.complete(messages)
        self.total_messages += 1
        self.memory.add("assistant", f"[CRITIC]\n{critique}")
        return critique

    # ---------- Public API ----------

    def run_task(
        self,
        task: str,
        max_steps: Optional[int] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        self_supervise: bool = True,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a single high-level task.

        Returns final `state` dict (including known tools).
        """
        if self.total_messages >= self.config.message_limit:
            print(self._color("error") + "[Agent] Global message limit reached, cannot run more tasks." + Style.RESET_ALL)
            return initial_state or {}

        state: Dict[str, Any] = initial_state or {}
        state.setdefault("tools", {})
        fs = state.setdefault("fs", {})
        # mount_root may already be set; if not, default to your repo
        if not fs.get("mount_root"):
            fs["mount_root"] = os.path.abspath(DEFAULT_MOUNT)
        # output_root is <mount_root>/output
        fs["output_root"] = os.path.join(fs["mount_root"], self.config.output_dir_name)
        os.makedirs(fs["output_root"], exist_ok=True)
        fs.setdefault("current_file", None)
        exec_state = state.setdefault("exec", {})

        step_limit = min(
            max_steps or self.config.max_steps_per_task,
            self.config.max_steps_per_task,
        )

        self.memory.add("user", f"[NEW TASK] {task}")

        for step in range(step_limit):
            if self.total_messages >= self.config.message_limit:
                if verbose:
                    print(self._color("error") + "\n[Agent] Global message limit reached, stopping." + Style.RESET_ALL)
                break

            if verbose:
                self._section_title(f"STEP {step + 1}")

            reply = self._call_llm(task, state, step)

            if verbose:
                self._spinner("Thinking")
                self._print_animated(reply.get("thought", ""), "thought", prefix="[Thought] ")
                self._print_animated(reply.get("message_to_user", ""), "message", prefix="[Message] ")

            action = reply.get("action")
            code = reply.get("code")
            tool_name = reply.get("tool_name")
            tool_code = reply.get("tool_code")
            requested_access = reply.get("requested_access")
            reason_for_access = reply.get("reason_for_access")
            target_path = reply.get("target_path") or "."
            file_content = reply.get("file_content") or ""

            if action == "finish":
                if verbose:
                    self._print_animated("Model chose to FINISH.", "system", prefix="[Agent] ")
                break

            elif action == "ask_user":
                if verbose:
                    self._print_animated("Agent wants to ask you something and pause.", "system", prefix="[Agent] ")
                self.memory.add("assistant", f"[QUESTION_TO_USER] {reply.get('message_to_user', '')}")
                break

            elif action == "code":
                if not code:
                    if verbose:
                        self._print_animated("No code provided despite action='code'. Stopping.", "error", prefix="[Agent] ")
                    break

                if verbose:
                    self._section_title("Executing snippet")
                    print(self._color("system") + code + Style.RESET_ALL)

                exec_result = self._safe_exec(code, state)
                state = exec_result["state"]

                observation = {
                    "type": "code",
                    "ok": exec_result["ok"],
                    "error": exec_result["error"],
                    "state_preview": repr(state)[:500],
                }

                if verbose:
                    if exec_result["ok"]:
                        self._print_animated("Snippet ran successfully.", "system", prefix="[Exec] ")
                    else:
                        self._print_animated("Snippet raised an error:", "error", prefix="[Exec] ")
                        print(self._color("error") + (exec_result["error"] or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "define_tool":
                if not tool_name or not tool_code:
                    if verbose:
                        self._print_animated("Missing tool_name or tool_code for define_tool. Stopping.", "error", prefix="[Agent] ")
                    break

                safe_name = "".join(ch for ch in tool_name if (ch.isalnum() or ch in "_-")) or "tool"
                file_path = os.path.join(self.config.tools_dir, f"{safe_name}.py")

                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(tool_code)

                    state["tools"][tool_name] = {
                        "path": file_path,
                        "code": tool_code,
                        "description": reply.get("message_to_user", ""),
                    }

                    observation = {
                        "type": "define_tool",
                        "tool_name": tool_name,
                        "path": file_path,
                        "ok": True,
                        "state_tools": list(state["tools"].keys()),
                    }
                    if verbose:
                        self._print_animated(f"Tool defined: {tool_name} -> {file_path}", "system", prefix="[Tool] ")

                except Exception:
                    err = traceback.format_exc()
                    observation = {
                        "type": "define_tool",
                        "tool_name": tool_name,
                        "ok": False,
                        "error": err,
                    }
                    if verbose:
                        self._print_animated("Tool definition FAILED:", "error", prefix="[Tool] ")
                        print(self._color("error") + err + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "call_tool":
                if not tool_name:
                    if verbose:
                        self._print_animated("Missing tool_name for call_tool. Stopping.", "error", prefix="[Agent] ")
                    break

                tool_info = state["tools"].get(tool_name)
                if not tool_info:
                    observation = {
                        "type": "call_tool",
                        "tool_name": tool_name,
                        "ok": False,
                        "error": f"Tool '{tool_name}' not found in state['tools'].",
                    }
                    if verbose:
                        self._print_animated(f"Tool '{tool_name}' not known.", "error", prefix="[Tool] ")
                    self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")
                    break

                if verbose:
                    self._print_animated(f"Calling tool: {tool_name}", "system", prefix="[Tool] ")

                exec_result = self._run_tool_code(tool_info["code"], state)
                state = exec_result["state"]

                observation = {
                    "type": "call_tool",
                    "tool_name": tool_name,
                    "ok": exec_result["ok"],
                    "error": exec_result["error"],
                    "state_preview": repr(state)[:500],
                }

                if verbose:
                    if exec_result["ok"]:
                        self._print_animated("Tool executed successfully.", "system", prefix="[Tool] ")
                    else:
                        self._print_animated("Tool raised an error:", "error", prefix="[Tool] ")
                        print(self._color("error") + (exec_result["error"] or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "request_access":
                observation = {
                    "type": "request_access",
                    "requested_access": requested_access,
                    "reason_for_access": reason_for_access,
                    "granted": False,  # demo never auto-grants
                }

                if verbose:
                    self._print_animated("Access request:", "system", prefix="[Agent] ")
                    print(self._color("system") + f"  requested_access = {requested_access}" + Style.RESET_ALL)
                    print(self._color("system") + f"  reason          = {reason_for_access}" + Style.RESET_ALL)
                    self._print_animated("Currently NOT granted (demo is locked down).", "error", prefix="[Agent] ")

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

                break

            elif action == "list_files":
                if verbose:
                    self._print_animated(f"Listing files at: {target_path!r}", "system", prefix="[FS] ")

                fs_result = self._list_files(state, target_path)
                observation = {
                    "type": "list_files",
                    "target_path": target_path,
                    "ok": fs_result["ok"],
                    "error": fs_result.get("error"),
                }

                if verbose:
                    if fs_result["ok"]:
                        self._print_animated("Entries stored in state['fs']['last_listing'].", "system", prefix="[FS] ")
                    else:
                        self._print_animated("Listing error:", "error", prefix="[FS] ")
                        print(self._color("error") + (fs_result.get("error") or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "open_file":
                if verbose:
                    self._print_animated(f"Opening file: {target_path!r}", "system", prefix="[FS] ")

                fs_result = self._open_file_chunks(state, target_path)
                observation = {
                    "type": "open_file",
                    "target_path": target_path,
                    "ok": fs_result["ok"],
                    "error": fs_result.get("error"),
                    "chunk_index": fs_result.get("chunk_index"),
                    "total_chunks": fs_result.get("total_chunks"),
                }

                if verbose:
                    if fs_result["ok"]:
                        self._print_animated("First chunk stored in state['fs']['current_file'].", "system", prefix="[FS] ")
                    else:
                        self._print_animated("Open file error:", "error", prefix="[FS] ")
                        print(self._color("error") + (fs_result.get("error") or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "next_file_chunk":
                if verbose:
                    self._print_animated(f"Requesting next chunk for: {target_path!r}", "system", prefix="[FS] ")

                fs_result = self._next_file_chunk(state, target_path)
                observation = {
                    "type": "next_file_chunk",
                    "target_path": target_path,
                    "ok": fs_result["ok"],
                    "error": fs_result.get("error"),
                    "chunk_index": fs_result.get("chunk_index"),
                    "is_last": fs_result.get("is_last"),
                    "total_chunks": fs_result.get("total_chunks"),
                }

                if verbose:
                    if fs_result["ok"]:
                        self._print_animated(
                            f"Chunk {fs_result.get('chunk_index')} / {fs_result.get('total_chunks') - 1} now in state['fs']['current_file'].",
                            "system",
                            prefix="[FS] ",
                        )
                    else:
                        self._print_animated("Next chunk error:", "error", prefix="[FS] ")
                        print(self._color("error") + (fs_result.get("error") or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "write_file":
                if verbose:
                    self._print_animated(f"Writing file: {target_path!r}", "system", prefix="[FS] ")

                fs_result = self._write_file(state, target_path, file_content)
                observation = {
                    "type": "write_file",
                    "target_path": target_path,
                    "ok": fs_result["ok"],
                    "error": fs_result.get("error"),
                }

                if verbose:
                    if fs_result["ok"]:
                        self._print_animated("File written under output folder.", "system", prefix="[FS] ")
                    else:
                        self._print_animated("Write error:", "error", prefix="[FS] ")
                        print(self._color("error") + (fs_result.get("error") or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            elif action == "run_python":
                if verbose:
                    self._print_animated(f"Running Python file: {target_path!r}", "system", prefix="[Exec] ")

                fs_result = self._run_python_file(state, target_path)
                observation = {
                    "type": "run_python",
                    "target_path": target_path,
                    "ok": fs_result["ok"],
                    "error": fs_result.get("error"),
                    "exit_code": fs_result.get("exit_code"),
                }

                if verbose:
                    if fs_result["ok"]:
                        last_run = exec_state.get("last_run", {})
                        self._print_animated(
                            f"Python exited with code {last_run.get('exit_code')}.\n[stdout]:",
                            "system",
                            prefix="[Exec] ",
                        )
                        print(self._color("system") + (last_run.get("stdout") or "") + Style.RESET_ALL)
                        if last_run.get("stderr"):
                            print(self._color("error") + "[stderr]:" + Style.RESET_ALL)
                            print(self._color("error") + last_run["stderr"] + Style.RESET_ALL)
                    else:
                        self._print_animated("Run error:", "error", prefix="[Exec] ")
                        print(self._color("error") + (fs_result.get("error") or "") + Style.RESET_ALL)

                self.memory.add("user", f"[OBSERVATION] {json.dumps(observation, indent=2)}")

                if self_supervise and self.total_messages < self.config.message_limit:
                    last_step_info = {"step": step, "reply": reply, "observation": observation}
                    critique = self._critic_pass(task, last_step_info)
                    if verbose:
                        self._section_title("Critic")
                        print(self._color("system") + critique + Style.RESET_ALL)

            else:
                if verbose:
                    self._print_animated(f"Unknown action '{action}', stopping.", "error", prefix="[Agent] ")
                break

        if verbose:
            preview = repr(state)[:300]
            self._print_animated(f"Final state preview: {preview}", "system", prefix="[Agent] ")

        return state


# =========================
# SIMPLE TERMINAL INTERFACE
# =========================

def main():
    llm_client = OpenAIChatClient(model="gpt-4.1-mini")
    agent = CodeAgent(llm_client, theme_name=DEFAULT_THEME)

    shared_state: Dict[str, Any] = {}

    # Intro
    theme = THEMES[agent.theme_name]
    print(theme["title"] + "Interactive Agent CLI" + Style.RESET_ALL)
    print(theme["title"] + "---------------------" + Style.RESET_ALL)
    print(theme["system"] + f"Default mount: {DEFAULT_MOUNT}" + Style.RESET_ALL)
    print(theme["system"] + "Commands:" + Style.RESET_ALL)
    print(theme["system"] + "  Type any task to run it." + Style.RESET_ALL)
    print(theme["system"] + "  /mount <path>  - change the read-only folder (agent output still goes to <path>/output)" + Style.RESET_ALL)
    print(theme["system"] + "  /theme <name>  - switch color theme (cyberpunk, ocean, mono)" + Style.RESET_ALL)
    print(theme["system"] + "  /state         - show current state preview" + Style.RESET_ALL)
    print(theme["system"] + "  /tools         - list known tools" + Style.RESET_ALL)
    print(theme["system"] + "  /exit or /quit - leave" + Style.RESET_ALL)
    print()

    while True:
        try:
            user_input = input(theme["user"] + "You: " + Style.RESET_ALL).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + theme["system"] + "Exiting." + Style.RESET_ALL)
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit"):
            print(theme["system"] + "Bye." + Style.RESET_ALL)
            break

        if user_input.lower().startswith("/mount "):
            path = user_input[len("/mount "):].strip()
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                print(theme["error"] + f"[Error] Not a directory: {path}" + Style.RESET_ALL)
                continue
            fs = shared_state.setdefault("fs", {})
            fs["mount_root"] = path
            fs["output_root"] = os.path.join(path, agent.config.output_dir_name)
            os.makedirs(fs["output_root"], exist_ok=True)
            print(theme["system"] + f"[Mounted] Read-only folder set to: {path}" + Style.RESET_ALL)
            print(theme["system"] + f"[Output ] Writing to: {fs['output_root']}" + Style.RESET_ALL)
            continue

        if user_input.lower().startswith("/theme"):
            parts = user_input.split(maxsplit=1)
            if len(parts) == 1:
                print(theme["system"] + f"Available themes: {', '.join(THEMES.keys())}" + Style.RESET_ALL)
                print(theme["system"] + f"Current theme: {agent.theme_name}" + Style.RESET_ALL)
            else:
                name = parts[1].strip().lower()
                if agent.set_theme(name):
                    theme = THEMES[agent.theme_name]
                    print(theme["system"] + f"Theme set to: {agent.theme_name}" + Style.RESET_ALL)
                else:
                    print(theme["error"] + f"Unknown theme: {name}" + Style.RESET_ALL)
            continue

        if user_input.lower() == "/state":
            print()
            print(theme["system"] + "[STATE]" + Style.RESET_ALL)
            print(theme["system"] + repr(shared_state)[:2000] + Style.RESET_ALL)
            print()
            continue

        if user_input.lower() == "/tools":
            tools = list(shared_state.get("tools", {}).keys())
            print()
            print(theme["system"] + "[TOOLS]" + Style.RESET_ALL)
            print(theme["system"] + f"Known tools: {tools}" + Style.RESET_ALL)
            print()
            continue

        # Normal task: talk to the agent.
        shared_state = agent.run_task(
            task=user_input,
            max_steps=5,            # per-turn limit so we don't burn 50 in one go
            initial_state=shared_state,
            self_supervise=True,
            verbose=True,
        )

        if agent.total_messages >= agent.config.message_limit:
            print(theme["error"] + "\n[Agent] Global message limit reached (50). Restart the script for a fresh session." + Style.RESET_ALL)
            break


if __name__ == "__main__":
    main()
