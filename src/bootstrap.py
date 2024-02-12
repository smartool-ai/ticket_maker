import os
import json


ENV_VAR_ALLOWLIST = [
    "AUTH0_DOMAIN",
    "AUTH0_CLIENT_ID",
    "AUTH0_AUDIENCE",
]


def bootstrap():
    """Performs any necessary bootstrapping for the application before serving.
    """
    prepare_static_dir(os.path.join(
        os.path.dirname(__file__), "..", "static"), "/tmp/static")


def prepare_static_dir(input_path, output_path):
    """Recursively replaces environment variables in all files in a directory.
    """
    for root, dirs, files in os.walk(input_path):
        for file in files:
            path = os.path.join(root, file)
            prepare_static_file(path, os.path.join(
                output_path, os.path.relpath(path, input_path)))


def prepare_static_file(input_path, output_path):
    """Replaces environment variables in a single file.

    Variables must be surrounded by double underscores, e.g. __MY_VAR__.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r") as f:
        content = f.read()

    for key, value in os.environ.items():
        if key not in ENV_VAR_ALLOWLIST:
            continue
        content = content.replace(f"__{key}__", json.dumps(value))

    with open(output_path, "w") as f:
        f.write(content)
