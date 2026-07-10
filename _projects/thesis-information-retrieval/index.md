---
layout: post
title: Evaluating Robust Retrieval Pipelines
description: An undergraduate engineering thesis investigating the robustness of Information Retrieval (IR) pipelines, specifically Pretrained Language Models (PLMs), against query variations. The project involved generating adversarial and semantic query variations and evaluating their impact on state-of-the-art neural ranking models.
skills:
  - Information Retrieval (IR)
  - Pretrained Language Models (PLMs)
  - Natural Language Processing (NLP)
  - Large Language Models (LLMs)
  - Data Wrangling (Pandas, ir_datasets)
  - Neural Network Training
  - Distributed Workloads (Google Colab)
main-image: /assets/images/thesis-retrieval.png
---

# Evaluating Robust Retrieval Pipelines

## Project Overview & Scope
As part of my Bachelor of Engineering (Honours) in Computer Systems / Electrical and Electronic Engineering at the University of Queensland, I undertook a year-long thesis project focusing on **Information Retrieval (IR) systems**. Modern search engines and IR pipelines increasingly rely on Pretrained Language Models (PLMs) to rank documents. However, these systems are typically benchmarked against a single standard query for a given information need, failing to account for the vast diversity in human expression. 

This project aimed to rigorously evaluate the robustness of recent PLM-based IR pipelines on large datasets. By generating novel and established query variations—while carefully maintaining core semantic meaning—I tested how "brittle" these advanced ranking architectures truly are.

The scope of the project required building a complete evaluation pipeline: fetching large-scale datasets, algorithmically generating query variations (using LLMs, lemmatization, and character deletion), and running these inputs through various retrieval models to quantify performance degradation.

---

## Core Objectives & Methodology

The bulk of my efforts were dedicated to **generating varied search queries and determining their retrieval effects**. This required a methodical approach to data handling and model evaluation.

### Datasets & Baselines
* **MS MARCO & ANTIQUE**: Utilized industry-standard datasets to ensure the evaluations were grounded in realistic, large-scale search scenarios.
* **Data Wrangling**: Leveraged libraries like `ir_datasets` and `pandas` to align, parse, and clean variations from existing databases (e.g., querying variations from G. Penha's repository) alongside my own generated queries.

### Query Variation Generation
To test model robustness, I designed and integrated multiple variation strategies:
1.  **LLM-Driven Variations**: Utilizing Large Language Models (like OpenAI's GPT) to paraphrase and rephrase queries naturally.
2.  **Lexical/Morphological Perturbations**: Implementing Lemmatization and Character Deletion to mimic user misspellings and syntax adjustments.

### Ranking Architectures Evaluated
The generated queries were tested against a historical spectrum of IR models to establish a baseline of robustness:
* **Traditional/Lexical**: BM25, Relevance Model 3 (RM3)
* **Neural IR**: KNRM, Conv-KNRM
* **Pretrained Language Models (PLMs)**: BERT, EPIC, T5

---

## Key Learnings & Design Choices

Through the design and execution of this pipeline, several critical insights emerged:

* **The Fragility of PLMs**: A primary discovery was that variations maintaining the exact same query semantics caused traditional, neural, and PLM-based retrieval systems to lose retrieval effectivity by approximately **45%**. This underscores a critical gap between benchmark performance and real-world robustness.
* **Evaluation Infrastructure**: Designing a pipeline that could interchangeably accept different query files and run them against varied models required highly modular code. This modularity allowed for rapid iteration when testing new generation techniques.
* **Data Provenance**: Managing the state of generated queries (e.g., distinguishing between misspelling, naturality, ordering, paraphrase, and synonym transformations) was handled rigorously via CSV tracking, which streamlined the final analytical phase.

---

## Technical Challenges & Computational Hurdles

A significant portion of the project involved navigating the computational constraints of deep learning.

### Overcoming Google Colab Limitations
Training and evaluating complex neural networks and transformer architectures (like BERT and T5) requires substantial GPU resources. I utilized Google Colab as the primary compute environment, which presented major difficulties for long-running neural learning tasks:
* **Session Timeouts & Resource Limits**: Colab instances frequently disconnect during extended training and evaluation loops. 
* **State Management**: I engineered the pipeline to heavily rely on Google Drive mounting (`drive.mount('/content/gdrive/')`). Intermediate states, model checkpoints, and generated query batches were continuously serialized to Drive. If a session crashed, the pipeline could resume from the last saved state rather than restarting.
* **Memory Optimization**: Loading large retrieval indexes (like MS MARCO) into Colab's limited RAM required chunking data operations and heavily utilizing efficient data structures in `pandas` and standardizing string operations using `re`.

---

## Conclusions & Sustainability

The findings from this thesis highlight that while Neural IR and PLMs have revolutionized search effectiveness, their *robustness* remains a vulnerability. If a user asks the exact same question in a slightly different way, the system's performance essentially drops by half.

**Future Recommendations:**
For future iterations or commercial applications of this work, the query-generation step could be integrated directly into a continual learning pipeline for ranking models (e.g., adversarial training). Furthermore, transitioning the computational workload from ephemeral Colab notebooks to dedicated cloud instances (like AWS EC2 or GCP Compute Engine) with automated orchestrators (like Airflow) would vastly improve the sustainability and scale of the evaluation runs.

> The full thesis document, alongside Jupyter Notebooks containing the query variation generation and evaluation scripts, are available upon request.
