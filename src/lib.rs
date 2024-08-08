mod dif;
mod pm;

use std::collections::HashMap;

use group::Group;
use jubjub::{Fr, SubgroupPoint};
use rand::prelude::*;
use sha2::{Digest, Sha256};

use dif::{DcfImplImpl, Dif, PrgImpl};
use pm::{PmapCompact, PmapSparse};

pub struct SendConfig {
    pub n: u32,
    pub m: u32,
    pub r: Vec<u32>,
    pub w: Vec<Fr>,
}

pub fn send(c: &SendConfig, m: &[u8; 1024]) {
    assert_eq!(c.r.len(), c.m as usize);

    let al = thread_rng().gen_range(0..=c.n);
    let ar = al + c.m + 1;

    let pm_s = PmapSparse::new_from_all_map((al, ar), &c.r, c.n);
    let mut cache = HashMap::new();
    for (&ri, w) in c.r.iter().zip(c.w.iter()) {
        cache.insert(ri, (pm_s.map(ri), w));
    }
    let pm_c: PmapCompact = pm_s.clone().into();

    let mut keys_l = vec![[0u8; 16]; 256];
    keys_l.iter_mut().for_each(|k| thread_rng().fill(k));
    let mut keys_r = vec![[0u8; 16]; 256];
    keys_r.iter_mut().for_each(|k| thread_rng().fill(k));
    let prg_l = PrgImpl::new(&std::array::from_fn(|i| &keys_l[i]));
    let prg_r = PrgImpl::new(&std::array::from_fn(|i| &keys_r[i]));
    let filter_bitn = 17;
    let dcf_l = DcfImplImpl::new_with_filter(prg_l, filter_bitn);
    let dcf_r = DcfImplImpl::new_with_filter(prg_r, filter_bitn);
    let dif = Dif(dcf_l, dcf_r);

    let mut s0s = vec![[0u8; 1024]; 2];
    s0s.iter_mut().for_each(|s0| thread_rng().fill(s0));

    let (k0, k1) = dif.gen((al, ar), m, std::array::from_fn(|i| &s0s[i]));

    let mut xs: Vec<u32> = (al + 1..ar).collect();
    let mut ys0 = vec![[0u8; 1024]; c.m as usize];
    let mut ys1 = vec![[0u8; 1024]; c.m as usize];
    dif.batch_eval(false, k0, &xs, &mut ys0);
    dif.batch_eval(true, k1, &xs, &mut ys1);

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
}
