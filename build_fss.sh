cd third_party/fss
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DWITH_CUDA=OFF -DWITH_TEST=OFF -DWITH_SAMPLES=OFF -DCMAKE_C_COMPILER=gcc
cmake --build build --config Release
