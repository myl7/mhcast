package main

import (
	"os"

	"github.com/myl7/mhcast"
)

const (
	wkeys_fname     = "wkeys.bin"
	pub_wkeys_fname = "pub_wkeys.bin"
)

func main() {
	wkeys := make([]byte, mhcast.WkeyLen*(1<<mhcast.Conf.AlphaBitlen))
	for i := range 1 << mhcast.Conf.AlphaBitlen {
		wkey := mhcast.GenWkey()
		copy(wkeys[i*mhcast.WkeyLen:(i+1)*mhcast.WkeyLen], wkey)
	}
	os.WriteFile(wkeys_fname, wkeys, 0644)

	pub_wkeys := make([]byte, mhcast.PubWkeyLen*(1<<mhcast.Conf.AlphaBitlen))
	for i := range 1 << mhcast.Conf.AlphaBitlen {
		pub_wkey := mhcast.GenPubWkey(wkeys[i*mhcast.WkeyLen : (i+1)*mhcast.WkeyLen])
		copy(pub_wkeys[i*mhcast.PubWkeyLen:(i+1)*mhcast.PubWkeyLen], pub_wkey)
	}
	os.WriteFile(pub_wkeys_fname, pub_wkeys, 0644)
}
