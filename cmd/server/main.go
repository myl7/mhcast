package main

import (
	"flag"

	"github.com/myl7/mhcast"
)

func main() {
	mhcast.PrgInit()

	id := flag.Int("id", 0, "server id")
	flag.Parse()

	server := mhcast.NewServer(*id)
	server.Connect()
	server.Listen()
}
