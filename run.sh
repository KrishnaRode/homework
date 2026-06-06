#!/usr/bin/env bash
# =============================================================================
#  File:        run.sh  (repo root)
#  Description: Convenience wrapper — delegates to the real PrepWell launcher in
#               prepwell/run.sh so `./run.sh` works from the repo root too.
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/prepwell"
exec ./run.sh "$@"
