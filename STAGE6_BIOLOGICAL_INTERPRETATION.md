# Stage 6: Biological Interpretation

**Status:** done. The code is in `notebooks/main.ipynb` (section *6. Biological Interpretation*), and the run with all outputs is in `mainplusoutput.ipynb`. To re-run, run the whole notebook from the top in Colab, because Stage 6 uses the variables made in Stages 3–5.

## Why this stage exists

Stage 5 tested each gene on its own and found that the hypothesis (H1) is only **partly supported**:
- **3 drug-metabolism genes are lower in cirrhosis:** CYP2C19, CYP1A2 and CYP2E1.
- **5 are higher:** GSTA1, ABCB1, SULT1A1, SULT1A2 and CYP3A4 (the CYP3A4 result is unreliable).
- **8 show no significant change.**

Stage 6 asks the follow-up questions:
1. Is drug metabolism lower **as a whole pathway**, not just in a few genes?
2. Which biological processes change most in cirrhosis?
3. Are the changes real changes inside liver cells, or do cirrhotic samples simply contain fewer liver cells?
4. What could this mean for drugs given to patients?

## What each step does

| Step | Method | Question it answers | Output |
| :--- | :--- | :--- | :--- |
| 6.1 | **Over-representation analysis (ORA):** hypergeometric test against GO Biological Process 2023 and KEGG 2021, with the 12,316 tested genes as the background | Which pathways are overrepresented among the strongly down- (or up-) regulated genes? | `bioint1_ora_dotplot.png`, `enrichment_ora.csv` |
| 6.2 | **Pre-ranked GSEA:** all genes ranked by Stage 5 t-statistic, tested against KEGG | Which pathways shift as a group, even if each gene moves only a little? (Negative NES = lower in cirrhosis) | `bioint2_gsea_kegg.png`, `enrichment_gsea_kegg.csv` |
| 6.3 | **Drug-metabolism focus:** results pulled out for *Drug metabolism – cytochrome P450*, *Metabolism of xenobiotics by cytochrome P450*, *Drug metabolism – other enzymes*, *Glutathione metabolism*, *ABC transporters*, *Bile secretion* and others | The pathway-level answer to the research question | `bioint3_drug_pathway_gsea.png`, `drug_metabolism_pathways.csv` |
| 6.4 | **Cell-composition check:** per-sample scores for hepatocyte, fibrosis, ductular and immune marker genes. Panel genes are re-tested with `expression ~ cirrhosis + hepatocyte score` | Is a drop caused by less expression per liver cell, or by fewer liver cells in the sample? | `bioint4_cell_composition.png`, `panel_cell_composition_adjusted.csv` |
| 6.5 | **Clinical mapping:** each panel gene linked to example drugs | What might the changes mean for dosing? | `panel_clinical_mapping.csv` |
| 6.6 | **Summary:** one cell prints the key numbers, and a markdown cell has *[...]* placeholders to fill in | The written interpretation | Notebook text |

Figures are saved to `figures/` and tables to `results/`.

## Key choices
- **Background = tested genes only.** Using the whole genome as the background would make liver genes look enriched just because the chip measures them.
- **Both ORA and GSEA.** ORA looks at the strongest hits. GSEA uses every gene, so it can detect a pathway that drifts down overall.
- **GSEA cut-off of FDR < 0.25.** This is the standard threshold for GSEA. ORA keeps FDR < 0.05.
- **Marker genes in 6.4 are kept separate from the drug panel**, so the adjustment does not explain a gene using itself.

## Results

**Gene lists:** 739 genes are strongly down and 1,382 strongly up (FDR < 0.05 and |log2FC| ≥ 0.58), out of 12,316 tested.

### 6.1–6.2: What changes in cirrhosis
- **Down (52 significant ORA terms):** the hepatocyte's protein-making and secretion machinery. This includes protein processing in the ER (ORA FDR 6.2e-15; GSEA NES −2.15), N-glycan biosynthesis, protein export and ER stress/ERAD. Next come sterol/cholesterol and steroid biosynthesis, complement and coagulation cascades, and amino-acid, propanoate and peroxisome metabolism.
- **Up (420 significant ORA terms; 127 of 138 GSEA pathways with FDR < 0.25):** immune and inflammatory signalling (T-cell receptor, antigen presentation, chemokines, phagosome) and tissue remodelling (cell migration, focal adhesion, cell adhesion molecules). KEGG "disease" terms such as *viral myocarditis* or *allograft rejection* appear only because they share immune/MHC genes.
- **Expectation check:** the downregulated side matched expectations (liver synthetic function). The upregulated side was more immune-driven than collagen-driven.

### 6.3: Drug-metabolism pathways (the research question)
| Pathway | Genes tested | Down / Up | GSEA NES | GSEA FDR |
| :--- | :---: | :---: | :---: | :---: |
| Metabolism of xenobiotics by cytochrome P450 | 51 | 6 / 18 | **+1.44** | 0.086 |
| Bile secretion | 68 | 15 / 22 | +1.36 | 0.127 |
| ABC transporters | 35 | 14 / 11 | +1.24 | 0.249 |
| Glutathione metabolism | 45 | 10 / 16 | +1.18 | 0.339 |
| Retinol metabolism | 40 | 12 / 10 | −0.67 | 1.0 |
| Steroid hormone biosynthesis | 41 | 11 / 9 | −0.57 | 1.0 |

