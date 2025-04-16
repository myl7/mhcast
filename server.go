package mhcast

import (
	"context"
	"log"
	"net"
	"strings"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func xorBytes(a, b []byte) []byte {
	for i := range a {
		a[i] ^= b[i]
	}
	return a
}

type betaTableEntry struct {
	beta      []byte
	betaOther []byte
	writeWait chan int32
}

type Server struct {
	id            int
	ms            *grpc.Server
	mc            MhcastClient
	betaTable     map[int64]*betaTableEntry
	betaTableLock sync.Mutex
}

func NewServer(id int) *Server {
	return &Server{
		id:            id,
		ms:            grpc.NewServer(),
		mc:            nil,
		betaTable:     make(map[int64]*betaTableEntry),
		betaTableLock: sync.Mutex{},
	}
}

func (s *Server) Connect() {
	var addrOther string
	if s.id == 0 {
		addrOther = Conf.Server1Addr
	} else {
		addrOther = Conf.Server0Addr
	}

	c, err := grpc.NewClient(addrOther, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect to the other server: %v", err)
	}

	s.mc = NewMhcastClient(c)
}

func (s *Server) Listen() {
	RegisterMhcastServer(s.ms, s)

	var addr string
	if s.id == 0 {
		addr = Conf.Server0Addr
	} else {
		addr = Conf.Server1Addr
	}

	port := ":" + strings.Split(addr, ":")[1]

	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("server %d listening at %v", s.id, addr)
	if err := s.ms.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

// Write impl MhcastServer
func (s *Server) Write(ctx context.Context, msg *Msg) (*WriteResp, error) {
	id := msg.Id

	log.Printf("to dif eval msg %d", id)
	evalT := time.Now()

	resultL := DcfEvalFullDomain(msg.S0, uint8(s.id), &DcfKey{Cws: msg.CwsL, CwNp1: msg.CwNp1L}, Conf.AlphaBitlen)
	resultR := DcfEvalFullDomain(msg.S0, uint8(s.id), &DcfKey{Cws: msg.CwsR, CwNp1: msg.CwNp1R}, Conf.AlphaBitlen)
	result := xorBytes(resultL, resultR)

	log.Printf("dif evaled msg %d, time %d", id, time.Since(evalT))

	log.Printf("to commit msg %d", id)
	commitT := time.Now()

	beta := CommitCwMac(uint8(s.id), msg.T, result, Conf.PubWkeys)

	log.Printf("commited msg %d, time %d", id, time.Since(commitT))

	go func() {
		ctx := context.Background()
		_, err := s.mc.ShareCommit(ctx, &Commit{
			Id:   id,
			Beta: beta,
		})
		if err != nil {
			log.Fatalf("failed to share commit: %v", err)
		}
	}()

	writeWait := make(chan int32)

	var ready bool
	func() {
		s.betaTableLock.Lock()
		defer s.betaTableLock.Unlock()

		entry, ok := s.betaTable[id]
		if ok {
			if entry.betaOther != nil {
				ready = true
			}

			entry.beta = beta
			entry.writeWait = writeWait
			s.betaTable[id] = entry
		} else {
			s.betaTable[id] = &betaTableEntry{beta: beta, writeWait: writeWait}
		}
	}()

	if ready {
		go s.verifyCommit(id)
	}

	ret := <-writeWait
	return &WriteResp{Ret: ret}, nil
}

// ShareCommit impl MhcastServer
func (s *Server) ShareCommit(ctx context.Context, commit *Commit) (*CommitResp, error) {
	go s.handleCommit(commit)
	return &CommitResp{}, nil
}

func (s *Server) handleCommit(commit *Commit) {
	id := commit.Id

	var ready bool
	func() {
		s.betaTableLock.Lock()
		defer s.betaTableLock.Unlock()

		entry, ok := s.betaTable[id]
		if ok {
			if entry.beta != nil {
				ready = true
			}

			entry.betaOther = commit.Beta
			s.betaTable[id] = entry
		} else {
			s.betaTable[id] = &betaTableEntry{betaOther: commit.Beta}
		}
	}()

	if ready {
		go s.verifyCommit(id)
	}
}

func (s *Server) verifyCommit(id int64) {
	log.Printf("to verify commit for id %d", id)

	var beta []byte
	var betaOther []byte
	var writeWait chan int32
	func() {
		s.betaTableLock.Lock()
		defer s.betaTableLock.Unlock()

		entry, ok := s.betaTable[id]
		if ok {
			beta = entry.beta
			betaOther = entry.betaOther
			writeWait = entry.writeWait
			delete(s.betaTable, id)
		} else {
			log.Fatalf("no beta found in beta table for id %d", id)
		}
	}()

	var ret int32 = 1
	if VerifyCwMac(beta, betaOther) {
		ret = 0
	} else {
		ret = 1
	}

	writeWait <- ret
}

// mustEmbedUnimplementedMhcastServer impl MhcastServer
func (s *Server) mustEmbedUnimplementedMhcastServer() {}
