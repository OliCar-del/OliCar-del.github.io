#!/bin/bash
# Build the site once and run the same checks as GitHub: links, images and videos that point at
# missing files, and files over 10 MB.   From Windows, in the repo folder:  wsl bash scripts/check.sh
set -euo pipefail
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init - bash)"
cd "$(dirname "$0")/.."
out="$HOME/portfolio-check"
rm -rf "$out"
bundle exec jekyll build --quiet --destination "$out"
python3 scripts/check_site.py "$out"
