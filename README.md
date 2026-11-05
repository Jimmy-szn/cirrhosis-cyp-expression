## Selected Research Question:
"Do genes responsible for first-pass drug metabolism (such as CYP enzymes) show
significantly lower expression in cirrhotic livers compared to healthy livers?"
## Target Dataset Source:
NCBI GEO (Gene Expression Omnibus) – Microarray/RNA-seq gene expression matrices
comparing healthy human liver tissue against cirrhotic liver tissue.
## Project Objectives:
1. To acquire and preprocess a public gene expression dataset comparing healthy and
cirrhotic human livers from NCBI GEO.
2. To explore and visualize the data by comparing the expression levels of key
drug-metabolizing genes (such as CYP3A4) across healthy and diseased samples.
3. To train and evaluate a machine learning classification model to predict liver tissue
states based on these metabolic gene profiles.
4. To interpret the results and conclude how liver cirrhosis impacts drug-metabolizing
gene expression and first-pass metabolic capacity.
### GEO Candidate Dataset Evaluation Summary

| GEO Accession | Platform | Total Samples | Healthy Controls ($n$) | Cirrhosis Samples ($n$) | Confounding Groups / Exclusions | Meets $\ge 15$ Per Group Rule? | Verdict |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| **GSE14323** | GPL570 | 124 | **19** | **58** | 47 liver tissues with HCC (can be filtered) | **Yes** | **Selected** — Best sample balance & clear non-tumor subset. |
| **GSE139602** | GPL13667 | 39 | 6 | 20 | 5 eCLD, 8 ACLF; progressive disease staging | **No** | *Underpowered* — Healthy control group ($n=6$) is too small. |
| **GSE25097** | GPL10687 | 557 | 6 | 40 | 268 tumor, 243 non-tumor | **No** | *Underpowered* — Healthy control group ($n=6$) is too small. |
| **GSE6764** | GPL570 | 75 | 10 | 13 | 52 dysplasia / HCC stages | **No** | *Underpowered* — Neither group reaches $n=15$. |

## Project Progress and Roadmap

| Stage | Description | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| Stage 1 | Research Question Definition | Done | Formulated hypothesis on CYP gene downregulation in cirrhotic livers. |
| Stage 2 | Dataset Selection | Done | Selected GSE14323 (19 healthy, 58 cirrhosis). |
| Stage 3 | Preprocessing and QC | Done | Filtered low-variance probes (22,277 down to 20,049). |
| Stage 4 | Probe-to-Gene Mapping | Pending | Pending |
| Stage 5 | Differential Expression | Pending | Pending |
| Stage 6 | Visualization & EDA | Pending | Pending |
| Stage 7 | Machine Learning | Pending | Pending |
| Stage 8 | Documentation | Pending | Pending |
