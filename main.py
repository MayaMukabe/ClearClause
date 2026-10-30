#!/usr/bin/env python3
"""Launch the ClearClause AI web app."""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path
from threading import Timer

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import load_environment


def main() -> int:
    load_environment()
    parser = argparse.ArgumentParser(description="ClearClause AI web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        Timer(1.0, lambda: webbrowser.open(url)).start()

    import uvicorn

    uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
