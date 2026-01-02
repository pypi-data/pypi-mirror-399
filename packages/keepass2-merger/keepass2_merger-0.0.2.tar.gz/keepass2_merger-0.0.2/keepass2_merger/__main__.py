"""Entrypoint for `python -m keepass2_merger`."""

from .cli import main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
