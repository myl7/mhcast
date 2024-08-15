use std::{env, fs};

use ff::Field;
use jubjub::Fr;
use rand::prelude::*;

use mhcast::dif::{DcfImplImpl, Dif, PrgImpl};
use mhcast::SendConfig;

fn main() {
    let mut keys_l = vec![[0u8; 16]; 256];
    keys_l.iter_mut().for_each(|k| thread_rng().fill(k));
    let mut keys_r = vec![[0u8; 16]; 256];
    keys_r.iter_mut().for_each(|k| thread_rng().fill(k));
    let prg_l = PrgImpl::new(&std::array::from_fn(|i| &keys_l[i]));
    let prg_r = PrgImpl::new(&std::array::from_fn(|i| &keys_r[i]));
    let filter_bitn: usize = env::var("NB").unwrap().parse().unwrap();
    let dcf_l = DcfImplImpl::new_with_filter(prg_l, filter_bitn);
    let dcf_r = DcfImplImpl::new_with_filter(prg_r, filter_bitn);
    let dif = Dif(dcf_l, dcf_r);

    let mut m = vec![0u8; 1024];
    thread_rng().fill_bytes(&mut m);
    let cm = 2u32.pow(env::var("MB").unwrap().parse().unwrap());
    let w: Vec<_> = (0..cm).map(|_| Fr::random(thread_rng())).collect();

    let (multicast0_bs, multicast1_bs) = mhcast::send(
        &SendConfig {
            n: 2u32.pow(filter_bitn as u32),
            m: cm,
            r: (10..10 + cm).collect(),
            w,
        },
        &dif,
        m.as_slice().try_into().unwrap(),
    );

    println!(
        "multicast size: {}B",
        multicast0_bs.len() + multicast1_bs.len()
    );

    fs::write("multicast0.bin", &multicast0_bs).unwrap();
    fs::write("multicast1.bin", &multicast1_bs).unwrap();
}
