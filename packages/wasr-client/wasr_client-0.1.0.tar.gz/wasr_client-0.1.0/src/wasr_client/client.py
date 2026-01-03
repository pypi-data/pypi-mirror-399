from typing import Literal, Optional

from .grpc import get_grpc_result


class ASRClient:
    def __init__(self, task_id: str, env: Literal["test", "ol"] = "ol"):
        self.host = f"{env}-lbg-huangye.wpai.58dns.org:8866"
        self.task_id = task_id
        self.env = env

    def predict(
        self,
        url: Optional[str] = None,
        mono: Optional[bool] = None,
        b64_str: Optional[str] = None,
        hotwords: Optional[str] = None,
    ) -> str:
        assert url is not None or b64_str is not None, "url or b64_str is required"
        inputs = {"url": url}
        if b64_str:
            inputs["b64_str"] = b64_str
        if hotwords:
            inputs["hotwords"] = hotwords
        if mono:
            inputs["mono"] = mono
        return get_grpc_result(inputs=inputs, task_id=self.task_id, env=self.env)

    def batch_predict(self, inputs: list[dict]) -> list[str]:
        return get_grpc_result(inputs=inputs, task_id=self.task_id, env=self.env)