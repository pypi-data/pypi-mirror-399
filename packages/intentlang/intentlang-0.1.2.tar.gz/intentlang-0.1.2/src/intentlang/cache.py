import hashlib
import json
from typing import Literal
from pathlib import Path
from typing import Any
from .models import IntentExecHandler, PythonExecResult, IntentIO, IntentResult


class NoteBook:
    def __init__(self, path: Path):
        self._path = path
        if not path.exists():
            self.empty()
        else:
            self._data = json.loads(path.read_text())
            if not self.get_metadata("completed"):
                self.empty()
        self._index = 0

    def empty(self):
        self._data = {
            "cells": [],
            "metadata": {
                "completed": False,
            }
        }
        self._save()

    def _save(self):
        self._path.write_text(json.dumps(
            self._data, indent=2, ensure_ascii=False))

    def get_metadata(self, key: str) -> Any:
        return self._data["metadata"][key]

    def set_metadata(self, key: str, value: Any):
        self._data["metadata"][key] = value
        self._save()

    def add_raw(self, text: str):
        self._data["cells"].append({
            "cell_type": "raw",
            "metadata": {},
            "source": text.splitlines(keepends=True)
        })
        self._save()

    def add_code(self, text: str):
        self._data["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "source": text.splitlines(keepends=True)
        })
        self._save()

    def update_next_raw(self, text: str):
        for i in range(self._index, len(self._data["cells"])):
            cell = self._data["cells"][i]
            if cell["cell_type"] == "raw":
                cell["source"] = text.splitlines(keepends=True)
                self._index = i + 1
                self._save()
                break

    def get_next_code(self) -> str:
        for i in range(self._index, len(self._data["cells"])):
            cell = self._data["cells"][i]
            if cell["cell_type"] == "code":
                self._index = i + 1
                return "".join(cell["source"])
        return "output = 'No more code cells available in cache.'"


class IntentExecCache(IntentExecHandler):
    def __init__(
        self,
        cache_mode: Literal["disable", "update", "reuse"] = "update",
        cache_dir: str = ".intent_cache"
    ):
        self._cache_mode = cache_mode
        self._cache_dir = cache_dir
        self._is_new: bool = False
        self._notebook: NoteBook = None

    def on_intent_ir(self, intent_ir: str):
        intent_ir_hash = hashlib.md5(intent_ir.encode()).hexdigest()[:12]
        self._cache_path = Path(self._cache_dir) / f"{intent_ir_hash}.ipynb"
        if self._cache_mode != "disable":
            Path(self._cache_dir).mkdir(parents=True, exist_ok=True)
            self._notebook = NoteBook(self._cache_path)
            if self._cache_mode == "update" or not self._notebook.get_metadata("completed"):
                self._notebook.empty()
                self._notebook.add_raw(intent_ir)

    def on_user_prompt(self, step: int, user_prompt: str) -> None | str:
        if self._cache_mode != "disable":
            if self._cache_mode == "reuse" and self._notebook.get_metadata("completed"):
                return self._notebook.get_next_code()
        return None

    def on_code_response(self, step: int, code_response: str):
        if self._cache_mode != "disable":
            if self._cache_mode == "update" or not self._notebook.get_metadata("completed"):
                self._notebook.add_code(code_response)

    def on_exec_result(self, step: int, exec_result: PythonExecResult):
        if self._cache_mode != "disable":
            text = exec_result.model_dump_json(indent=2, ensure_ascii=False)
            if self._cache_mode == "update" or not self._notebook.get_metadata("completed"):
                self._notebook.add_raw(text)
            elif self._cache_mode == "reuse":
                self._notebook.update_next_raw(text)

    def on_completed(self, result: IntentResult):
        if self._cache_mode != "disable":
            self._notebook.set_metadata("completed", True)
