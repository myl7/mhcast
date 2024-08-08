pub mod dif;
mod pm;

mod grpc {
    tonic::include_proto!("mhcast");
}

use std::collections::HashMap;

use group::{Group, GroupEncoding};
use jubjub::{Fr, SubgroupPoint};
use rand::prelude::*;
use sha2::{Digest, Sha256};

use dif::Dif;
use pm::{PmapCompact, PmapSparse};
use tracing::info_span;

#[derive(Debug)]
pub struct SendConfig {
    pub n: u32,
    pub m: u32,
    pub r: Vec<u32>,
    pub w: Vec<Fr>,
}

pub fn send(c: &SendConfig, dif: &Dif, m: &[u8; 1024]) -> (Vec<u8>, Vec<u8>) {
    _ = info_span!("send", c.n, c.m).entered();

    let pm_span = info_span!("pm").entered();
    assert_eq!(c.r.len(), c.m as usize);

    let al = thread_rng().gen_range(0..=c.n);
    let ar = al + c.m + 1;

    let pm_s = PmapSparse::new_from_all_map((al, ar), &c.r, c.n);
    let mut cache = HashMap::new();
    for (&ri, w) in c.r.iter().zip(c.w.iter()) {
        cache.insert(ri, (pm_s.map(ri), w));
    }
    let pm_c: PmapCompact = pm_s.clone().into();
    let pm_bs: Vec<_> = pm_c.into();
    drop(pm_span);

    let dif_span = info_span!("dif").entered();
    let mut s0s = vec![[0u8; 1024]; 2];
    s0s.iter_mut().for_each(|s0| thread_rng().fill(s0));

    let (k0, k1) = dif.gen((al, ar), m, std::array::from_fn(|i| &s0s[i]));
    drop(dif_span);

    let dif_eval_span = info_span!("dif_eval").entered();
    let xs: Vec<u32> = (al + 1..ar).collect();
    let mut ys0 = vec![[0u8; 1024]; c.m as usize];
    let mut ys1 = vec![[0u8; 1024]; c.m as usize];
    dif.batch_eval(false, k0.clone(), &xs, &mut ys0);
    dif.batch_eval(true, k1.clone(), &xs, &mut ys1);
    drop(dif_eval_span);

    let mac_span = info_span!("mac").entered();
    let ys0_fs = ys0
        .iter()
        .map(|y| {
            let mut bs = vec![0; 64];
            bs[..32].copy_from_slice(Sha256::digest(y).as_slice());
            Fr::from_bytes_wide(bs.as_slice().try_into().unwrap())
        })
        .collect::<Vec<_>>();
    let ys1_fs = ys0
        .iter()
        .map(|y| {
            let mut bs = vec![0; 64];
            bs[..32].copy_from_slice(Sha256::digest(y).as_slice());
            // Neg is important.
            -Fr::from_bytes_wide(bs.as_slice().try_into().unwrap())
        })
        .collect::<Vec<_>>();
    let ys_mac: Vec<_> = ys0_fs
        .iter()
        .zip(ys1_fs.iter())
        .map(|(y0, y1)| y0 + y1)
        .collect();
    let ys_sum_mac = ys_mac.iter().enumerate().fold(Fr::zero(), |acc, (i, y)| {
        acc + y * cache[&pm_s.map(i as u32 + al + 1)].1
    });
    let t = SubgroupPoint::generator() * ys_sum_mac;
    let t0 = SubgroupPoint::random(&mut thread_rng());
    let t1 = t - t0;
    let t0_bs = t0.to_bytes().to_vec();
    let t1_bs = t1.to_bytes().to_vec();
    drop(mac_span);

    let multicast0 = grpc::Multicast {
        share: Some(grpc::DifShare {
            s0: k0.s0s[0].to_vec(),
            cws_l: k0
                .cws_l
                .iter()
                .map(|cw| grpc::Cw {
                    s: cw.s.to_vec(),
                    v: cw.v.to_vec(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_l: k0.cw_np1_l.to_vec(),
            cws_r: k0
                .cws_r
                .iter()
                .map(|cw| grpc::Cw {
                    s: cw.s.to_vec(),
                    v: cw.v.to_vec(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_r: k0.cw_np1_r.to_vec(),
        }),
        pm: pm_bs.clone(),
        mac_share: t0_bs,
    };
    let multicast0_bs = prost::Message::encode_to_vec(&multicast0);
    let multicast1 = grpc::Multicast {
        share: Some(grpc::DifShare {
            s0: k1.s0s[0].to_vec(),
            cws_l: k1
                .cws_l
                .iter()
                .map(|cw| grpc::Cw {
                    s: cw.s.to_vec(),
                    v: cw.v.to_vec(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_l: k1.cw_np1_l.to_vec(),
            cws_r: k1
                .cws_r
                .iter()
                .map(|cw| grpc::Cw {
                    s: cw.s.to_vec(),
                    v: cw.v.to_vec(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_r: k1.cw_np1_r.to_vec(),
        }),
        pm: pm_bs,
        mac_share: t1_bs,
    };
    let multicast1_bs = prost::Message::encode_to_vec(&multicast1);
    (multicast0_bs, multicast1_bs)
}
