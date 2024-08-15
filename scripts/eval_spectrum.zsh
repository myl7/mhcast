#!/usr/bin/env zsh
[ "${ZSH_VERSION:-}" = "" ] && echo >&2 "Only works with zsh" && exit 1
set -euo pipefail

LOG_DIR=${LOG_DIR:-$(pwd)/logs/spectrum/}

export RAYON_NUM_THREADS=8
export THREAD_NUM=8

cd third_party/spectrum
for nb in {11..17..3}; do
  export NB=${nb}
  for mb in {0..5}; do
    export MB=${mb}
    wf=write-nb${nb}-mb${mb}.log
    cargo run -r --bin write >> ${LOG_DIR}/${wf}
    echo >> ${LOG_DIR}/${wf}
  done
done
