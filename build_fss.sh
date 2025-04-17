cd third_party/fss
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DFSS_PRG_BLOCK_NUM=4 -DBUILD_WITH_CUDA=OFF -DBUILD_TESTING=OFF -DBUILD_SAMPLES=OFF -DCMAKE_C_COMPILER=gcc
cmake --build build --config Release
