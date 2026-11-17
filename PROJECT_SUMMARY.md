# Project Summary: Drug-Metabolism Gene Expression in Cirrhotic vs Healthy Liver

## What this project is about

This is a group bioinformatics project that asks:

> **Do genes responsible for first-pass drug metabolism (such as CYP enzymes) show significantly lower expression in cirrhotic livers compared to healthy livers?**

The liver clears many oral drugs before they reach the bloodstream ("first-pass metabolism"), mainly through cytochrome P450 (CYP) enzymes, Phase II conjugating enzymes (UGT, SULT, GST) and drug transporters. If cirrhosis lowers expression of these genes, drug exposure in cirrhotic patients could rise. The project tests this idea with public gene expression data from NCBI GEO.

### Objectives
1. Get and preprocess a public GEO dataset that compares healthy and cirrhotic human liver.
2. Explore and visualise the expression of key drug-metabolising genes in each group.
3. Train and evaluate a machine learning classifier that predicts liver state from metabolic gene profiles. *(planned)*
4. Interpret what the results mean for first-pass metabolic capacity in cirrhosis.

---

## Repository layout

| Path | Contents |
| :--- | :--- |
| `README.md` | Research question, objectives, dataset comparison and stage roadmap |
| `notebooks/main.ipynb` | The full analysis pipeline, written for Google Colab (acquisition → QC → EDA → differential expression → biological interpretation) |
| `mainplusoutput.ipynb` | Copy of the notebook with all outputs, including Stage 6 |
| `STAGE6_BIOLOGICAL_INTERPRETATION.md` | Plain-language guide to Stage 6 and its results |
| `figures/` | Saved plots from EDA (`eda1`–`eda6`), core analysis (`ca_differential-exp.png`, `ca_effect-sizes.png`) and biological interpretation (`bioint1`–`bioint4`) |
| `notebooks/.gitignore` | Excludes GEO downloads (`geodata/`, `*.soft.gz`) and notebook checkpoints inside `notebooks/` |

**Tools:** Python (run in Google Colab) with `GEOparse`, `pandas`, `numpy`, `scipy`, `scikit-learn` (PCA, scaling), `matplotlib` and `seaborn`. Stage 6 adds `gseapy` (pathway enrichment) and `statsmodels` (adjusted regression). `pydeseq2` is installed but deliberately not used, because the data are normalised microarray intensities rather than RNA-seq counts.

---

## Pipeline (what the notebook does)

### 1. Dataset selection
Four GEO series were downloaded and screened. Samples were sorted into healthy and cirrhosis groups using their metadata, and each series was checked against a rule of at least 15 samples per group:

| GEO Accession | Healthy | Cirrhosis | Notes | Verdict |
| :--- | :---: | :---: | :--- | :--- |
| **GSE14323** | 19 | 58 | 47 HCC tumour samples, which can be filtered out | **Selected** |
| GSE139602 | 6 | 20 | Disease-staging cohort (eCLD, ACLF) | Too few controls |
| GSE25097 | 6 | 40 | Mostly tumour / non-tumour pairs | Too few controls |
| GSE6764 | 10 | 13 | Dysplasia and HCC stages | Both groups too small |

### 2. Preprocessing and QC (GSE14323)
- HCC samples were removed, leaving **60 samples (19 healthy, 41 cirrhosis)**, all on the Affymetrix GPL571 platform.
- Values were already log2-scaled (range 3.5–14.4), so no transformation was needed.
- Missing values were dropped and the lowest-variance 10% of probes were filtered out: **22,277 → 20,049 probes**.
- Probes were mapped to gene symbols. Where several probes matched one gene, the probe with the highest mean expression was kept, giving **12,316 unique genes**.

### 3. Exploratory data analysis
A 17-gene **drug-metabolism panel** was defined:
- **Phase I:** CYP3A4, CYP3A5, CYP2C9, CYP2C19, CYP2D6, CYP1A2, CYP2E1
- **Phase II:** UGT1A1, UGT2B7, GSTA1, SULT1A1, SULT1A2, SULT1E1, SULT2A1
- **Transporters:** ABCB1, SLCO1B1, SLC22A1

UGT2B7 is not on the chip, so 16 genes were analysed. Key EDA findings:
- Sample distributions are consistent, so samples are comparable.
- **PCA:** PC1 (23.6% of variance) separates healthy from cirrhotic samples. There is no platform batch effect and no outliers beyond 3 SD.
- Samples cluster by group in the sample-correlation map. All mean correlations are above 0.91.
- Sanity checks passed: liver markers (APOA1, CYP3A4, ALB) are highly expressed, and the sex genes (XIST and RPS4Y1) split cleanly.
- Panel genes move in **both** directions. This was an early sign that H1 would not hold uniformly.

### 4. Core analysis: differential expression
- **Method:** Welch's t-test per gene (cirrhosis vs healthy), Benjamini–Hochberg FDR, log2 fold change, 95% CI and Hedges' g effect size. A one-sided test of H1 and a Mann–Whitney U check were run as secondary analyses.
- **Genome-wide:** 7,845 of 12,316 genes are significant (FDR < 0.05): 4,325 down and 3,520 up in cirrhosis. 2,121 genes also pass |log2FC| ≥ 0.58 (1.5-fold).

**Panel results:**

| Direction | Genes |
| :--- | :--- |
| **Significantly lower in cirrhosis (3)** | CYP2C19 (−1.63 log2), CYP1A2 (−0.97), CYP2E1 (−0.64, the strongest evidence) |
| **Significantly higher in cirrhosis (5)** | GSTA1 (+2.13), ABCB1 (+0.90), SULT1A1, SULT1A2, CYP3A4* |
| **Not significant (8)** | CYP3A5, CYP2C9, CYP2D6, UGT1A1, SULT1E1, SULT2A1, SLCO1B1, SLC22A1 |

