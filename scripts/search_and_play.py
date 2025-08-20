import json
import subprocess
import sys


def main() -> None:
    query = "Daft Punk One More Time"
    try:
        result = subprocess.check_output(
            [sys.executable, "scripts/search_tracks.py", "--query", query, "--limit", "1"],
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        raise

    items = json.loads(result or "[]")
    if not items:
        print("no_results")
        return
    uri = items[0]["uri"]

    subprocess.check_call(
        [sys.executable, "scripts/play_uri.py", "--uri", uri]
    )


if __name__ == "__main__":
    main()


