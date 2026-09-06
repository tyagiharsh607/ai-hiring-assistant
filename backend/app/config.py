from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hunar_api_key: str
    hunar_base_url: str = "https://api.voice.hunar.ai/external/v1"
    hunar_screening_agent_id: str = ""
    hunar_reachout_agent_id: str = ""

    pdl_api_key: str

    public_base_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///./hiring.db"

    class Config:
        env_file = ".env"


settings = Settings()
