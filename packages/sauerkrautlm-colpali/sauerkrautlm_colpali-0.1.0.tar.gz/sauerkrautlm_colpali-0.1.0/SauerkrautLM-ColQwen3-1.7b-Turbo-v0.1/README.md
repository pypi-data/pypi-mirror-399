---
language:
  - en
  - de
  - fr
  - es
  - it
  - pt
license: apache-2.0
library_name: sauerkrautlm-colpali
tags:
  - document-retrieval
  - vision-language-model
  - multi-vector
  - colpali
  - late-interaction
  - visual-retrieval
  - qwen3-vl
  - pruned
  - turbo
  - efficient
  - mteb
  - vidore
base_model: Qwen/Qwen3-VL-2B
pipeline_tag: image-text-to-text
datasets:
  - vidore/colpali_train_set
  - openbmb/VisRAG-Ret-Train-In-domain-data
  - llamaindex/vdr-multilingual-train
  - unicamp-dl/mmarco
metrics:
  - ndcg_at_5
---

# SauerkrautLM-ColQwen3-1.7b-Turbo-v0.1

<p align="center">
  <img src="https://vago-solutions.ai/wp-content/uploads/2024/03/vago-logo.webp" alt="VAGO Solutions Logo" width="200"/>
</p>

**⚡ Turbo Edition** | **23% Smaller, 88.89 ViDoRe v1**

SauerkrautLM-ColQwen3-1.7b-Turbo-v0.1 is a **pruned and optimized** model created by applying **structured pruning** to Qwen3-VL-2B. Despite being **23% smaller**, it achieves **88.89 NDCG@5** on ViDoRe v1 - still beating ColPali-v1.3 (84.75) by a large margin!

<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1.png" alt="ViDoRe v1 Benchmark - 128-dim Models" width="100%"/>
</p>

## 🎯 Why Visual Document Retrieval?

Traditional OCR-based retrieval **loses layout, tables, and visual context**. Our visual approach:
- ✅ **No OCR errors** - Direct visual understanding
- ✅ **Layout-aware** - Understands tables, forms, charts
- ✅ **End-to-end** - Single model, no pipeline complexity

## ✨ What Makes This "Turbo"?

| Aspect | 2B Model | 1.7B Turbo | Reduction |
|--------|----------|------------|-----------|
| **Parameters** | 2.2B | 1.7B | **-23%** |
| **VRAM (bf16)** | ~4.4 GB | ~3.4 GB | **-23%** |
| **ViDoRe v1** | 90.24 | 88.89 | -1.35 pts |
| **Inference Speed** | Baseline | ~20% faster | ⚡ |

## 🏆 Benchmark Results

| Benchmark | Score | Rank (128-dim) |
|-----------|-------|----------------|
| ViDoRe v1 | 88.89 | #10 |
| MTEB v1+v2 | 77.94 | #10 |
| ViDoRe v3 | 48.76 | #7 |

### Medium Category Comparison (1-3B, 128-dim)

| Model | Params | Dim | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----|-----------|------------|-----------|
| SauerkrautLM-ColQwen3-2b-v0.1 ⭐ | 2.2B | 128 | **90.24** | 81.02 | **54.32** |
| colqwen2.5-v0.2 | 2.2B | 128 | 89.54 | **81.12** | 52.44 |
| colqwen2-v1.0 | 2.2B | 128 | 89.23 | 79.74 | 44.18 |
| **SauerkrautLM-ColQwen3-1.7b-Turbo-v0.1** | 1.7B | 128 | 88.89 | 77.94 | 48.76 |

### vs. ColPali Baseline

| Model | Params | ViDoRe v1 |
|-------|--------|-----------|
| **ColQwen3-1.7b-Turbo** | **1.7B** | **88.89** |
| colpali-v1.3 | 2.9B | 84.75 |
| colpali-v1.2 | 2.9B | 83.15 |
| colpali-v1.1 | 2.9B | 81.61 |

*Turbo model beats ColPali-v1.3 by +4.14 points with 42% fewer parameters!*

### Detailed Benchmark Results

<details>
<summary><b>📊 ViDoRe v1 (NDCG@5) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ArxivQA | 91.09 |
| DocVQA | 60.98 |
| InfoVQA | 92.08 |
| ShiftProject | 87.76 |
| SyntheticDocQA-AI | 98.16 |
| SyntheticDocQA-Energy | 97.49 |
| SyntheticDocQA-Gov | 94.88 |
| SyntheticDocQA-Health | 98.26 |
| TabFQuAD | 87.03 |
| TATDQA | 81.19 |
| **Average** | **88.89** |

</details>

<details>
<summary><b>📊 MTEB v1+v2 (NDCG@5) - Click to expand</b></summary>

**ViDoRe v1 Tasks:**
| Task | Score |
|------|-------|
| ArxivQA | 91.09 |
| DocVQA | 60.98 |
| InfoVQA | 92.08 |
| ShiftProject | 87.76 |
| SyntheticDocQA-AI | 98.16 |
| SyntheticDocQA-Energy | 97.49 |
| SyntheticDocQA-Gov | 94.88 |
| SyntheticDocQA-Health | 98.26 |
| TabFQuAD | 87.03 |
| TATDQA | 81.19 |

