import hashlib
from typing import Callable

from pydantic import BaseModel


class HTMLFile(BaseModel):
    abs_file_path: str

    def __init__(self, abs_file_path: str):
        # custom init to allow positional argument for the file path
        super().__init__(abs_file_path=abs_file_path)


class RegisteredMethod(BaseModel):
    tag_id: str
    func: Callable[[], str]
    interval: int
    html_file: HTMLFile

    def signature(self) -> str:
        signature = (
            f"{self.html_file.abs_file_path};;;{self.tag_id};;;{self.func.__name__}"
        )
        hash = hashlib.new("sha256")
        hash.update(signature.encode())
        return hash.hexdigest()
