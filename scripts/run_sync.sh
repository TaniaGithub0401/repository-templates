
#!/usr/bin/env bash
set -euo pipefail

# Central template repository
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export TEMPLATES_DIR="$PROJECT_DIR/templates"
export CONFIG_PATH="$PROJECT_DIR/config/templates.yml"

# Check required tools
command -v multi-gitter >/dev/null || {
    echo "Error: multi-gitter is not installed."
    exit 1
}

command -v python3 >/dev/null || {
    echo "Error: python3 is not installed."
    exit 1
}

# Check GitHub authentication
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "Error: GITHUB_TOKEN is not configured."
    exit 1
fi

# Check arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [--dry-run] owner/repo [owner/repo ...]"
    exit 1
fi

# Enable dry-run by default for safety
DRY_RUN=true

if [[ "${1:-}" == "--apply" ]]; then
    DRY_RUN=false
    shift
elif [[ "${1:-}" == "--dry-run" ]]; then
    shift
fi

if [[ $# -eq 0 ]]; then
    echo "Error: At least one repository is required."
    exit 1
fi

# Build repository arguments
REPOSITORY_ARGS=()

for repository in "$@"; do
    if [[ ! "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
        echo "Invalid repository: $repository"
        exit 1
    fi

    REPOSITORY_ARGS+=("-R" "$repository")
done

# Additional Multi-Gitter options
OPTIONS=()

if [[ "$DRY_RUN" == true ]]; then
    OPTIONS+=("--dry-run")
fi

echo "Starting template synchronization..."
echo "Repositories: $*"
echo "Dry run: $DRY_RUN"

multi-gitter run \
    "python3 $PROJECT_DIR/scripts/sync_templates.py" \
    "${REPOSITORY_ARGS[@]}" \
    --base-branch main \
    --fork \
    --git-type cmd \
    "${OPTIONS[@]}" \
    -B sync-repository-templates \
    -m "Synchronize repository templates" \
    --pr-title "Synchronize shared repository templates" \
    --pr-body "Synchronize shared files from the central template repository." \
    --author-name "github-actions[bot]" \
    --author-email "41898282+github-actions[bot]@users.noreply.github.com" \
    --log-level=info
