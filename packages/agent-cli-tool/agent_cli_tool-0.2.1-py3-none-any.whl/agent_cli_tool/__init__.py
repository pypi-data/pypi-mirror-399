#!/usr/bin/env python3

from .agents import Agent
from .cli import cli_args
from .config import env_config
from .plugins import after_ai_ask, before_ai_ask


def main():
    model = cli_args.model or env_config.get("DEFAULT_MODEL")
    assert model, "AI model is required!"

    agent = Agent(
        cli_args,
        model,
        env_config,
        before_ai_ask_hook=before_ai_ask,
        after_ai_ask_hook=after_ai_ask,
    )
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        from traceback import print_exc

        print_exc()


if __name__ == "__main__":
    main()
