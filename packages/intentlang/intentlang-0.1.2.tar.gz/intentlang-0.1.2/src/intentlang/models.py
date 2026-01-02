from abc import ABC, abstractmethod
from typing import Callable
from pydantic import BaseModel, ConfigDict


class ContextSpace(BaseModel):
    texts: list[str] = []
    funcs: list[Callable] = []


class IntentIO(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RuleList(BaseModel):
    texts: list[str] = []


class PythonExecResult(BaseModel):
    prints: list[str] = []
    error: str = ""


class IntentResult(BaseModel):
    output: IntentIO


class IntentExecutor(ABC):
    @abstractmethod
    async def run(self) -> IntentResult:
        pass

    @abstractmethod
    def run_sync(self) -> IntentResult:
        pass


class IntentExecHandler(ABC):
    def on_intent_ir(self, intent_ir: str):
        return

    def on_system_prompt(self, system_prompt: str):
        return

    def on_user_prompt(self, step: int, user_prompt: str) -> None | str:
        return None

    def on_code_response(self, step: int, code_response: str):
        return

    def on_exec_result(self, step: int, exec_result: PythonExecResult):
        return

    def on_output(self, step: int, output: IntentIO):
        return

    def on_failed(self, error: Exception):
        return

    def on_completed(self, result: IntentResult):
        return
