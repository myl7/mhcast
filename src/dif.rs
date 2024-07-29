use fss_rs::dcf::{BoundState, CmpFn, Dcf, DcfImpl};
use fss_rs::group::int_prime::{U128Group, PRIME_MAX_LE_U128_MAX};
use fss_rs::prg::Aes128MatyasMeyerOseasPrg;
use fss_rs::{Cw, Share};

pub type GroupImpl = U128Group<PRIME_MAX_LE_U128_MAX>;
pub type PrgImpl = Aes128MatyasMeyerOseasPrg<16, 2, 4>;
pub type DcfImplImpl = DcfImpl<3, 16, PrgImpl>;
pub type ShareImpl = Share<16, GroupImpl>;
pub type CwImpl = Cw<16, GroupImpl>;

pub struct Dif(pub DcfImplImpl, pub DcfImplImpl);

fn idx_to_alpha(x: u32) -> [u8; 3] {
    x.to_be_bytes()[..3].try_into().unwrap()
}

impl Dif {
    pub fn gen(&self, (l, r): (u32, u32), b: u128, s0s: [&[u8; 16]; 2]) -> (DifShare, DifShare) {
        let kl = self.0.gen(
            &CmpFn {
                alpha: idx_to_alpha(l),
                beta: [0; 16].into(), // Let the life easier
                bound: BoundState::GtAlpha,
            },
            s0s,
        );
        let kr = self.1.gen(
            &CmpFn {
                alpha: idx_to_alpha(r),
                beta: b.into(),
                bound: BoundState::LtAlpha,
            },
            s0s,
        );
        let mut share0 = DifShare::from((kl, kr));
        let mut share1 = share0.clone();
        share1.s0s = vec![share0.s0s.remove(1)];
        (share0, share1)
    }

    pub fn full_eval(&self, b: bool, k: DifShare, ys: &mut [u128]) {
        let mut ys_buf = vec![GroupImpl::from([0; 16]); ys.len()];
        let mut ys_iter: Vec<_> = ys_buf.iter_mut().collect();
        let (kl, kr) = k.into();
        self.0.full_eval(b, &kl, &mut ys_iter);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            *y = (*y_iter).clone().into();
        });
        self.1.full_eval(b, &kr, &mut ys_iter);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            let mut y_g: GroupImpl = (*y).into();
            y_g += (*y_iter).clone();
            *y = y_g.into();
        });
    }
}

#[derive(Clone)]
pub struct DifShare {
    pub s0s: Vec<[u8; 16]>,
    pub cws_l: Vec<DifCw>,
    pub cw_np1_l: u128,
    pub cws_r: Vec<DifCw>,
    pub cw_np1_r: u128,
}

impl From<(ShareImpl, ShareImpl)> for DifShare {
    fn from((kl, kr): (ShareImpl, ShareImpl)) -> Self {
        assert_eq!(kl.s0s, kr.s0s);
        let s0s = kl.s0s;
        let cws_l = kl.cws.into_iter().map(|cw| cw.into()).collect();
        let cw_np1_l = kl.cw_np1.into();
        let cws_r = kr.cws.into_iter().map(|cw| cw.into()).collect();
        let cw_np1_r = kr.cw_np1.into();
        DifShare {
            s0s,
            cws_l,
            cw_np1_l,
            cws_r,
            cw_np1_r,
        }
    }
}

impl From<DifShare> for (ShareImpl, ShareImpl) {
    fn from(share: DifShare) -> Self {
        let kl = ShareImpl {
            s0s: share.s0s.clone(),
            cws: share.cws_l.into_iter().map(|cw| cw.into()).collect(),
            cw_np1: share.cw_np1_l.into(),
        };
        let kr = ShareImpl {
            s0s: share.s0s,
            cws: share.cws_r.into_iter().map(|cw| cw.into()).collect(),
            cw_np1: share.cw_np1_r.into(),
        };
        (kl, kr)
    }
}

#[derive(Clone)]
pub struct DifCw {
    pub s: [u8; 16],
    pub v: u128,
    pub tl: bool,
    pub tr: bool,
}

impl From<CwImpl> for DifCw {
    fn from(cw: CwImpl) -> Self {
        DifCw {
            s: cw.s,
            v: cw.v.into(),
            tl: cw.tl,
            tr: cw.tr,
        }
    }
}

impl From<DifCw> for CwImpl {
    fn from(cw: DifCw) -> Self {
        CwImpl {
            s: cw.s,
            v: cw.v.into(),
            tl: cw.tl,
            tr: cw.tr,
        }
    }
}

#[cfg(test)]
mod tests {
    use arbtest::arbtest;

    use super::*;

    #[test]
    fn test_correctness() {
        arbtest(|u| {
            let keys: [[u8; 16]; 4] = u.arbitrary()?;
            let prg_l = PrgImpl::new(&std::array::from_fn(|i| &keys[i]));
            let prg_r = PrgImpl::new(&std::array::from_fn(|i| &keys[i]));
            let filter_bitn = 20;
            let dcf_l = DcfImplImpl::new_with_filter(prg_l, filter_bitn);
            let dcf_r = DcfImplImpl::new_with_filter(prg_r, filter_bitn);
            let dif = Dif(dcf_l, dcf_r);
            let s0s: [[u8; 16]; 2] = u.arbitrary()?;
            let (mut l, mut r): (u32, u32) = u.arbitrary()?;
            l = l % 2u32.pow(20);
            r = r % 2u32.pow(20);
            if l > r {
                std::mem::swap(&mut l, &mut r);
            }
            let b: u128 = u.arbitrary()?;

            let (k0, k1) = dif.gen((l, r), b, std::array::from_fn(|i| &s0s[i]));

            let mut ys0 = vec![0; 2u32.pow(20) as usize];
            let mut ys1 = vec![0; 2u32.pow(20) as usize];
            dif.full_eval(false, k0.clone(), &mut ys0);
            dif.full_eval(true, k1.clone(), &mut ys1);

            let mut ys = ys0;
            ys.iter_mut().zip(ys1.iter()).for_each(|(y, y1)| {
                let mut y_g: GroupImpl = (*y).into();
                y_g += (*y1).into();
                *y = y_g.into();
            });
            for x in 0..2u32.pow(20) {
                if x <= l {
                    assert_eq!(ys[x as usize], 0, "x = {}", x);
                } else if x >= r {
                    assert_eq!(ys[x as usize], 0, "x = {}", x);
                } else {
                    assert_eq!(ys[x as usize], b, "x = {}", x);
                }
            }
            Ok(())
        });
    }
}
