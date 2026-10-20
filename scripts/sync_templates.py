
#!/usr/bin/env python3
"""Synchronize selected templates with a target repository."""

import os
import re
import subprocess
from pathlib import Path

import yaml


def get_target_repository():
    """Identify the GitHub repository from its Git remote."""
    if os.environ.get("TARGET_REPOSITORY"):
        return os.environ["TARGET_REPOSITORY"]

    remote = subprocess.check_output(
        ["git", "remote", "get-url", "origin"],
        text=True,
    ).strip()

    match = re.search(r"github\.com[:/]([^/]+)/([^/\s]+)", remote)

    if not match:
        raise ValueError(f"Cannot identify GitHub repository: {remote}")

    owner, repo = match.groups()
    return f"{owner}/{repo.removesuffix('.git')}"


def main():
    templates_dir = Path(os.environ["TEMPLATES_DIR"])
    config_path = Path(os.environ["CONFIG_PATH"])
    repository = get_target_repository()

    print(f"Processing repository: {repository}")

    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    selected_groups = set()

    for target in config["targets"]:
        if repository in target.get("repositories", []):
            selected_groups.update(target["groups"])

    if not selected_groups:
        print(f"No templates configured for {repository}")
        return

    for group_name in sorted(selected_groups):
        group = config["groups"][group_name]

        for template in group["files"]:
            source = templates_dir / template["source"]
            destination = Path.cwd() / template["destination"]

            if not source.is_file():
                raise FileNotFoundError(f"Template not found: {source}")

            content = source.read_bytes()

            if destination.exists() and destination.read_bytes() == content:
                print(f"Unchanged: {template['destination']}")
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)

            print(f"Updated: {template['destination']}")


if __name__ == "__main__":
    main()
