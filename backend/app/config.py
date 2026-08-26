"""
Central application configuration.

All values are read from environment variables (or a .env file in the
backend/ directory). Nothing sensitive is hard-coded here.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    # Database
    DB_MODE: str = "sqlite"  # "sqlite" or "mssql"
    SQLITE_PATH: str = "./customer_db.sqlite3"

    MSSQL_SERVER: str = "localhost"
    MSSQL_PORT: str = ""  # Empty for named instances like localhost\SQLEXPRESS
    MSSQL_DATABASE: str = "Customer_DB"
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    MSSQL_ENCRYPT: str = "yes"
    MSSQL_TRUST_SERVER_CERT: str = "yes"

    # Auth
    JWT_SECRET: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_ENABLED: bool = True
    OLLAMA_TIMEOUT_SECONDS: int = 20

    # Company contact (empty string == "not configured")
    COMPANY_WHATSAPP_NUMBER: str = ""
    COMPANY_SUPPORT_EMAIL: str = ""
    COMPANY_SUPPORT_PHONE: str = ""

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DB_MODE == "mssql":
            from urllib.parse import quote_plus
            driver = self.MSSQL_DRIVER.replace(" ", "+")
            # Build server string - include port only if specified
            server_str = self.MSSQL_SERVER
            if self.MSSQL_PORT:
                server_str = f"{self.MSSQL_SERVER}:{self.MSSQL_PORT}"
            
            # Use Windows Authentication if user/password are empty
            if not self.MSSQL_USER or not self.MSSQL_PASSWORD:
                return (
                    f"mssql+pyodbc://@{server_str}/{self.MSSQL_DATABASE}"
                    f"?driver={driver}"
                    f"&Trusted_Connection=yes"
                    f"&Encrypt={self.MSSQL_ENCRYPT}"
                    f"&TrustServerCertificate={self.MSSQL_TRUST_SERVER_CERT}"
                    f"&Connection+Timeout=10"
                )
            else:
                # URL-encode username and password to handle special characters
                user_encoded = quote_plus(self.MSSQL_USER)
                password_encoded = quote_plus(self.MSSQL_PASSWORD)
                return (
                    f"mssql+pyodbc://{user_encoded}:{password_encoded}"
                    f"@{server_str}/{self.MSSQL_DATABASE}"
                    f"?driver={driver}"
                    f"&Encrypt={self.MSSQL_ENCRYPT}"
                    f"&TrustServerCertificate={self.MSSQL_TRUST_SERVER_CERT}"
                    f"&Connection+Timeout=10"
                )
        return f"sqlite:///{self.SQLITE_PATH}"


def get_company_email() -> str:
    """
    Dynamically fetch company email from .env file at runtime.
    This allows changes to the .env file to be reflected immediately
    without restarting the backend.
    """
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return os.getenv("COMPANY_SUPPORT_EMAIL", "")


def get_company_phone() -> str:
    """
    Dynamically fetch company phone from .env file at runtime.
    """
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return os.getenv("COMPANY_SUPPORT_PHONE", "")


def get_company_whatsapp() -> str:
    """
    Dynamically fetch company WhatsApp from .env file at runtime.
    """
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return os.getenv("COMPANY_WHATSAPP_NUMBER", "")


settings = Settings()
