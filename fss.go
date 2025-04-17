package mhcast

/*
#cgo CFLAGS: -I${SRCDIR}/third_party/fss/include
#cgo LDFLAGS: -L${SRCDIR}/third_party/fss/build -ldcf -lcw_mac_bytes -lgroup_bytes -lprg_aes_mmo_ni -lgomp -lsodium
#include <dcf.h>
#include <cw_mac_bytes.h>
#include <fss_decl.h>
*/
import "C"

import (
	"unsafe"
)

func PrgInit() {
	C.prg_init((*C.uint8_t)(unsafe.Pointer(&PrgState[0])), C.int(len(PrgState)))
}

var PrgState = func() []byte {
	state := make([]byte, 64)
	for i := range len(state) {
		state[i] = byte(i)
	}
	return state
}()

const (
	Lambda       = 1024
	DcfCwLen     = Lambda*2 + 1
	WkeyLen      = 32
	PubWkeyLen   = 32
	MacLen       = 32
	MacCommitLen = 32
)

// Bound represents the comparison bound type
type Bound int

const (
	// LtAlpha means output = beta when input < alpha, otherwise output = 0
	LtAlpha Bound = C.kLtAlpha
	// GtAlpha means output = beta when input > alpha, otherwise output = 0
	GtAlpha Bound = C.kGtAlpha
)

// CmpFunc represents a comparison function
type CmpFunc struct {
	Alpha Bits
	Beta  []byte
	Bound Bound
}

// DcfKey represents a DCF key
type DcfKey struct {
	Cws   []byte
	CwNp1 []byte
}

func NewEmptyDcfKey() *DcfKey {
	return &DcfKey{
		Cws:   make([]byte, DcfCwLen*Conf.AlphaBitlen),
		CwNp1: make([]byte, Lambda),
	}
}

// Bits represents a bit array
type Bits struct {
	bytes  []byte
	bitlen int
}

// DcfGen generates a DCF key
func DcfGen(k *DcfKey, cf *CmpFunc, s0s []byte) {
	sbuf := make([]byte, Lambda*10)
	copy(sbuf, s0s)

	cK := C.DcfKey{
		cws:    (*C.uint8_t)(unsafe.Pointer(&k.Cws[0])),
		cw_np1: (*C.uint8_t)(unsafe.Pointer(&k.CwNp1[0])),
	}
	cAlpha := C.Bits{
		bytes:  (*C.uint8_t)(unsafe.Pointer(&cf.Alpha.bytes[0])),
		bitlen: C.int(cf.Alpha.bitlen),
	}
	cCf := C.CmpFunc{
		alpha: cAlpha,
		beta:  (*C.uint8_t)(unsafe.Pointer(&cf.Beta[0])),
		bound: C.enum_Bound(cf.Bound),
	}
	cSbuf := (*C.uint8_t)(unsafe.Pointer(&sbuf[0]))
	C.dcf_gen(cK, cCf, cSbuf)
}

// DcfEval evaluates a DCF at a single input point
func DcfEval(s0 []byte, b uint8, k *DcfKey, x Bits) []byte {
	sbuf := make([]byte, 6*Lambda)
	copy(sbuf, s0)

	cSbuf := (*C.uint8_t)(unsafe.Pointer(&sbuf[0]))
	cK := C.DcfKey{
		cws:    (*C.uint8_t)(unsafe.Pointer(&k.Cws[0])),
		cw_np1: (*C.uint8_t)(unsafe.Pointer(&k.CwNp1[0])),
	}
	cX := C.Bits{
		bytes:  (*C.uint8_t)(unsafe.Pointer(&x.bytes[0])),
		bitlen: C.int(x.bitlen),
	}
	C.dcf_eval(cSbuf, C.uint8_t(b), cK, cX)

	return sbuf[:Lambda]
}

// DcfEvalFullDomain evaluates a DCF at all input points
func DcfEvalFullDomain(s0 []byte, b uint8, k *DcfKey, xBitlen int) []byte {
	sbuf := make([]byte, 1<<xBitlen*Lambda)
	copy(sbuf, s0)

	cSbuf := (*C.uint8_t)(unsafe.Pointer(&sbuf[0]))
	cK := C.DcfKey{
		cws:    (*C.uint8_t)(unsafe.Pointer(&k.Cws[0])),
		cw_np1: (*C.uint8_t)(unsafe.Pointer(&k.CwNp1[0])),
	}
	C.dcf_eval_full_domain(cSbuf, C.uint8_t(b), cK, C.int(xBitlen))

	return sbuf
}

// GenWkey generates a write key
func GenWkey() []byte {
	wkey := make([]byte, WkeyLen)
	C.gen_wkey((*C.uint8_t)(unsafe.Pointer(&wkey[0])))
	return wkey
}

// GenPubWkey generates a public write key
func GenPubWkey(wkey []byte) []byte {
	pubWkey := make([]byte, PubWkeyLen)
	C.gen_pub_wkey(
		(*C.uint8_t)(unsafe.Pointer(&pubWkey[0])),
		(*C.uint8_t)(unsafe.Pointer(&wkey[0])),
	)
	return pubWkey
}

// GenCwMac generates a Carter-Wegman MAC and shares it
func GenCwMac(sbufs0, sbufs1 []byte, sbufsNum int, wkeys []byte) ([]byte, []byte) {
	t0 := make([]byte, MacLen)
	t1 := make([]byte, MacLen)

	C.gen_cw_mac(
		(*C.uint8_t)(unsafe.Pointer(&t0[0])),
		(*C.uint8_t)(unsafe.Pointer(&t1[0])),
		(*C.uint8_t)(unsafe.Pointer(&sbufs0[0])),
		(*C.uint8_t)(unsafe.Pointer(&sbufs1[0])),
		C.int(sbufsNum),
		C.int(Lambda),
		(*C.uint8_t)(unsafe.Pointer(&wkeys[0])),
	)

	return t0, t1
}

// CommitCwMac commits a Carter-Wegman MAC share
func CommitCwMac(b uint8, t, sbufs []byte, pubWkeys []byte) []byte {
	beta := make([]byte, MacCommitLen)

	C.commit_cw_mac(
		(*C.uint8_t)(unsafe.Pointer(&beta[0])),
		C.uint8_t(b),
		(*C.uint8_t)(unsafe.Pointer(&t[0])),
		(*C.uint8_t)(unsafe.Pointer(&sbufs[0])),
		C.int(1<<Conf.AlphaBitlen),
		C.int(Lambda),
		(*C.uint8_t)(unsafe.Pointer(&pubWkeys[0])),
	)

	return beta
}

// VerifyCwMac verifies a Carter-Wegman MAC commitment
func VerifyCwMac(beta0, beta1 []byte) bool {
	return C.verify_cw_mac(
		(*C.uint8_t)(unsafe.Pointer(&beta0[0])),
		(*C.uint8_t)(unsafe.Pointer(&beta1[0])),
	) == 1
}
