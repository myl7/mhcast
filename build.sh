mkdir -p bin
(cd cmd/gen-wkeys && go build -o ../../bin/gen-wkeys)
(cd cmd/client && go build -o ../../bin/client)
(cd cmd/server && go build -o ../../bin/server)