- **No pathway-level drop.** The xenobiotic-metabolism pathway leans slightly **up**, so H1 is not supported at the pathway level. To see which genes drive this, check the `Lead_genes` column in `enrichment_gsea_kegg.csv`.
- **Two pathways could not be tested.** KEGG *Drug metabolism – cytochrome P450* and *Drug metabolism – other enzymes* are not in Enrichr's KEGG_2021_Human library.

### 6.4: Cell composition
| Score | Healthy vs cirrhosis |
| :--- | :--- |
| Hepatocyte | No difference (p = 0.24) |
| Fibrosis | Much higher in cirrhosis (p = 4.5e-14) |
| Ductular | Much higher in cirrhosis (p = 3e-28) |
| Immune | Much higher in cirrhosis (p = 8.4e-26) |

- **The CYP drops are not explained by hepatocyte loss.** After adjusting for the hepatocyte score, CYP2C19 (−1.52 log2, FDR 0.0003), CYP1A2 (−0.79, FDR 0.019) and CYP2E1 (−0.58, FDR < 0.0001) all stay significantly lower, with similar sizes.
- **More panel genes reach significance after adjustment:** 13 of 16 in total, 5 down and 8 up. The new ones (SLC22A1 and SULT1E1 down; UGT1A1, CYP3A5 and CYP2C9 up) all have small effects (|log2FC| ≤ 0.52).
- **Ductular cells may explain the rises.** The big rise in the ductular score fits the idea that expanding bile-duct cells drive the rise in ABCB1 and GSTA1. This is a hypothesis, not directly tested.

### 6.5: Clinical meaning
Lower CYP2C19, CYP1A2 and CYP2E1 suggests slower clearance of omeprazole, diazepam, theophylline and clozapine, and weaker activation of the prodrug clopidogrel. Lower CYP2E1 plus higher GSTA1 may reduce the build-up of NAPQI, the toxic metabolite of paracetamol.

### Bottom line
Cirrhosis does **not** shut down drug metabolism as a whole. It selectively lowers specific CYPs, and this holds up after adjusting for hepatocyte content. The larger story is loss of hepatocyte synthetic and secretory function, plus immune infiltration, ductular expansion and fibrosis.

## Possible follow-ups
- Test the two missing KEGG drug pathways using another library (e.g. `KEGG_2019_Human`) or a gene list taken directly from KEGG.
- Adjust the panel for the ductular and immune scores to test the ductular-cell explanation for ABCB1 and GSTA1.
- Use the fibrosis, ductular and immune scores as features in Stage 7.

## Limitations
- Two core KEGG drug pathways were not tested because they are missing from the library.
- Bulk tissue measures a mix of cell types.
- The hepatocyte score is built from plasma-protein genes, so it may not track hepatocyte numbers perfectly.
- Samples have no sex, age or cause-of-disease data.
- The groups are unbalanced (19 vs 41).
- mRNA levels are not the same as enzyme activity.
- CYP3A4 probes disagree with each other, and UGT2B7 is not on the chip.

---

## ELI5: Explain it like I'm 5

Your liver is like a **big kitchen** that cleans up medicines after you swallow them. The kitchen has lots of **workers** (genes), and each worker has a special job, like chopping or washing up.

In **Stage 5**, we counted the workers one by one in healthy kitchens and in **damaged kitchens** (cirrhosis). Some cleaning workers went missing, some new ones turned up, and most stayed the same.

In **Stage 6**, we step back and ask bigger questions:

- **Which teams are short-staffed?** Workers belong to teams, like the "medicine-cleaning team" and the "fat-cooking team". We check whether a whole team is smaller, not just one worker. That's **pathway enrichment**.
- **Is the whole team a bit quieter?** Sometimes every worker on a team does just a little less work. No one person stands out, but together it adds up. That's **GSEA**.
- **Is the kitchen just smaller?** A damaged kitchen has scar tissue, like broken walls, where there used to be cooks. If we count fewer cleaners, is it because each cook is lazier, or because there are fewer cooks? We check how many cooks are left. That's the **cell-composition check**.
- **What does it mean for medicine?** If the cleaners for a certain medicine are missing, that medicine stays in your body longer. Doctors may need to give a smaller dose. That's the **clinical mapping**.

**What we found:** The damaged kitchen hasn't lost its cooks. There are about as many as before, but the room is now crowded with **security guards** (immune cells), **builders** (scar tissue) and **plumbers** (bile-duct cells). The cooks are making less of their usual food, like the proteins and clotting helpers the body needs. Most of the medicine-cleaning team is still working, and some members even work harder. But three important cleaners (CYP2C19, CYP1A2 and CYP2E1) really are working less, even after we counted the cooks. So some medicines get cleaned up more slowly, and doctors may need to give smaller doses of those ones.

**In one sentence:** Stage 6 turns a list of "this gene went up, that gene went down" into a story about which liver jobs break in cirrhosis, and what that means for the medicines people take.
