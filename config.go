package mhcast

import (
	"encoding/json"
	"log"
	"os"
)

func init() {
	LoadConfig("")
}

type Config struct {
	Server0Addr string `json:"server0_addr"`
	Server1Addr string `json:"server1_addr"`
	AlphaBitlen int    `json:"alpha_bitlen"`
	Wkeys       []byte
	PubWkeys    []byte
}

var Conf Config

func LoadConfig(path string) {
	if path == "" {
		path = "config.json"
	}

	confB, err := os.ReadFile(path)
	if err != nil {
		log.Fatalln("failed to read config file", err)
	}

	err = json.Unmarshal(confB, &Conf)
	if err != nil {
		log.Fatalln("failed to unmarshal config", err)
	}

	Conf.Wkeys, err = os.ReadFile("wkeys.bin")
	if err != nil {
		log.Println("failed to read wkeys", err)
	}

	Conf.PubWkeys, err = os.ReadFile("pub_wkeys.bin")
	if err != nil {
		log.Println("failed to read pub_wkeys", err)
	}
}
