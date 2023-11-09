import json
from functools import cache

from pydantic import BaseModel


class JupyterConfig(BaseModel):
    shell_port: int
    iopub_port: int
    stdin_port: int
    control_port: int
    hb_port: int
    ip: str
    key: str = ""
    transport: str = ""
    signature_scheme: str = ""
    kernel_name: str = ""


class APIConfig(BaseModel):
    client_port: int = 44556
    server_port: int = 44557


class StreamHandlerConfig(BaseModel):
    sender_port: int = 55655
    notifier_port: int = 55656


class Config(BaseModel):
    jupyter: JupyterConfig
    api: APIConfig
    stream: StreamHandlerConfig


@cache
def get_config():
    with open("config.json") as config_file:
        return Config.model_validate(json.load(config_file))