**ViDoRe v2 Tasks (Multilingual):**
| Task | Score |
|------|-------|
| ViDoRe-v2-2BioMed | 53.92 |
| ViDoRe-v2-2Econ | 47.85 |
| ViDoRe-v2-2ESG-HL | 57.23 |
| ViDoRe-v2-2ESG | 43.27 |
| **Combined Average** | **77.94** |

</details>

<details>
<summary><b>📊 ViDoRe v3 (NDCG@10) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ViDoRe-v3-CS | 67.14 |
| ViDoRe-v3-Energy | 56.48 |
| ViDoRe-v3-FinanceEn | 46.17 |
| ViDoRe-v3-FinanceFr | 33.73 |
| ViDoRe-v3-HR | 46.66 |
| ViDoRe-v3-Industry | 39.44 |
| ViDoRe-v3-Pharma | 55.31 |
| ViDoRe-v3-Physics | 45.14 |
| **Average** | **48.76** |

</details>

## 📋 Summary Tables

### 128-dim Models Comparison
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/table_summary_128dim.png" alt="128-dim Models Summary" width="100%"/>
</p>

### Comparison vs High-dim Models
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/table_summary_highdim_comparison.png" alt="High-dim Comparison" width="100%"/>
</p>

## ⚙️ Pruning Methodology

### Structured Pruning

1. **Layer Pruning**: Removed less important transformer layers based on gradient-based importance scoring
2. **Intermediate Size Reduction**: Reduced FFN intermediate dimensions
3. **Result**: 23% parameter reduction (2.2B → 1.7B)

### Recovery Training with mMARCO

After pruning, the model underwent recovery training:

```
Pruned Model → mMARCO Pre-training → Fine-tuning → Final Model
```

The [mMARCO](https://huggingface.co/datasets/unicamp-dl/mmarco) pre-training was crucial to "heal" the model after pruning.

## Model Details

| Property | Value |
|----------|-------|
| **Original Model** | Qwen3-VL-2B |
| **Parameters** | 1.7B (-23%) |
| **Embedding Dimension** | 128 |
| **VRAM (bfloat16)** | ~3.4 GB |
| **Max Context Length** | 262,144 tokens |
| **Pruning Method** | Layer + Intermediate Size |
| **Recovery Dataset** | mMARCO |
| **License** | Apache 2.0 |

## Training

### Hardware & Configuration

| Setting | Value |
|---------|-------|
| **GPUs** | 4x NVIDIA RTX 6000 Ada (48GB) |
| **Effective Batch Size** | 256 |
| **Precision** | bfloat16 |

### Training Pipeline

1. **Phase 1**: Structured Pruning (gradient-based importance)
2. **Phase 2**: mMARCO Recovery Training
3. **Phase 3**: Retrieval Fine-tuning on standard datasets

## Installation & Usage

> ⚠️ **Important**: Install our package first before loading the model:

```bash
pip install git+https://github.com/VAGOsolutions/sauerkrautlm-colpali
```

```python
import torch
from PIL import Image
from sauerkrautlm_colpali.models import ColQwen3, ColQwen3Processor

model_name = "VAGOsolutions/SauerkrautLM-ColQwen3-1.7b-Turbo-v0.1"

model = ColQwen3.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="cuda:0",
).eval()

processor = ColQwen3Processor.from_pretrained(model_name)

images = [Image.open("document.png")]
queries = ["What is the main topic?"]

batch_images = processor.process_images(images).to(model.device)
batch_queries = processor.process_queries(queries).to(model.device)

with torch.no_grad():
    image_embeddings = model(**batch_images)
    query_embeddings = model(**batch_queries)

scores = processor.score(query_embeddings, image_embeddings)
```

## When to Use Turbo

✅ **Choose Turbo when:**
- Running on limited GPU memory (< 4GB available)
- Need faster inference
- Deploying on edge devices
- Cost optimization is priority

❌ **Choose 2B instead when:**
- Maximum accuracy required
- Memory is not a constraint

## 📊 Additional Benchmark Visualizations

### MTEB v1+v2 Benchmark (128-dim Models)
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1v2.png" alt="MTEB v1+v2 Benchmark - 128-dim Models" width="100%"/>
</p>

### ViDoRe v3 Benchmark (128-dim Models)
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v3.png" alt="ViDoRe v3 Benchmark - 128-dim Models" width="100%"/>
</p>

### Our Models vs High-dim Models
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_ours_vs_highdim_v1.png" alt="ViDoRe v1 - Our Models vs High-dim" width="100%"/>
</p>

## Citation

```bibtex
@misc{sauerkrautlm-colpali-2025,
  title={SauerkrautLM-ColPali: Multi-Vector Vision Retrieval Models},
  author={David Golchinfar},
  organization={VAGO Solutions},
  year={2025},
  url={https://github.com/VAGOsolutions/sauerkrautlm-colpali}
}
```

## Contact

- **VAGO Solutions**: [https://vago-solutions.ai](https://vago-solutions.ai)
- **GitHub**: [https://github.com/VAGOsolutions](https://github.com/VAGOsolutions)
