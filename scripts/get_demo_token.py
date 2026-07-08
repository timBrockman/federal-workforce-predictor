#!/usr/bin/env python
"""Development helper to mint a local test JWT.

Usage:
  uv run python scripts/get_demo_token.py --user demo-user-123 --consent 2
"""

import argparse
import sys
from pathlib import Path

# Ensure package import
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import create_demo_token  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="demo-user-123")
    parser.add_argument("--consent", type=int, default=2)
    args = parser.parse_args()

    token = create_demo_token(user_id=args.user, consent_level=args.consent)
    print(token)


if __name__ == "__main__":
    main()
