import argparse
import sys

import g4f
from g4f.Provider.retry_provider import RetryProvider
from colorama import Fore, Style

import monkey_patch

monkey_patch.patch_rich()
from rich.live import Live
from rich.markdown import Markdown
from rich.console import Console


def _names(provider):
    if isinstance(provider, RetryProvider):
        return [p.__name__ for p in provider.providers]
    else:
        return [provider.__name__]


def list_providers(model=None):
    providers = []
    if model is not None:
        model = g4f.ModelUtils.convert[model]
        providers.extend(_names(model.best_provider))

    for name, provider in g4f.ProviderUtils.convert.items():
        if provider.working and model is None or name in providers:
            print(name)


def list_models(provider=None):
    for name, model in g4f.ModelUtils.convert.items():
        if provider is None or provider in _names(model.best_provider):
            print(name)


def chat(
        provider=g4f.Provider.GeekGpt,
        model=g4f.models.default,
        system_prompt=None,
        color=True,
):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    while True:
        try:
            if color:
                message = input(Fore.GREEN + ">>> ")
                print(Style.RESET_ALL, end="")
            else:
                message = input(">>> ")

            if message == "!exit":
                break

            messages.append({"role": "user", "content": message})

            extra_args = {}
            if (
                    isinstance(provider, str)
                    and provider in g4f.ProviderUtils.convert
                    and g4f.ProviderUtils.convert[provider].supports_stream
            ):
                extra_args["stream"] = True

            response = g4f.ChatCompletion.create(
                provider=provider,
                model=model,
                messages=messages,
                **extra_args,
            )

            full_response = ""
            if color:
                with Live(
                        Markdown(full_response),
                        auto_refresh=False,
                        vertical_overflow="crop_top",
                ) as live:
                    for part in response:
                        full_response += part
                        live.update(Markdown(full_response), refresh=True)
            else:
                for part in response:
                    full_response += part
                    print(part, flush=True, end="")
                print()
            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            if color:
                Console().print_exception()
            else:
                print(e, file=sys.stderr)

            if messages and messages[-1]["role"] == "user":
                messages.pop()

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    list_help = "list available providers/models and exit\n(set --model or --provider to narrow down the results)"
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("SYSTEM_PROMPT", nargs="*", help="system prompt")
    parser.add_argument("--provider", help="provider to use/list models for")
    parser.add_argument("--model", help="model to use/list providers for")
    parser.add_argument("--list", choices=["providers", "models"], help=list_help)
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug output")
    parser.add_argument("-C", "--color", action="store_true", help="show colored output")
    args = parser.parse_args()

    if args.list == "providers":
        list_providers(args.model)
        parser.exit(0)
    elif args.list == "models":
        list_models(args.provider)
        parser.exit(0)

    g4f.debug.logging = args.verbose
    g4f.debug.version_check = False

    completion_args = {"system_prompt": " ".join(args.SYSTEM_PROMPT)}

    if not args.provider and not args.model:
        completion_args["provider"] = g4f.Provider.GeekGpt
        completion_args["model"] = g4f.models.default
    elif not args.model:
        completion_args["model"] = g4f.models.default
    else:
        completion_args["provider"] = args.provider
        completion_args["model"] = args.model

    chat(**completion_args, color=args.color)
