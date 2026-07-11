---
main-image: /fighead.png
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

main-image: /fighead.png

---

# Evaluating Robust Retrieval Pipelines

> "Modern search engines seem practically omniscient—until you ask them the exact same question in a slightly different way. Then, state-of-the-art models can silently fail."

## Project Overview & Scope

As part of my Bachelor of Engineering (Honours) in Computer Systems / Electrical and Electronic Engineering at the University of Queensland, I undertook a year-long thesis project focusing on **Information Retrieval (IR) systems**.

> 
> *"This project aims to evaluate the robustness of recent PLM IR pipelines on large datasets with novel and established query variation techniques, to establish how variations which maintain query semantics affect systems' effectiveness."* 
> 
> 

Modern search engines and IR pipelines increasingly rely on Pretrained Language Models (PLMs) to rank documents. However, these systems are typically benchmarked against a single standard query for a given information need. This ignores the vast diversity in human expression, leading to a critical question: *How brittle are these advanced ranking architectures in the real world?*

{% include image-gallery.html images="Fig1.png" height="600" %}
<span style="font-size: 14px">Figure 1; Multistage architecture of modern information retrieval system. Image Source *J Guo et al.,  2022*.</span>

>  
> 
> 

{% include image-gallery.html images="Fig1.png" height="600" %}
<span style="font-size: 14px">Figure 1; Multistage architecture of modern information retrieval system. Image Source *J Guo et al.,  2022*.</span> 


{% include image-gallery.html images="TRECefficacy.png" height="600" %}
{% include image-gallery.html images="ANTIQUEefficacy.png" height="600" %}
<span style="font-size: 14px">Figures 2&3; Comparative Efficacy (nDCG@10) Across Varied Retrieval Methodologies in TREC-DL-2019 and ANTIQUE Datasets Subject to Query Modifications. All query variation methods result in statistically significant (P<0.05) effectivity drops across both datasets (ANTIQUE and TREC-DL-2019).

</span> 



>
> 
> 

This project aimed to rigorously evaluate robustness by generating novel and established query variations—while strictly maintaining core semantic meaning—and quantifying the resulting performance degradation across multiple search architectures.

---

## Core Objectives & Methodology

The bulk of my efforts centered around **generating varied search queries and determining their retrieval effects**.

### Datasets & Baselines

I utilized industry-standard datasets, including **MS MARCO & ANTIQUE**, to ensure evaluations were grounded in realistic, large-scale search scenarios. By leveraging libraries like `ir_datasets` and `pandas`, I aligned, parsed, and cleaned variations from existing databases (such as G. Penha's repository) alongside my own dynamically generated queries.

> **Insert Image**: Figure 10; Demonstration of random character deletion on an original query OR Figure 11; Demonstration of lemmatisation on an original query 
> 
> 

The following script excerpts highlight the data-wrangling routine and LLM prompt-generation logic used to dynamically generate semantic variations:

```python
import openai
import csv

# Initialize the OpenAI API client
openai.api_key = 'REDACTED'

def get_paraphrase(query):
    # Construct the API call to OpenAI to generate semantic variations
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Paraphrase the following query and provide a query that conveys the same meaning. The query must be grammatically correct and clearly written: {query}"}
        ]
    )
    return response.choices[0].message['content'].strip()

def main():
    input_filename = 'unique_queries_antique.csv'
    output_filename = 'paraphrased_queries.csv'
    
    with open(input_filename, 'r', encoding='utf-8') as infile, \
         open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            original_query = row[0]
            varied_query = get_paraphrase(original_query)
            writer.writerow([original_query, varied_query])

if __name__ == "__main__":
    main()

```

### Ranking Architectures Evaluated

Queries were tested against a historical spectrum of IR models to establish a comprehensive baseline of robustness:

* **Traditional/Lexical**: BM25, Relevance Model 3 (RM3)
* **Neural IR**: KNRM, Conv-KNRM
* **Pretrained Language Models (PLMs)**: BERT, EPIC, T5

---

## Key Learnings: The 45% Problem

> 
> **The Fragility of PLMs**: *"The evaluation metric used (NDCG@10) shows significant degradation in retrieval capability in the event of query variation, with an average effectiveness drop of 45.36% across both datasets (TREC-DL-2019 and ANTIQUE)."* 
> 
> 

> 
> *"No query variations evaluated across either data set was more effective in retrieval than the original query and by statistically significant margins (P<0.05)."* 
> 
> 

> 
> *"Traditional, neural and pre-trained ranking models are not robust to natural language query variations."* 
> 
> 

This finding underscores a massive gap between controlled benchmark performance and real-world robustness. To manage the analytical phase and prove this drop, **data provenance** was crucial. I rigorously tracked the state of generated queries—distinguishing between misspellings, naturality, ordering, paraphrasing, and synonym transformations—via CSVs to isolate exactly *which* types of variations caused the worst system failures.

> **Insert Image**: Figure 12 or 13; Increase in query variation length as a function of original query length 
> 
> 

---

## Technical Challenges & Computational Hurdles

Training and evaluating complex transformer architectures requires substantial GPU resources. I utilized Google Colab as my primary compute environment, which presented serious difficulties for long-running neural learning tasks.

> **Insert Image**: Figure 8; Process flow for generating a query variation using OpenAI GPT API 
> 
> 

### Overcoming Colab Limitations

* **Session Timeouts & State Management**: Colab instances frequently disconnect. I engineered the pipeline to heavily rely on Google Drive mounting (`drive.mount('/content/gdrive/')`). Intermediate states, model checkpoints, and generated query batches were continuously serialized so the pipeline could resume from the last saved state rather than restarting from scratch.
* **Memory Optimization**: Loading large retrieval indexes (like MS MARCO) into Colab's limited RAM required careful data chunking, highly efficient data structures in `pandas`, and standardized string operations utilizing Python's `re` library to minimize overhead.

---

## Sustainability & Future Recommendations

This thesis proves that while Neural IR and PLMs have revolutionized search effectiveness, their lack of robustness remains a severe vulnerability. Viewing this through an engineering lens highlights key operational areas for scaling this pipeline in future work:

* **Adversarial Training**: Integrating this query-generation step directly into a continual learning pipeline for ranking models so they learn to be robust against variations during training.
* **Compute Infrastructure Scaling**: Transitioning the computational workload from ephemeral Colab notebooks to dedicated cloud instances (e.g., AWS EC2 or GCP Compute Engine) with automated orchestrators like Apache Airflow to handle large scale index loading and distributed training loops smoothly.

> *The full thesis document, alongside Jupyter Notebooks containing the query variation generation and evaluation scripts, are available at my [GitHub](https://github.com/OliCar-del/EvaluatingRobustRetrivalPipelines).*