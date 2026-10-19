#!/bin/bash
# Live preview of the site at http://localhost:4000, rebuilt whenever a file is saved.
# From Windows, in the repo folder:  wsl bash scripts/serve.sh
set -euo pipefail
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init - bash)"
cd "$(dirname "$0")/.."
# --force_polling: WSL can't see file-change events on Windows drives, so poll instead.
# Output goes to a Linux folder because writing to the Windows drive from WSL is slow.
exec bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload --force_polling \
  --destination "$HOME/portfolio-preview" "$@"
