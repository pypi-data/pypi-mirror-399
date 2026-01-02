import asyncio
import json
from types import SimpleNamespace
from pathlib import Path
from jinja2 import Template
from pydantic import ValidationError
from .models import IntentResult, IntentIO, PythonExecResult, IntentExecHandler
from .runtime import PythonRuntime
from .llm import LLM
from .intent import Intent


def reason(prompt: str, model: type[IntentIO]) -> IntentIO:
    model_schema = model.model_json_schema()
    infer_template_path = Path(__file__).parent / "prompts" / "reason.md"
    infer_template = Template(infer_template_path.read_text())
    infer_prompt = infer_template.render(model_schema=model_schema)

    llm = LLM(system_prompt=infer_prompt)
    max_attempts = 3
    for i in range(max_attempts):
        response = llm.chat(prompt)
        try:
            res = json.loads(response)
        except json.JSONDecodeError as e:
            if i == max_attempts-1:
                raise e
            error_msg = (
                "Your response is not valid JSON. Please output a complete, standard JSON string only.\n"
                f"Parse error: {str(e)}\n"
            )
            prompt = error_msg
            continue
        try:
            validated = model.model_validate(res)
            return validated
        except ValidationError as e:
            if i == max_attempts-1:
                raise e
            error_msg = (
                "The JSON is valid but does not match the required schema.\n"
                f"Validation errors:\n{e}\n"
            )
            prompt = error_msg
            continue


class LLMIntentExecutor:
    def __init__(
        self,
        intent: Intent,
        handler: IntentExecHandler,
        max_iterations: int = 30
    ):
        self._intent = intent
        self.handler = handler
        self._max_iterations = max_iterations

    def _build_system_prompt(self, intent_prompt: str) -> str:
        system_template_path = Path(__file__).parent / "prompts" / "system.md"
        system_template = Template(system_template_path.read_text())
        system_prompt = system_template.render(intent=intent_prompt)
        return system_prompt

    def _build_user_prompt(self, exec_result: PythonExecResult) -> str:
        user_template_path = Path(__file__).parent / "prompts/user.md"
        user_template = Template(user_template_path.read_text())
        user_prompt = user_template.render(
            prints=json.dumps(exec_result.prints, indent=2,
                              ensure_ascii=False),
            error=exec_result.error
        )
        return user_prompt

    async def run(self) -> IntentResult:
        intent_ir = self._intent._build_ir()
        self.handler.on_intent_ir(intent_ir)

        tools = SimpleNamespace(
            **{func.__name__: func for func in self._intent._ctx.funcs})
        runtime = PythonRuntime(
            reason, self._intent._input, tools, self._intent._output)

        system_prompt = self._build_system_prompt(intent_ir)
        self.handler.on_system_prompt(system_prompt)
        user_prompt = "start"
        llm = LLM(system_prompt)
        output = None
        for step in range(self._max_iterations):
            handler_response = self.handler.on_user_prompt(
                step, user_prompt)
            if handler_response:
                code_response = handler_response
            else:
                code_response = llm.chat(user_prompt)
            self.handler.on_code_response(step, code_response)
            exec_result = await runtime.exec(code_response)
            self.handler.on_exec_result(step, exec_result)

            output = runtime.get_output()
            if output:
                self.handler.on_output(step, output)
                break

            user_prompt = self._build_user_prompt(exec_result)
        else:
            e = RuntimeError(
                f"Intent execution failed: no result produced after {self._max_iterations} iterations"
            )
            self.handler.on_failed(e)
            raise e

        if not isinstance(output, IntentIO):
            e = TypeError(
                f"Intent execution failed: invalid output type\n"
                f"Expected: {self._intent._output.__name__}\n"
                f"Got: {type(output).__name__}\n"
                f"Output: {output}"
            )
            self.handler.on_failed(e)
            raise e

        result = IntentResult(output=output)
        self.handler.on_completed(result)
        return result

    def run_sync(self) -> IntentResult:
        return asyncio.run(self.run())
