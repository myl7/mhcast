#!/usr/bin/env zsh
[ "${ZSH_VERSION:-}" = "" ] && echo >&2 "Only works with zsh" && exit 1
set -euo pipefail

LOG_DIR=${LOG_DIR:-$(pwd)/logs/express/}

cd third_party/express
(cd serverA && go build -o serverA serverA.go)
(cd serverB && go build -o serverB serverB.go)
for nb in {11..17..3}; do
  for mb in {0..5}; do
    wf=write-nb${nb}-mb${mb}.log
    n=$(python -c "x = 2 ** ${nb}; print(x)")

    m=$(python -c "x = 2 ** ${mb}; print(x)")
    for i in {1..${m}}; do
      (cd serverA && ./serverA 127.0.0.1:4442 1 8 ${n} 1024 >> ${LOG_DIR}/${wf} &)
      (cd serverB && ./serverB 1 8 ${n} 1024 &)
      sleep 1
      ./client/client 127.0.0.1:4443 127.0.0.1:4442 1 1024 &> /dev/null
      pkill serverB
      pkill serverA
      sleep 1
      echo >> ${LOG_DIR}/${wf}
    done

    echo >> ${LOG_DIR}/${wf}
    echo >> ${LOG_DIR}/${wf}
  done
done
