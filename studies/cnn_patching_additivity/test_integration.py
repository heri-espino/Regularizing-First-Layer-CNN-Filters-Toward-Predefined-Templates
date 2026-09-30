import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import torch
from torch import nn
import evaluate as ev
from math_core import decompose_set

class Tiny(nn.Module):
    def __init__(self, pooling='max'):
        super().__init__(); self.pooling=pooling; self.classifier=nn.Linear(16,4)
    def tail(self,h):
        z=h.amax((2,3)) if self.pooling=='max' else h.mean((2,3))
        return self.classifier(z)

torch.set_grad_enabled(False)
torch.manual_seed(1)
for pooling in ('max','avg'):
    model=Tiny(pooling).eval()
    # Synthetic post-ReLU maps: each channel is spatially constant. This makes
    # both max and average pooling channelwise linear under whole-channel swaps.
    H=torch.rand(12,16,5,5)
    # Three groups, four states each; use two directed changes per group.
    b=torch.tensor([0,1,4,5,8,9]); c=torch.tensor([1,0,5,4,9,8]); g=torch.tensor([0,0,1,1,2,2])
    pair=(b,c,g)
    order=np.vstack([np.arange(16),np.roll(np.arange(16),1),np.roll(np.arange(16),2)])
    l=model.tail(H); l0,l1=l[b],l[c]
    singles=ev.singleton_logits(model,H,pair,3,64)
    for k in range(17):
        joint=ev.patch_logits(model,H,order,k,pair,64).cpu()
        channels=ev.channel_sets_for_pairs(order,k,g.cpu())
        dec=decompose_set(l0,l1,singles,joint,channels)
        assert dec.summary['residual_max_abs_component'] < 2e-6, (pooling,k,dec.summary['residual_max_abs_component'])
print('tiny whole-channel additivity integration test PASS')
