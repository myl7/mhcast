pub mod dif;
pub mod pm;

pub mod grpc {
    tonic::include_proto!("mhcast");
}

use std::collections::HashMap;
use std::hint::black_box;
use std::time::Instant;

use group::{Group, GroupEncoding};
use jubjub::{Fr, SubgroupPoint};
use rand::prelude::*;
use rayon::prelude::*;
use sha2::{Digest, Sha256};

use dif::Dif;
use pm::{PmapCompact, PmapSparse};

#[derive(Debug)]
pub struct SendConfig {
    pub n: u32,
    pub m: u32,
    pub r: Vec<u32>,
    pub w: Vec<Fr>,
}

#[derive(Debug)]
pub struct WriteConfig {
    pub b: bool,
    pub n: u32,
    pub gw: Vec<SubgroupPoint>,
}

pub fn send(c: &SendConfig, dif: &Dif, m: &[u8; 1024]) -> (Vec<u8>, Vec<u8>) {
    let send_start = Instant::now();

    let pm_start = Instant::now();
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
    println!("pm: {:?}", pm_start.elapsed());

    let dif_gen_start = Instant::now();
    let mut s0s = vec![[0u8; 1024]; 2];
    s0s.iter_mut().for_each(|s0| thread_rng().fill(s0));

    let (k0, k1) = dif.gen((al, ar), m, std::array::from_fn(|i| &s0s[i]));
    println!("dif gen: {:?}", dif_gen_start.elapsed());

    let dif_eval_start = Instant::now();
    let xs: Vec<u32> = (al + 1..ar).collect();
    let mut ys0 = vec![[0u8; 1024]; c.m as usize];
    let mut ys1 = vec![[0u8; 1024]; c.m as usize];
    dif.batch_eval(false, k0.clone(), &xs, &mut ys0);
    dif.batch_eval(true, k1.clone(), &xs, &mut ys1);
    println!("dif eval: {:?}", dif_eval_start.elapsed());

    let mac_start = Instant::now();
    let ys0_fs: Vec<_> = ys0
        .iter()
        .map(|y| {
            let mut bs = vec![0; 64];
            bs[..32].copy_from_slice(Sha256::digest(y).as_slice());
            Fr::from_bytes_wide(bs.as_slice().try_into().unwrap())
        })
        .collect();
    let ys1_fs: Vec<_> = ys0
        .iter()
        .map(|y| {
            let mut bs = vec![0; 64];
            bs[..32].copy_from_slice(Sha256::digest(y).as_slice());
            // Neg is important.
            -Fr::from_bytes_wide(bs.as_slice().try_into().unwrap())
        })
        .collect();
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
    println!("mac: {:?}", mac_start.elapsed());

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

    println!("send: {:?}", send_start.elapsed());
    (multicast0_bs, multicast1_bs)
}

pub fn write(c: &WriteConfig, dif: &Dif, msg: grpc::Multicast) -> Vec<[u8; 1024]> {
    let write_start = Instant::now();

    let grpc::Multicast {
        share: share_opt,
        pm,
        mac_share,
    } = msg;
    let elem_num = c.n;
    let elem_bitlen = elem_num.next_power_of_two().trailing_zeros();
    let pm_c: PmapCompact = (pm, elem_num, elem_bitlen).into();
    let share = {
        let share = share_opt.unwrap();
        let grpc::DifShare {
            s0,
            cws_l,
            cw_np1_l,
            cws_r,
            cw_np1_r,
        } = share;
        dif::DifShare {
            s0s: vec![s0.try_into().unwrap()],
            cws_l: cws_l
                .into_iter()
                .map(|cw| dif::DifCw {
                    s: cw.s.try_into().unwrap(),
                    v: cw.v.try_into().unwrap(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_l: cw_np1_l.try_into().unwrap(),
            cws_r: cws_r
                .into_iter()
                .map(|cw| dif::DifCw {
                    s: cw.s.try_into().unwrap(),
                    v: cw.v.try_into().unwrap(),
                    tl: cw.tl,
                    tr: cw.tr,
                })
                .collect(),
            cw_np1_r: cw_np1_r.try_into().unwrap(),
        }
    };
    let t = SubgroupPoint::from_bytes(&mac_share.try_into().unwrap()).unwrap();

    let dif_eval_start = Instant::now();
    let mut ys = vec![[0; 1024]; elem_num.next_power_of_two() as usize];
    dif.full_eval(c.b, share, &mut ys);
    println!("dif eval: {:?}", dif_eval_start.elapsed());

    let mac_start = Instant::now();
    let ys_fr: Vec<_> = ys
        .par_iter()
        .enumerate()
        .map(|(_i, y)| {
            let mut bs = vec![0; 64];
            bs[..32].copy_from_slice(Sha256::digest(y).as_slice());
            let y_fr = Fr::from_bytes_wide(bs.as_slice().try_into().unwrap());
            y_fr
        })
        .collect();
    let y_points: Vec<_> = ys_fr
        .par_iter()
        .enumerate()
        .map(|(i, y_fr)| c.gw[pm_c.map(i as u32) as usize] * y_fr)
        .collect();
    let point_sum: SubgroupPoint = y_points.into_iter().sum();
    let beta = point_sum - t;
    let beta_other = black_box(-beta);
    assert_eq!(beta + beta_other, SubgroupPoint::identity());
    println!("mac: {:?}", mac_start.elapsed());

    println!("write: {:?}", write_start.elapsed());
    ys
}
