import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass
class Config:
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    MODEL_NAME: str = "gpt-5-chat"

    @classmethod
    def from_env(cls) -> "Config":
        api_key = os.getenv("OPENAI_API_KEY")
        base = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("MODEL_NAME", cls.MODEL_NAME)
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 未设置；请在 .env 或环境变量中配置")
        if not base:
            raise RuntimeError("OPENAI_BASE_URL 未设置；请在 .env 或环境变量中配置")
        return cls(
            OPENAI_API_KEY=api_key,
            OPENAI_BASE_URL=base,
            MODEL_NAME=model
            )    

def get_config(load_env_file: bool = True) -> Config:
    """
    加载配置
    
    :param load_env_file: 是否加载 .env 文件
    :type load_env_file: bool
    :return: 配置对象
    :rtype: Config
    """
    if load_env_file:
        load_dotenv()
    return Config.from_env()


if __name__ == "__main__":
    cfg = get_config()
    print(cfg)