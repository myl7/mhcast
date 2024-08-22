#!/usr/bin/env zsh
[ "${ZSH_VERSION:-}" = "" ] && echo >&2 "Only works with zsh" && exit 1
set -euo pipefail

LOG_DIR=${LOG_DIR:-$(pwd)/logs/mhcast/}

export RAYON_NUM_THREADS=8

for nb in {11..17..3}; do
  export NB=${nb}
  for mb in {6..11}; do
    export MB=${mb}
    sf=send-nb${nb}-mb${mb}.log
    cargo run -r --bin send >> ${LOG_DIR}/${sf}
    echo >> ${LOG_DIR}/${sf}
    wf=write-nb${nb}-mb${mb}.log
    cargo run -r --bin write >> ${LOG_DIR}/${wf}
    echo >> ${LOG_DIR}/${wf}
  done
done
