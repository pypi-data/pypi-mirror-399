def main():
    import subprocess
    import sys

    from ruff.__main__ import find_ruff_bin  # pyright: ignore[reportMissingTypeStubs]

    def run_ruff(args: list[str]) -> int:
        ruff = find_ruff_bin()

        if sys.platform == "win32":
            completed = subprocess.run([ruff, *args])
            return completed.returncode
        else:
            completed = subprocess.run([ruff, *args])
            return completed.returncode

    user_args = sys.argv[1:]

    if not user_args:
        print("Usage: iruff <PATH> [additional ruff args...]")
        sys.exit(1)

    # import sort and lint fix
    exit_code = run_ruff(["check", "--select", "I", "--fix", *user_args])
    if exit_code != 0:
        sys.exit(exit_code)

    # formatter run
    exit_code = run_ruff(["format", *user_args])
    sys.exit(exit_code)
