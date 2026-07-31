"""Enable `python3 -m ingenium ...` to invoke the CLI."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
