import ast
import traceback
from types import SimpleNamespace
from typing import Type, Any, Dict, Callable
from .models import PythonExecResult, IntentIO


class PythonRuntime:
    def __init__(self, reason: Callable, input: IntentIO, tools: SimpleNamespace, output: Type[IntentIO]):
        self._prints: list[str] = []
        self._globals: Dict[str, Any] = {
            "__builtins__": __builtins__,
            "print": lambda *args, **kwargs: self._prints.append(" ".join(str(a) for a in args)),
            "IntentIO": IntentIO,
            "reason": reason,
            "input": input,
            "tools": tools,
            "OutputModel": output,
            "output": None
        }

    async def exec(self, source: str) -> PythonExecResult:
        error = "None"
        try:
            code = compile(
                source=source,
                filename="<runtime>",
                mode="exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            coro = eval(code, self._globals)
            if coro is not None:
                await coro
        except Exception:
            tb = traceback.format_exc()
            error = tb[tb.find('File "<runtime>"'):]
        return PythonExecResult(prints=self._get_prints(), error=error)

    def _get_prints(self) -> list[str]:
        prints = self._prints.copy()
        self._prints.clear()
        return prints

    def get_output(self) -> IntentIO:
        result = self._globals["output"]
        return result
