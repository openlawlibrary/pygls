import sys
import subprocess

AUTOGENERATED_CLIENT_FILE = "pygls/lsp/client.py"

subprocess.run(["poe", "generate_client"])

result = subprocess.run(
    ["git", "diff", "--exit-code", AUTOGENERATED_CLIENT_FILE], stdout=subprocess.DEVNULL
)

if result.returncode == 0:
    print("✅ Pygls client is up to date")
else:
    print(
        "🔴 Pygls client not uptodate\n"
        "1. Generate with: `poetry run poe generate_client`\n"
        "2. Commit"
    )
    sys.exit(result.returncode)