#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    implementation = skill_root / "scripts" / "query_book_router_impl.py"
    registry = skill_root / "references" / "library" / "registry.json"
    policy = skill_root / "references" / "fowler_routing_policy.json"
    arguments = list(sys.argv[1:])
    if "--registry" not in arguments and not any(
        argument.startswith("--registry=") for argument in arguments
    ):
        arguments.extend(["--registry", str(registry)])
    if "--policy" not in arguments and not any(
        argument.startswith("--policy=") for argument in arguments
    ):
        arguments.extend(["--policy", str(policy)])
    sys.argv = [str(implementation), *arguments]
    sys.path.insert(0, str(implementation.parent))
    runpy.run_path(str(implementation), run_name="__main__")


if __name__ == "__main__":
    main()
