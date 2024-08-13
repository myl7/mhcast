use fss_rs::dcf::{BoundState, CmpFn, Dcf, DcfImpl};
use fss_rs::group::byte::ByteGroup;
use fss_rs::group::Group;
use fss_rs::prg::Aes128MatyasMeyerOseasPrg;
use fss_rs::utils::xor_inplace;
use fss_rs::{Cw, Share};

pub type GroupImpl = ByteGroup<1024>;
pub type PrgImpl = Aes128MatyasMeyerOseasPrg<1024, 2, 256>;
pub type DcfImplImpl = DcfImpl<3, 1024, PrgImpl>;
pub type ShareImpl = Share<1024, GroupImpl>;
pub type CwImpl = Cw<1024, GroupImpl>;

pub struct Dif(pub DcfImplImpl, pub DcfImplImpl);

fn idx_to_alpha(x: u32) -> [u8; 3] {
    x.to_be_bytes()[..3].try_into().unwrap()
}

impl Dif {
    pub fn gen(
        &self,
        (l, r): (u32, u32),
        b: &[u8; 1024],
        s0s: [&[u8; 1024]; 2],
    ) -> (DifShare, DifShare) {
        let kl = self.0.gen(
            &CmpFn {
                alpha: idx_to_alpha(l),
                beta: [0; 1024].into(), // Let the life easier
                bound: BoundState::GtAlpha,
            },
            s0s,
        );
        let kr = self.1.gen(
            &CmpFn {
                alpha: idx_to_alpha(r),
                beta: b.clone().into(),
                bound: BoundState::LtAlpha,
            },
            s0s,
        );
        let mut share0 = DifShare::from((kl, kr));
        let mut share1 = share0.clone();
        share1.s0s = vec![share0.s0s.remove(1)];
        (share0, share1)
    }

    pub fn full_eval(&self, b: bool, k: DifShare, ys: &mut [[u8; 1024]]) {
        let mut ys_buf = vec![GroupImpl::zero(); ys.len()];
        let mut ys_iter: Vec<_> = ys_buf.iter_mut().collect();
        let (kl, kr) = k.into();
        self.0.full_eval(b, &kl, &mut ys_iter);
        drop(kl);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            *y = (*y_iter).clone().into();
        });
        self.1.full_eval(b, &kr, &mut ys_iter);
        drop(kr);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            xor_inplace(y, &[&((*y_iter).clone().into())]);
        });
    }

    pub fn batch_eval(&self, b: bool, k: DifShare, xs: &[u32], ys: &mut [[u8; 1024]]) {
        assert_eq!(xs.len(), ys.len());

        let mut ys_buf = vec![GroupImpl::zero(); ys.len()];
        let mut ys_iter: Vec<_> = ys_buf.iter_mut().collect();
        let xs_buf: Vec<_> = xs.iter().map(|&x| idx_to_alpha(x)).collect();
        let xs_iter: Vec<_> = xs_buf.iter().collect();
        let (kl, kr) = k.into();
        self.0.eval(b, &kl, &xs_iter, &mut ys_iter);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            *y = (*y_iter).clone().into();
        });
        self.1.eval(b, &kr, &xs_iter, &mut ys_iter);
        ys_iter.iter().zip(ys.iter_mut()).for_each(|(y_iter, y)| {
            xor_inplace(y, &[&((*y_iter).clone().into())]);
        });
    }
}

#[derive(Clone)]
pub struct DifShare {
    pub s0s: Vec<[u8; 1024]>,
    pub cws_l: Vec<DifCw>,
    pub cw_np1_l: [u8; 1024],
    pub cws_r: Vec<DifCw>,
    pub cw_np1_r: [u8; 1024],
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
    pub s: [u8; 1024],
    pub v: [u8; 1024],
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
