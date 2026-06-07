#!/usr/bin/env python
"""Thin wrapper so the eval runner can be invoked as a script.

Prefer the installed console command `pii-eval`; this exists for environments
where running a file directly is more convenient:

    python scripts/run_eval.py data/eval/sample.jsonl
"""

from pii_detector.eval.runner import main

if __name__ == "__main__":
    main()
