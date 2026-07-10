---
layout: post
title: Evaluating Robust Retrieval Pipelines
description: An undergraduate engineering thesis investigating the robustness of Information Retrieval (IR) pipelines, specifically Pretrained Language Models (PLMs), against query variations. The project involved generating adversarial and semantic query variations and evaluating their impact on state-of-the-art neural ranking models.
skills:

* Information Retrieval (IR)
* Pretrained Language Models (PLMs)
* Natural Language Processing (NLP)
* Large Language Models (LLMs)
* Data Wrangling (Pandas, ir_datasets)
* Neural Network Training
* Distributed Workloads (Google Colab)
main-image: /assets/images/thesis-retrieval.png

---

# Evaluating Robust Retrieval Pipelines

> "Modern search engines seem practically omniscient—until you ask them the exact same question in a slightly different way. Then, state-of-the-art models can silently fail."

## Project Overview & Scope

As part of my Bachelor of Engineering (Honours) in Computer Systems / Electrical and Electronic Engineering at the University of Queensland, I undertook a year-long thesis project focusing on **Information Retrieval (IR) systems**.

Modern search engines and IR pipelines increasingly rely on Pretrained Language Models (PLMs) to rank documents. However, these systems are typically benchmarked against a single standard query for a given information need. This ignores the vast diversity in human expression, leading to a critical question: *How brittle are these advanced ranking architectures in the real world?*

> **Image Suggestion**: *Insert a bar chart or line graph here comparing the baseline performance (e.g., MRR@10 or NDCG@10) of a standard query versus the degraded performance of the varied queries across different models. Visualizing this sharp drop makes the structural problem immediately tangible to a technical recruiter.*

This project aimed to rigorously evaluate robustness by generating novel and established query variations—while strictly maintaining core semantic meaning—and quantifying the resulting performance degradation across multiple search architectures.

---

## Core Objectives & Methodology

The bulk of my efforts centered around **generating varied search queries and determining their retrieval effects**.

### Datasets & Baselines

I utilized industry-standard datasets, including **MS MARCO & ANTIQUE**, to ensure evaluations were grounded in realistic, large-scale search scenarios. By leveraging libraries like `ir_datasets` and `pandas`, I aligned, parsed, and cleaned variations from existing databases (such as G. Penha's repository) alongside my own dynamically generated queries.

```python
# Snippet: Processing variations and managing query datasets
import pandas as pd
import ir_datasets

# Load MS MARCO train queries 
dataset = ir_datasets.load("msmarco-passage/train")
queries_df = pd.DataFrame(dataset.queries_iter())

def apply_lexical_perturbation(query_text):
    # Apply lemmatization or targeted character deletion
    # to simulate user typos and morphological shifts
    # ... 
    return modified_query

# Generate variations tracking provenance
queries_df['varied_query'] = queries_df['text'].apply(apply_lexical_perturbation)
queries_df['variation_type'] = 'lexical_typo'

```

> **Code Suggestion**: *Replace this placeholder snippet with a specific, clean excerpt from your Jupyter notebooks showing either your LLM prompt-generation logic or your exact data-wrangling routine to highlight your Python data-engineering proficiency.*

### Ranking Architectures Evaluated

Queries were tested against a historical spectrum of IR models to establish a comprehensive baseline of robustness:

* **Traditional/Lexical**: BM25, Relevance Model 3 (RM3)
* **Neural IR**: KNRM, Conv-KNRM
* **Pretrained Language Models (PLMs)**: BERT, EPIC, T5

---

## Key Learnings: The 45% Problem

> **The Fragility of PLMs**: Variations that maintained the *exact same* query semantics caused traditional, neural, and PLM-based retrieval systems to lose approximately **45%** of their retrieval effectiveness.

This finding underscores a massive gap between controlled benchmark performance and real-world robustness. To manage the analytical phase and prove this drop, **data provenance** was crucial. I rigorously tracked the state of generated queries—distinguishing between misspellings, naturality, ordering, paraphrasing, and synonym transformations—via CSVs to isolate exactly *which* types of variations caused the worst system failures.

---

## Technical Challenges & Computational Hurdles

Training and evaluating complex transformer architectures requires substantial GPU resources. I utilized Google Colab as my primary compute environment, which presented serious difficulties for long-running neural learning tasks.

> **Image Suggestion**: *Add a simple flowchart showing your Colab state management pipeline: from data generation -> Google Drive checkpointing -> Model Evaluation. This visually proves your systems-engineering mindset and ability to architect workarounds.*

### Overcoming Colab Limitations

* **Session Timeouts & State Management**: Colab instances frequently disconnect. I engineered the pipeline to heavily rely on Google Drive mounting (`drive.mount('/content/gdrive/')`). Intermediate states, model checkpoints, and generated query batches were continuously serialized so the pipeline could resume from the last saved state rather than restarting from scratch.
* **Memory Optimization**: Loading large retrieval indexes (like MS MARCO) into Colab's limited RAM required careful data chunking, highly efficient data structures in `pandas`, and standardized string operations utilizing Python's `re` library to minimize overhead.

---

## Sustainability & Future Recommendations

This thesis proves that while Neural IR and PLMs have revolutionized search effectiveness, their lack of robustness remains a severe vulnerability. Viewing this through an engineering lens highlights key operational areas for scaling this pipeline in future work:

* **Adversarial Training**: Integrating this query-generation step directly into a continual learning pipeline for ranking models so they learn to be robust against variations during training.
* **Compute Infrastructure Scaling**: Transitioning the computational workload from ephemeral Colab notebooks to dedicated cloud instances (e.g., AWS EC2 or GCP Compute Engine) with automated orchestrators like Apache Airflow to handle large scale index loading and distributed training loops smoothly.

> *The full thesis document, alongside Jupyter Notebooks containing the query variation generation and evaluation scripts, are available upon request.*