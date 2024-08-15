use std::{env, fs};

use aes::{cipher::KeyIvInit, Aes128};
use ctr::Ctr64LE;
use fss_rs::utils::xor_inplace;
use group::Group;
use jubjub::SubgroupPoint;
use prost::Message;
use rand::prelude::*;
use rayon::prelude::*;

use mhcast::{
    dif::{DcfImplImpl, Dif, PrgImpl},
    grpc,
    pm::PmapCompact,
    WriteConfig,
};

type Aes128Ctr64LE = Ctr64LE<Aes128>;

const KEY: [u8; 16] = [1; 16];
const IV: [u8; 16] = [2; 16];

fn main() {
    let filter_bitn: usize = env::var("NB").unwrap().parse().unwrap();
    let mut mailboxes = vec![
        ([0u8; 1024], Aes128Ctr64LE::new(&KEY.into(), &IV.into()));
        2u32.pow(filter_bitn as u32) as usize
    ];
    mailboxes.par_iter_mut().for_each(|_mailbox| {
        // enc(&mut mailbox.1, &mut mailbox.0);
    });

    let mut keys_l = vec![[0u8; 16]; 256];
    keys_l.iter_mut().for_each(|k| thread_rng().fill(k));
    let mut keys_r = vec![[0u8; 16]; 256];
    keys_r.iter_mut().for_each(|k| thread_rng().fill(k));
    let prg_l = PrgImpl::new(&std::array::from_fn(|i| &keys_l[i]));
    let prg_r = PrgImpl::new(&std::array::from_fn(|i| &keys_r[i]));
    let dcf_l = DcfImplImpl::new_with_filter(prg_l, filter_bitn);
    let dcf_r = DcfImplImpl::new_with_filter(prg_r, filter_bitn);
    let dif = Dif(dcf_l, dcf_r);

    let multicast_bs = fs::read("multicast0.bin").unwrap();
    let multicast = grpc::Multicast::decode(multicast_bs.as_slice()).unwrap();
    // let w: Vec<_> = (0..2u32.pow(filter_bitn as u32)).map(|i| Fr::from(i as u64)).collect();
    let gw = (0..2u32.pow(filter_bitn as u32))
        .into_iter()
        .map(|_w| SubgroupPoint::generator())
        .collect();
    let elem_num = 2u32.pow(filter_bitn as u32);
    let elem_bitlen = elem_num.next_power_of_two().trailing_zeros();
    let pm_c = PmapCompact::from((multicast.pm.clone(), elem_num, elem_bitlen));

    let ys = mhcast::write(
        &WriteConfig {
            b: false,
            n: 2u32.pow(filter_bitn as u32),
            gw,
        },
        &dif,
        multicast,
    );

    mailboxes
        .par_iter_mut()
        .enumerate()
        .for_each(|(i, mailbox)| {
            xor_inplace(&mut mailbox.0, &[&ys[pm_c.map(i as u32) as usize]]);
        });
}
