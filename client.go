package mhcast

import (
	"context"
	crand "crypto/rand"
	"fmt"
	"log"
	"sync"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/protobuf/proto"
)

type Client struct {
	mc0 MhcastClient
	mc1 MhcastClient
}

func NewClient() *Client {
	return &Client{
		mc0: nil,
		mc1: nil,
	}
}

func (c *Client) Connect() {
	conn0, err := grpc.NewClient(Conf.Server0Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect to the server 0: %v", err)
	}

	c.mc0 = NewMhcastClient(conn0)

	conn1, err := grpc.NewClient(Conf.Server1Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect to the server 1: %v", err)
	}

	c.mc1 = NewMhcastClient(conn1)
}

func genRandBytes(n int) []byte {
	b := make([]byte, n)
	if _, err := crand.Read(b); err != nil {
		log.Fatalf("failed to generate random bytes: %v", err)
	}
	return b
}

func intToBytes(n int, bitlen int) []byte {
	// Calculate minimum number of bytes needed to contain bitlen bits
	byteLen := (bitlen + 7) / 8
	bytes := make([]byte, byteLen)

	// Convert to little-endian bytes
	for i := 0; i < byteLen; i++ {
		bytes[i] = byte(n >> (i * 8))
	}

	return bytes
}

func (c *Client) Write(ctx context.Context, id int64, body []byte, alphaL, alphaR int) (int32, error) {
	if len(body) != Lambda {
		return 0, fmt.Errorf("body must be %d bytes", Lambda)
	}
	// TODO: body MSB must be 0

	s0s := genRandBytes(Lambda * 2)
	dcfKeyL := NewEmptyDcfKey()
	dcfKeyR := NewEmptyDcfKey()

	alphaLBytes := intToBytes(alphaL, Conf.AlphaBitlen)
	alphaLBits := Bits{bytes: alphaLBytes, bitlen: Conf.AlphaBitlen}
	alphaRBytes := intToBytes(alphaR, Conf.AlphaBitlen)
	alphaRBits := Bits{bytes: alphaRBytes, bitlen: Conf.AlphaBitlen}

	DcfGen(dcfKeyL, &CmpFunc{Alpha: alphaLBits, Beta: body, Bound: LtAlpha}, s0s)
	DcfGen(dcfKeyR, &CmpFunc{Alpha: alphaRBits, Beta: body, Bound: LtAlpha}, s0s)

	// Evaluate DCF only for the range [alphaL, alphaR)
	ys0 := make([]byte, (alphaR-alphaL)*Lambda)
	ys1 := make([]byte, (alphaR-alphaL)*Lambda)

	for i := alphaL; i < alphaR; i++ {
		// Create Bits for current position
		xBytes := intToBytes(i, Conf.AlphaBitlen)
		xBits := Bits{bytes: xBytes, bitlen: Conf.AlphaBitlen}

		// Evaluate DCF at position i for both servers
		y0L := DcfEval(s0s[0:Lambda], 0, dcfKeyL, xBits)
		y0R := DcfEval(s0s[0:Lambda], 0, dcfKeyR, xBits)
		y1L := DcfEval(s0s[Lambda:], 1, dcfKeyL, xBits)
		y1R := DcfEval(s0s[Lambda:], 1, dcfKeyR, xBits)

		// XOR the results and store in the appropriate position
		offset := (i - alphaL) * Lambda
		copy(ys0[offset:offset+Lambda], xorBytes(y0L, y0R))
		copy(ys1[offset:offset+Lambda], xorBytes(y1L, y1R))
	}
	t0, t1 := GenCwMac(ys0, ys1, alphaR-alphaL, Conf.Wkeys[alphaL*WkeyLen:alphaR*WkeyLen])

	// TODO
	var pm []byte

	var ret0, ret1 int32
	var wg sync.WaitGroup

	wg.Add(2)
	go func() {
		defer wg.Done()

		msg0 := &Msg{
			Id:     id,
			S0:     s0s[0:Lambda],
			CwsL:   dcfKeyL.Cws,
			CwNp1L: dcfKeyL.CwNp1,
			CwsR:   dcfKeyR.Cws,
			CwNp1R: dcfKeyR.CwNp1,
			Pm:     pm,
			T:      t0,
		}

		// Extra test
		msg0Bs, err := proto.Marshal(msg0)
		if err != nil {
			log.Fatalf("failed to marshal msg0: %v", err)
		}
		log.Printf("msg0 len: %dB", len(msg0Bs))

		resp, err := c.mc0.Write(ctx, msg0)
		if err != nil {
			log.Fatalf("failed to write to the server 0: %v", err)
		}
		ret0 = resp.Ret
	}()
	go func() {
		defer wg.Done()

		msg1 := &Msg{
			Id:     id,
			S0:     s0s[Lambda:],
			CwsL:   dcfKeyL.Cws,
			CwNp1L: dcfKeyL.CwNp1,
			CwsR:   dcfKeyR.Cws,
			CwNp1R: dcfKeyR.CwNp1,
			Pm:     pm,
			T:      t1,
		}

		resp, err := c.mc1.Write(ctx, msg1)
		if err != nil {
			log.Fatalf("failed to write to the server 1: %v", err)
		}
		ret1 = resp.Ret
	}()
	wg.Wait()

	var ret int32
	if ret0 != 0 {
		ret = ret0
	} else if ret1 != 0 {
		ret = ret1
	}
	return ret, nil
}