\*Individual CYP3A4 probes disagree with each other, so the apparent increase is treated as unreliable.

**Robustness checks:**
- Re-running with all 58 cirrhosis samples (adding the 17 "cirrhosis + HCC" samples) gave almost the same results. CYP2D6 also becomes significantly lower in that version, but only borderline.
- The non-parametric tests broadly agree with the t-tests.

### 5. Biological interpretation (Stage 6)
- **Methods:** over-representation analysis (ORA) of the 739 down- and 1,382 upregulated genes against GO Biological Process 2023 and KEGG 2021, using the 12,316 tested genes as the background. Pre-ranked GSEA by t-statistic on KEGG. A focused drug-metabolism pathway table. Cell-type scores with a hepatocyte-adjusted re-test of the panel. A clinical mapping of panel genes to drugs.

**Results:**

| Question | Finding |
| :--- | :--- |
| Drug metabolism as a pathway? | *Metabolism of xenobiotics by cytochrome P450* is slightly **up** (NES +1.44, FDR 0.086; 6 genes down and 18 up of 51). Steroid hormone biosynthesis and retinol metabolism are flat (FDR 1). KEGG *Drug metabolism – cytochrome P450* and *– other enzymes* are **missing from the library** and were not tested. |
| Down in cirrhosis (52 ORA terms) | ER protein processing (FDR 6e-15; GSEA NES −2.15), N-glycan biosynthesis, protein export, cholesterol/steroid synthesis, complement and coagulation, amino-acid metabolism |
| Up in cirrhosis (420 ORA terms; 127 of 138 GSEA hits) | Immune and inflammatory signalling (T-cell receptor, antigen presentation, chemokines, phagosome) and remodelling (cell migration, focal adhesion) |
| Cell composition | Hepatocyte score not different (p = 0.24). Fibrosis (p = 4.5e-14), ductular (p = 3e-28) and immune (p = 8.4e-26) scores are much higher in cirrhosis. |
| Hepatocyte-adjusted panel | CYP2C19 (−1.52), CYP1A2 (−0.79) and CYP2E1 (−0.58) stay significantly lower. In total, 5 genes are down and 8 up (newly significant: SLC22A1, SULT1E1 down; UGT1A1, CYP3A5, CYP2C9 up; all small effects). |

Figures: `bioint1_ora_dotplot.png`, `bioint2_gsea_kegg.png`, `bioint3_drug_pathway_gsea.png`, `bioint4_cell_composition.png`. Tables in `results/`: `enrichment_ora.csv`, `enrichment_gsea_kegg.csv`, `drug_metabolism_pathways.csv`, `panel_cell_composition_adjusted.csv`, `panel_clinical_mapping.csv`. See `STAGE6_BIOLOGICAL_INTERPRETATION.md` for a plain-language guide.

---

## Conclusion so far

**H1 is only partly supported.** Cirrhosis clearly lowers several Phase I CYP enzymes (CYP2C19, CYP1A2, CYP2E1), and this drop holds after adjusting for hepatocyte content. It does **not** lower drug metabolism across the board: some Phase II enzymes (GSTA1, SULTs) and the efflux transporter ABCB1 go up, and the xenobiotic-metabolism pathway as a whole is not reduced. The rise in ABCB1 and GSTA1 may reflect the large expansion of ductular cells, or stress responses.

The wider biological picture is **loss of hepatocyte synthetic and secretory function** (protein processing, clotting factors, cholesterol) together with **immune infiltration, ductular expansion and fibrosis**. Clinically, lower CYP2C19, CYP1A2 and CYP2E1 suggests slower clearance of drugs such as omeprazole, diazepam, theophylline and clozapine, and weaker activation of clopidogrel.

---

## Project status

| Stage | Description | Status |
| :--- | :--- | :--- |
| 1 | Research question | Done |
| 2 | Dataset selection (GSE14323) | Done |
| 3 | Preprocessing and QC | Done |
| 4 | Probe-to-gene mapping | Done |
| 5 | EDA and differential expression | Done |
| 6 | Biological interpretation (enrichment, GSEA, cell-composition check and clinical mapping) | Done |
| 7 | Machine learning classifier (healthy vs cirrhosis) | Not started |
| 8 | Documentation | In progress |

## Known caveats and notes
- **Group sizes:** the cirrhosis group has 41 samples, not the 58 listed in the README, because 17 "cirrhosis + HCC" samples are excluded by the HCC filter. The groups are also unbalanced (19 vs 41).
- **Platform:** GSE14323 samples are on **GPL571** (plus 9 HCC samples on GPL96). The README originally said GPL570; this is now corrected.
- **Missing KEGG pathways:** *Drug metabolism – cytochrome P450* and *Drug metabolism – other enzymes* are not in Enrichr's KEGG_2021_Human library. A different library version or a direct KEGG gene list would be needed to test them.
- **Hepatocyte score:** it is built from plasma-protein genes, so it may not track hepatocyte numbers perfectly.
- **Missing metadata:** samples have no recorded sex, age or cause of disease, and the sex mix looks different between groups.
- **Missing gene:** UGT2B7 is not on the array.
- **Untracked outputs:** the notebook writes result tables (`de_all_genes.csv`, `de_panel_genes.csv`, `downregulated_genes.txt`, plus the Stage 6 tables) to a `results/` folder that is not in the repository.
