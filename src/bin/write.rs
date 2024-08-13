use std::{env, fs};

use aes::{cipher::KeyIvInit, Aes128};
use ctr::Ctr64LE;
use fss_rs::utils::xor_inplace;
use group::Group;
use jubjub::SubgroupPoint;
use prost::Message;
use rand::prelude::*;
use rayon::prelude::*;
use tracing::info_span;
use tracing_subscriber::fmt::format::FmtSpan;

use mhcast::{
    dif::{DcfImplImpl, Dif, PrgImpl},
    grpc,
    pm::PmapCompact,
    WriteConfig,
};

type Aes128Ctr64LE = Ctr64LE<Aes128>;

const KEY: [u8; 16] = [1; 16];
const IV: [u8; 16] = [2; 16];

// fn enc(cipher: &mut Aes128Ctr64LE, buf: &mut [u8; 1024]) {
//     cipher.apply_keystream(&mut buf[..]);
// }

// fn dec(cipher: &mut Aes128Ctr64LE, buf: &mut [u8; 1024]) {
//     cipher.apply_keystream(&mut buf[..]);
// }

fn main() {
    tracing_subscriber::fmt()
        .with_span_events(FmtSpan::CLOSE)
        .init();

    let filter_bitn: usize = env::var("NB").unwrap().parse().unwrap();
    let mut mailboxes = vec![
        ([0u8; 1024], Aes128Ctr64LE::new(&KEY.into(), &IV.into()));
        2u32.pow(filter_bitn as u32) as usize
    ];
    mailboxes.par_iter_mut().for_each(|_mailbox| {
        // enc(&mut mailbox.1, &mut mailbox.0);
    });

    let dif_init_span = info_span!("dif_init").entered();
    let mut keys_l = vec![[0u8; 16]; 256];
    keys_l.iter_mut().for_each(|k| thread_rng().fill(k));
    let mut keys_r = vec![[0u8; 16]; 256];
    keys_r.iter_mut().for_each(|k| thread_rng().fill(k));
    let prg_l = PrgImpl::new(&std::array::from_fn(|i| &keys_l[i]));
    let prg_r = PrgImpl::new(&std::array::from_fn(|i| &keys_r[i]));
    let dcf_l = DcfImplImpl::new_with_filter(prg_l, filter_bitn);
    let dcf_r = DcfImplImpl::new_with_filter(prg_r, filter_bitn);
    let dif = Dif(dcf_l, dcf_r);
    drop(dif_init_span);

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

    // let reenc_span = info_span!("reenc").entered();
    mailboxes
        .par_iter_mut()
        .enumerate()
        .for_each(|(i, mailbox)| {
            // dec(&mut mailbox.1, &mut mailbox.0);
            xor_inplace(&mut mailbox.0, &[&ys[pm_c.map(i as u32) as usize]]);
            // enc(&mut mailbox.1, &mut mailbox.0);
        });
    // drop(reenc_span);
}
