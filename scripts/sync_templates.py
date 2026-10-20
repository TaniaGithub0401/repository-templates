
#!/usr/bin/env python3
"""Synchronize shared template files with a target repository."""

import os
import shutil
from pathlib import Path


def main():
    # Directory containing the central templates
    templates_dir = Path(os.environ["TEMPLATES_DIR"])

    # Multi-Gitter runs the script inside each target repository.
    target_dir = Path.cwd()

    for source in templates_dir.rglob("*"):
        if not source.is_file():
            continue

        relative_path = source.relative_to(templates_dir)
        destination = target_dir / relative_path

        # Avoid unnecessary changes
        if destination.exists() and destination.read_bytes() == source.read_bytes():
            print(f"Unchanged: {relative_path}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        print(f"Updated: {relative_path}")


if __name__ == "__main__":
    main()
