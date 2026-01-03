from enum import StrEnum

from pydantic_settings import BaseSettings, CliPositionalArg

from webquest_mcp.main import main as serve_main
from webquest_mcp.token_generator import main as token_main


class Command(StrEnum):
    SERVE = "serve"
    TOKEN = "token"


class Settings(BaseSettings, cli_parse_args=True):
    command: CliPositionalArg[Command] = Command.SERVE


def main() -> None:
    settings = Settings()

    if settings.command is Command.SERVE:
        serve_main()
        return

    if settings.command is Command.TOKEN:
        token_main()
        return


if __name__ == "__main__":
    main()
