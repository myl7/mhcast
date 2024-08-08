use ff::Field;
use jubjub::Fr;
use rand::prelude::*;
use tracing::{info, info_span};
use tracing_subscriber::fmt::format::FmtSpan;

use mhcast::dif::{DcfImplImpl, Dif, PrgImpl};
use mhcast::SendConfig;

fn main() {
    tracing_subscriber::fmt()
        .with_span_events(FmtSpan::CLOSE)
        .init();

    let dif_init_span = info_span!("dif_init").entered();
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
    drop(dif_init_span);

    let mut m = vec![0u8; 1024];
    thread_rng().fill_bytes(&mut m);
    let cm = 16;
    let w: Vec<_> = (0..16).map(|_| Fr::random(thread_rng())).collect();

    let (multicast0_bs, multicast1_bs) = mhcast::send(
        &SendConfig {
            n: 2u32.pow(17),
            m: cm,
            r: (10..10 + cm).collect(),
            w,
        },
        &dif,
        m.as_slice().try_into().unwrap(),
    );

    info!(
        "multicast size: {}",
        multicast0_bs.len() + multicast1_bs.len()
    );
}
