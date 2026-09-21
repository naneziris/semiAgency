"""Allocate a run file for a chat-mode run and print its path.

    python scripts/bench_new_run.py <case> <model-id>

Used by /bench-run so that file names stay consistent. Writes the header only.
"""
import sys

import benchlib as B


def main(argv):
    if len(argv) != 2:
        B.die("usage: bench_new_run.py <case> <model-id>")
    case, model = argv
    B.case_dir(case)
    p, n = B.new_run_path(case, model, "chat")
    print(p.relative_to(B.ROOT).as_posix())


if __name__ == "__main__":
    main(sys.argv[1:])
