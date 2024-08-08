fn main() {
    tonic_build::compile_protos("proto/mhcast.proto").unwrap();
}
