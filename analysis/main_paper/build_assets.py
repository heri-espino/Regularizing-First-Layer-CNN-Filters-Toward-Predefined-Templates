"""Build historical paper tables and plots from existing analyses; no new model evaluation."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
r=pd.read_csv(ROOT/'analysis/patch_robustness_gpu_001/paired_contrasts.csv')
assert len(r)==96
fig,axes=plt.subplots(2,4,figsize=(18,8),sharex=True,sharey='row')
settings=[(t,a) for t in ['single_shape','two_concepts'] for a in ['TinyCNN','TwoLayerCNN']]
for j,(task,arch) in enumerate(settings):
 for i,metric in enumerate(['causal_usefulness','cf_accuracy']):
  ax=axes[i,j]
  for shift,method,color in zip([-.12,0,.12],['contrast','auroc','validation_patch'],['#3465a4','#c97800','#8056a6']):
   s=r[(r.task==task)&(r.architecture==arch)&(r.metric==metric)&(r.method==method)].sort_values('k')
   assert s.k.tolist()==[1,2,4,8]
   ax.errorbar(np.arange(4)+shift,s['mean'],yerr=[s['mean']-s.ci_low,s.ci_high-s['mean']],label=method,marker='o',capsize=3,color=color)
  ax.axhline(0,color='grey',ls='--',lw=1);ax.set_xticks(range(4));ax.set_xticklabels([1,2,4,8]);ax.grid(alpha=.15)
  if i==0:ax.set_title(task+'\n'+arch)
  else:ax.set_xlabel('Patched channels')
axes[0,0].set_ylabel('Release − constant: U');axes[1,0].set_ylabel('Release − constant: CF accuracy')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='lower center',ncol=3)
fig.suptitle('All settings and channel sizes; exploratory marginal 95% paired t intervals (10 blocks)')
fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(OUT/'all_robustness.png',dpi=180);plt.close(fig)
text=['# Historical supplementary tables','', 'These tables reproduce existing analyses without new statistical tests. Values are not selected by significance.','', '## S1. All prospective primary contrasts','']
p=pd.read_csv(ROOT/'studies/cnn_causal_milestone/analysis/primary_contrasts.csv');assert len(p)==4
text+=['| Setting | ΔU [marginal 95% CI] | Raw p | Holm p | Δalignment | Δaccuracy (pp) |','|---|---:|---:|---:|---:|---:|']
for _,v in p.iterrows():text.append(f"| {v.task} / {v.architecture} | {v['mean']:+.4f} [{v.lo:+.4f}, {v.hi:+.4f}] | {v.p:.4f} | {v.p_holm:.4f} | {v.alignment_delta:+.3f} | {100*v.accuracy_delta:+.2f} |")
text+=['','## S2. All 200-epoch condition means','', 'Mean ± sample SD across ten blocks. All five conditions and all four settings are shown. Accuracy is a percentage; U, alignment, AUROC and IoU are dimensionless.','', '| Setting | Condition | Accuracy (%) | Alignment | Concept AUROC | Localization IoU | U | Selected CF accuracy (%) |','|---|---|---:|---:|---:|---:|---:|---:|']
e=pd.read_csv(ROOT/'analysis/retention_release_001/endpoints.csv')
for (task,arch,condition),s in e.groupby(['task','architecture','condition']):
 vals=[]
 for metric,scale in [('id_acc',100),('alignment',1),('semantic_auc',1),('localization_iou',1),('causal_usefulness',1),('cf_accuracy',100)]:
  vals.append(f'{s[metric].mean()*scale:.3f} ± {s[metric].std()*scale:.3f}')
 text.append('| '+task+' / '+arch+' | '+condition+' | '+' | '.join(vals)+' |')
text+=['','## S3. Complete measurement-sensitivity contrasts','', 'Release minus constant retention. All 96 contrasts: 4 settings × 3 rankings × 4 sizes × 2 outcomes. Intervals are marginal 95% paired t intervals; no multiplicity adjustment.','']
for metric in ['causal_usefulness','cf_accuracy']:
 text+=['### '+metric,'','| Setting | Ranking | k | Mean difference | 95% interval |','|---|---|---:|---:|---:|']
 for _,v in r[r.metric==metric].iterrows():text.append(f"| {v.task} / {v.architecture} | {v.method} | {int(v.k)} | {v['mean']:+.4f} | [{v.ci_low:+.4f}, {v.ci_high:+.4f}] |")
 text+=['']
text+=['## Data and analysis map','', '- Prospective raw per-run results: `studies/cnn_causal_milestone/analysis/per_run.csv`.','- Retention-release: `analysis/retention_release_001/endpoints.csv` and `paired_contrasts.csv`.','- Robustness raw method/size data: `results/patch_robustness_gpu_001/analysis/metrics.csv`.','- Rebuild with `python analysis/main_paper/build_assets.py`.']
(OUT/'supplementary_results.md').write_text('\n'.join(text)+'\n')
print('Saved historical tables and all-setting sensitivity figure.')
