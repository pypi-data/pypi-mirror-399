"""Console entrypoints for LLM-ify."""

import subprocess
import sys


def _ensure_interactive() -> None:
    if "--interactive" not in sys.argv:
        sys.argv.insert(1, "--interactive")


def _maybe_run_setup() -> bool:
    if len(sys.argv) < 2:
        return False
    if sys.argv[1].lower() != "setup":
        return False
    subprocess.run(["crawl4ai-setup"], check=True)
    return True


def main() -> None:
    if _maybe_run_setup():
        return
    _ensure_interactive()
    from llmify.generate_llmstxt import main as run

    run()


def main_tui() -> None:
    if _maybe_run_setup():
        return
    _ensure_interactive()
    from llmify.generate_llmstxt import main as run

    run()
