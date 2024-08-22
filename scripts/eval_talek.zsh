#!/usr/bin/env zsh
[ "${ZSH_VERSION:-}" = "" ] && echo >&2 "Only works with zsh" && exit 1
set -euo pipefail

LOG_DIR=${LOG_DIR:-$(pwd)/logs/talek/}

export DATA_SIZE=1024
export THREAD_NUM=8

cd third_party/talek/server
for nb in {11..14..3}; do
  # Because bucket depth is 4.
  export NUM_BUCKETS=$(python -c "x = 2 ** ${nb} // 4; print(x)")
  for mb in {0..5}; do
    # Yeah, all clients need to read.
    # So it is unrelated to `mb`.
    export READS_PER_WRITE=$(python -c "x = 2 ** ${nb}; print(x)")
    wf=write-nb${nb}-mb${mb}.log
    # Talek originally suggests 1min iteration, so we follow that.
    # go test -run 0 -bench BenchmarkShard -benchtime 1m >> ${LOG_DIR}/${wf} # For debug
    go test -run 0 -bench BenchmarkShard -benchtime 1m -timeout 1h | sed '/^\[/d' >> ${LOG_DIR}/${wf}
  done
done

# Too slow, so only run it once.
nb=17
export NUM_BUCKETS=$(python -c "x = 2 ** ${nb} // 4; print(x)")
mb=0
export READS_PER_WRITE=$(python -c "x = 2 ** ${nb}; print(x)")
wf=write-nb${nb}-mb${mb}.log
go test -run 0 -bench BenchmarkShard -benchtime 1m -timeout 1h | sed '/^\[/d' >> ${LOG_DIR}/${wf}
