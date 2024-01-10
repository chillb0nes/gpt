```
usage: main.py [-h] [--provider PROVIDER] [--model MODEL]
               [--list {providers,models}] [-v] [-C]
               [SYSTEM_PROMPT ...]

positional arguments:
  SYSTEM_PROMPT         system prompt

options:
  -h, --help            show this help message and exit
  --provider PROVIDER   provider to use/list models for
  --model MODEL         model to use/list providers for
  --list {providers,models}
                        list available providers/models and exit
                        (set --model or --provider to narrow down the results)
  -v, --verbose         show debug output
  -C, --color           show colored output
```
