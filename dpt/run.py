"""
===============================================================================
Batch runner for org.py

Reads parameter sets from a text file, creates a separate output folder
for each set, and runs the simulation inside that folder.

Usage:
  python run.py                    # use default params.txt
  python run.py my_params.txt      # use a custom parameter file

Parameter file format (one set per line):
  alpha  beta  N
  # lines starting with # are ignored
===============================================================================
"""

import os
import subprocess
import sys


def load_params(path):
    """Read (alpha, beta, N) tuples from a text file."""
    sets = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tokens = line.split()
            if len(tokens) < 3:
                continue
            try:
                alpha = float(tokens[0])
                beta  = float(tokens[1])
                N     = int(tokens[2])
                sets.append((alpha, beta, N))
            except ValueError:
                print(f"  [skip] bad line: {line}", file=sys.stderr)
    return sets


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ORG_SCRIPT = os.path.join(SCRIPT_DIR, "org.py")


def run_one(alpha, beta, N):
    """Run org.py for (alpha, beta, N) inside a dedicated folder."""
    folder = f"run_{N}_{alpha}_{beta}"
    folder_path = os.path.join(SCRIPT_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  alpha={alpha}  beta={beta}  N={N}")
    print(f"  output -> {folder}/")
    print(f"{'=' * 60}")

    result = subprocess.run(
        [sys.executable, ORG_SCRIPT, str(alpha), str(beta), str(N)],
        cwd=folder_path,
        capture_output=True,
        text=True,
        check=False
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"  [stderr] {result.stderr.strip()}")

    if result.returncode != 0:
        print(f"  !! Failed with return code {result.returncode}")
        return False
    return True


def main():
    if len(sys.argv) >= 2:
        param_file = sys.argv[1]
    else:
        param_file = os.path.join(SCRIPT_DIR, "params.txt")

    if not os.path.exists(param_file):
        print(f"Error: parameter file not found: {param_file}", file=sys.stderr)
        sys.exit(1)

    params = load_params(param_file)
    if not params:
        print(f"Error: no valid parameter sets in {param_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Parameter file: {param_file}")
    print(f"Total sets: {len(params)}\n")

    ok = 0
    fail = 0
    for alpha, beta, N in params:
        if run_one(alpha, beta, N):
            ok += 1
        else:
            fail += 1

    print(f"\n{'=' * 60}")
    print(f"  Done.  Successful: {ok}  Failed: {fail}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
