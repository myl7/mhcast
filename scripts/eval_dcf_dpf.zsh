#!/usr/bin/env zsh
[ "${ZSH_VERSION:-}" = "" ] && echo >&2 "Only works with zsh" && exit 1
set -euo pipefail

LOG_DIR=${LOG_DIR:-$(pwd)/logs/dcf_dpf/}

export RAYON_NUM_THREADS=8

for trial in {1..5}; do
  for nb in {11..17}; do
    export NB=${nb}
    export MB=0
    cargo run -r --bin send &> /dev/null
    wf=dif-nb${nb}.log
    cargo run -r --bin write >> ${LOG_DIR}/${wf}
    echo >> ${LOG_DIR}/${wf}
  done
done

cd third_party/express
(cd serverA && go build -o serverA serverA.go)
(cd serverB && go build -o serverB serverB.go)
for nb in {11..17}; do
  wf=dpf-nb${nb}.log
  n=$(python -c "x = 2 ** ${nb}; print(x)")
  (cd serverA && ./serverA 127.0.0.1:4442 1 8 ${n} 1024 >> ${LOG_DIR}/${wf} &)
  (cd serverB && ./serverB 1 8 ${n} 1024 &)
  sleep 1
  ./client/client 127.0.0.1:4443 127.0.0.1:4442 1 1024 &> /dev/null
  pkill serverB
  pkill serverA
  sleep 1
done
