#!/usr/bin/env python3
"""Supported executable entrypoint for ordinary PASS source authoring."""

from runtime.pass_authoring_workflow import main


if __name__ == "__main__":
    raise SystemExit(main())
