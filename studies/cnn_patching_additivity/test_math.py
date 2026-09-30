import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import torch
from math_core import center_logits, decompose_set

torch.manual_seed(7)
N,J,C=11,16,4
l0=torch.randn(N,C)
l1=torch.randn(N,C)
# arbitrary singleton changes, with common-mode shifts included
D=torch.randn(N,J,C)*0.2
singleton=l0[:,None,:]+D
channels=torch.tensor([[0,1,4,7]]*N)
a=D[:,channels[0]].sum(1)
joint=l0+a
res=decompose_set(l0,l1,singleton,joint,channels,keep_pair_arrays=True)
assert res.summary['residual_max_abs_component'] < 1e-6
assert res.summary['raw_residual_max_abs_component'] < 1e-6
assert res.summary['identity_additive_direct_max_abs_error'] < 1e-10
assert res.summary['identity_additive_expanded_max_abs_error'] < 1e-10
assert res.summary['identity_nonadditive_correction_max_abs_error'] < 1e-10
# Introduce non-additive residual and verify exact correction.
r=torch.randn(N,C)*0.05
joint2=joint+r
res2=decompose_set(l0,l1,singleton,joint2,channels)
assert res2.summary['identity_nonadditive_correction_max_abs_error'] < 1e-10
# k=1 is exact by construction if the joint is the stored singleton.
ch1=torch.tensor([[3]]*N)
res1=decompose_set(l0,l1,singleton,singleton[:,3,:],ch1)
assert res1.summary['residual_max_abs_component'] < 1e-6
# k=0 identity with base.
ch0=torch.empty((N,0),dtype=torch.long)
res0=decompose_set(l0,l1,singleton,l0,ch0)
assert res0.summary['residual_max_abs_component'] < 1e-6
print('math_core self-test PASS')
