use bitvec::prelude::*;
use rand::prelude::*;
use rayon::prelude::*;

#[derive(Clone)]
pub struct PmapSparse {
    idxs: Vec<u32>,
    elem_num: u32,
}

impl PmapSparse {
    // Inclusive interval to avoid int overflow.
    // `elem_num` is between `$2^10$` and `$2^20$` in the experiment.
    pub fn new_from_all_map((l, r): (u32, u32), ys: &[u32], elem_num: u32) -> Self {
        assert_eq!((r - l + 1) as usize, ys.len());

        let mut y_idxs = ys.to_vec();
        y_idxs.shuffle(&mut thread_rng());
        let mut other_idxs: Vec<_> = (0..elem_num).filter(|&x| !y_idxs.contains(&x)).collect();
        other_idxs.shuffle(&mut thread_rng());

        let mut idxs = vec![0; elem_num as usize];
        let mut other_iter = other_idxs.iter();
        (0..l).for_each(|x| {
            idxs[x as usize] = *other_iter.next().unwrap();
        });
        (l..=r).zip(y_idxs.iter()).for_each(|(x, &y)| {
            idxs[x as usize] = y;
        });
        ((r + 1)..elem_num).for_each(|x| {
            idxs[x as usize] = *other_iter.next().unwrap();
        });

        assert_eq!(other_iter.next(), None);
        Self { idxs, elem_num }
    }
}

impl From<PmapSparse> for PmapCompact {
    fn from(value: PmapSparse) -> Self {
        let elem_bitlen = value.elem_num.next_power_of_two().trailing_zeros();
        assert_ne!(elem_bitlen, 0);
        let blk_bitlen = num::integer::lcm(u32::BITS, elem_bitlen);
        let blk_bvec_elem_num = blk_bitlen / u32::BITS;
        let blk_elem_num = blk_bitlen / elem_bitlen;
        let blk_num = (value.elem_num * elem_bitlen + blk_bitlen - 1) / blk_bitlen;

        let buf: Vec<_> = (0..blk_num)
            .into_par_iter()
            .map(|blk_idx| {
                let mut buf_bvec =
                    BitVec::<u32, Lsb0>::from_vec(vec![0u32; blk_bvec_elem_num as usize]);
                (0..blk_elem_num).for_each(|j| {
                    let i = blk_idx * blk_elem_num + j;
                    if i >= value.elem_num {
                        return;
                    }

                    buf_bvec
                        .get_mut((j * elem_bitlen) as usize..((j + 1) * elem_bitlen) as usize)
                        .unwrap()
                        .store_le(value.idxs[i as usize]);
                });
                buf_bvec.into_vec()
            })
            .flatten()
            .collect();

        let mut bvec = BitVec::from_vec(buf);
        bvec.resize((value.elem_num * elem_bitlen) as usize, false);
        Self {
            idxs: bvec,
            elem_num: value.elem_num,
            elem_bitlen,
        }
    }
}

#[derive(Clone)]
pub struct PmapCompact {
    idxs: BitVec<u32>,
    elem_num: u32,
    elem_bitlen: u32,
}

impl From<PmapCompact> for Vec<u8> {
    fn from(value: PmapCompact) -> Self {
        value
            .idxs
            .as_raw_slice()
            .iter()
            .flat_map(|&i| i.to_le_bytes().to_vec())
            .collect()
    }
}

impl From<(Vec<u8>, u32, u32)> for PmapCompact {
    fn from((value, elem_num, elem_bitlen): (Vec<u8>, u32, u32)) -> Self {
        let bitlen = (elem_num * elem_bitlen) as usize;
        assert!(bitlen <= value.len() * 8);
        let idxs = value
            .chunks_exact(4)
            .map(|chunk| u32::from_le_bytes(chunk.try_into().unwrap()))
            .collect::<Vec<_>>();
        let mut bvec = BitVec::from_vec(idxs);
        bvec.resize(bitlen, false);
        Self {
            idxs: bvec,
            elem_num,
            elem_bitlen,
        }
    }
}

impl PmapCompact {
    pub fn map(&self, x: u32) -> u32 {
        self.idxs
            .get((x * self.elem_bitlen) as usize..((x + 1) * self.elem_bitlen) as usize)
            .unwrap()
            .load_le()
    }
}

#[cfg(test)]
mod tests {
    use arbtest::arbtest;

    use super::*;

    #[test]
    fn test_map() {
        arbtest(|u| {
            let l: u32 = 100;
            let r: u32 = 199;

            let ys = (l..=r).collect::<Vec<_>>();
            let elem_num = 2u32.pow(20);
            let pmap_sparse = PmapSparse::new_from_all_map((l, r), &ys, elem_num);
            let pmap_compact0: PmapCompact = pmap_sparse.clone().into();
            let bs: Vec<u8> = pmap_compact0.clone().into();

            let pmap_compact1: PmapCompact = (bs, elem_num, pmap_compact0.elem_bitlen).into();
            for x in 0..elem_num {
                assert_eq!(pmap_compact0.map(x), pmap_compact1.map(x));
            }

            Ok(())
        });
    }
}
