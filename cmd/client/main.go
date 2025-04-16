package main

import (
	"bytes"
	"context"
	"flag"
	"log"

	"github.com/myl7/mhcast"
)

var body = func() []byte {
	text := []byte("Hello, world!")
	padLen := mhcast.Lambda - len(text)
	pad := bytes.Repeat([]byte{0}, padLen)
	return append(text, pad...)
}()

const alphaL = 100

func main() {
	mhcast.PrgInit()

	msgNum := flag.Int("n", 100, "sent msg num")
	groupSize := flag.Int("g", 16, "group size")
	flag.Parse()

	client := mhcast.NewClient()
	ctx := context.Background()
	client.Connect()

	for id := range *msgNum {
		ret, err := client.Write(ctx, int64(id), body, alphaL, alphaL+*groupSize)
		if err != nil {
			log.Fatalf("failed to write msg %d: %v", id, err)
		}

		log.Printf("sent msg %d, ret %d", id, ret)
	}
}
