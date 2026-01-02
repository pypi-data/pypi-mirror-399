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
  - mteb
  - vidore
base_model: Qwen/Qwen3-VL-4B
pipeline_tag: image-text-to-text
datasets:
  - vidore/colpali_train_set
  - openbmb/VisRAG-Ret-Train-In-domain-data
  - llamaindex/vdr-multilingual-train
metrics:
  - ndcg_at_5
---

# SauerkrautLM-ColQwen3-4b-v0.1

<p align="center">
  <img src="https://vago-solutions.ai/wp-content/uploads/2024/03/vago-logo.webp" alt="VAGO Solutions Logo" width="200"/>
</p>

**🥇 Best 128-dim Model in Large (3-5B) Category** | **Excellent Performance with Half the Memory**

SauerkrautLM-ColQwen3-4b-v0.1 achieves **90.80 NDCG@5** on ViDoRe v1, making it the **#2 overall among 128-dim models** and the **best in the Large (3-5B) category** for ViDoRe v1.

<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1.png" alt="ViDoRe v1 Benchmark - 128-dim Models" width="100%"/>
</p>

## 🎯 Why Visual Document Retrieval?

Traditional OCR-based retrieval **loses layout, tables, and visual context**. Our visual approach:
- ✅ **No OCR errors** - Direct visual understanding
- ✅ **Layout-aware** - Understands tables, forms, charts
- ✅ **End-to-end** - Single model, no pipeline complexity

## 🏆 Key Achievements

| Benchmark | Score | Rank (128-dim) |
|-----------|-------|----------------|
| **ViDoRe v1** | **90.80** | **#2** |
| MTEB v1+v2 | 81.97 | #4 |
| ViDoRe v3 | 56.03 | #4 |

### Large Category Comparison (3-5B, 128-dim)

| Model | Params | Dim | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----|-----------|------------|-----------|
| **SauerkrautLM-ColQwen3-4b-v0.1** ⭐ | 4.0B | 128 | **90.80** | 81.97 | 56.03 |
| EvoQwen2.5-VL-Retriever-3B-v1 | 3.0B | 128 | 90.67 | **82.76** | - |
| colnomic-embed-multimodal-3b | 3.0B | 128 | 89.86 | 80.09 | **56.40** |
| colqwen2.5-v0.2 | 3.0B | 128 | 89.54 | 81.12 | 52.44 |
| SauerkrautLM-ColMinistral3-3b-v0.1 | 3.0B | 128 | 81.98 | 71.93 | 40.50 |

*Best ViDoRe v1 in the Large category!*

### Detailed Benchmark Results

<details>
<summary><b>📊 ViDoRe v1 (NDCG@5) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ArxivQA | 91.83 |
| DocVQA | **66.96** 🥇 |
| InfoVQA | 94.23 |
| ShiftProject | 90.55 |
| SyntheticDocQA-AI | 99.63 |
| SyntheticDocQA-Energy | 96.52 |
| SyntheticDocQA-Gov | 96.16 |
| SyntheticDocQA-Health | **100.00** 🥇 |
| TabFQuAD | 89.48 |
| TATDQA | 82.66 |
| **Average** | **90.80** |

</details>

<details>
<summary><b>📊 MTEB v1+v2 (NDCG@5) - Click to expand</b></summary>

**ViDoRe v1 Tasks:**
| Task | Score |
|------|-------|
| ArxivQA | 91.83 |
| DocVQA | **66.96** 🥇 |
| InfoVQA | 94.23 |
| ShiftProject | 90.55 |
| SyntheticDocQA-AI | 99.63 |
| SyntheticDocQA-Energy | 96.52 |
| SyntheticDocQA-Gov | 96.16 |
| SyntheticDocQA-Health | **100.00** 🥇 |
| TabFQuAD | 89.48 |
| TATDQA | 82.66 |

**ViDoRe v2 Tasks (Multilingual):**
| Task | Score |
|------|-------|
| ViDoRe-v2-2BioMed | 58.85 |
| ViDoRe-v2-2Econ | 54.96 |
| ViDoRe-v2-2ESG-HL | 69.23 |
| ViDoRe-v2-2ESG | 56.52 |
| **Combined Average** | **81.97** |

</details>

<details>
<summary><b>📊 ViDoRe v3 (NDCG@10) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ViDoRe-v3-CS | 73.96 |
| ViDoRe-v3-Energy | 64.66 |
| ViDoRe-v3-FinanceEn | 55.92 |
| ViDoRe-v3-FinanceFr | 42.87 |
| ViDoRe-v3-HR | 55.70 |
| ViDoRe-v3-Industry | 46.06 |
| ViDoRe-v3-Pharma | 60.70 |
| ViDoRe-v3-Physics | 48.33 |
| **Average** | **56.03** |

</details>

### Overall Summary (128-dim Models)

| Model | Params | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----------|------------|-----------|
| SauerkrautLM-ColQwen3-8b-v0.1 | 8.0B | **91.08 (#1)** | 82.91 (#2) | **58.55 (#1)** |
| **SauerkrautLM-ColQwen3-4b-v0.1** ⭐ | 4.0B | 90.80 (#2) | 81.97 (#4) | 56.03 (#4) |
| EvoQwen2.5-VL-Retriever-7B-v1 | 7.0B | 90.68 (#3) | **83.41 (#1)** | - |
| EvoQwen2.5-VL-Retriever-3B-v1 | 3.0B | 90.67 (#4) | 82.76 (#3) | - |
| SauerkrautLM-ColQwen3-2b-v0.1 | 2.2B | 90.24 (#5) | 81.02 (#7) | 54.32 (#5) |
| colqwen2.5-v0.2 | 3.0B | 89.54 (#8) | 81.12 (#6) | 52.44 (#6) |

## 📋 Summary Tables

### 128-dim Models Comparison
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/table_summary_128dim.png" alt="128-dim Models Summary" width="100%"/>
</p>

### Comparison vs High-dim Models
<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/table_summary_highdim_comparison.png" alt="High-dim Comparison" width="100%"/>
</p>

## ✨ Key Features

- **🏆 #2 Overall (128-dim)**: Second highest ViDoRe v1 score among all 128-dim models
- **🥇 #1 in Large Category**: Best 3-5B model on ViDoRe v1
- **💾 Memory Efficient**: Only ~8GB VRAM (half of 8B model)
- **⚡ Compact Embeddings**: 128-dimensional
- **🌍 Multilingual**: 6 languages (EN, DE, FR, ES, IT, PT)

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | [Qwen/Qwen3-VL-4B](https://huggingface.co/Qwen/Qwen3-VL-4B) |
| **Parameters** | 4.0B |
| **Embedding Dimension** | 128 |
| **VRAM (bfloat16)** | ~8 GB |
| **Max Context Length** | 262,144 tokens |
| **License** | Apache 2.0 |

## Training

### Hardware & Configuration

| Setting | Value |
|---------|-------|
| **GPUs** | 4x NVIDIA RTX 6000 Ada (48GB) |
| **Effective Batch Size** | 256 |
| **Precision** | bfloat16 |

### Datasets

| Dataset | Type | Description |
|---------|------|-------------|
| [vidore/colpali_train_set](https://huggingface.co/datasets/vidore/colpali_train_set) | Public | ColPali training data |
| [openbmb/VisRAG-Ret-Train-In-domain-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data) | Public | Visual RAG training data |
| [llamaindex/vdr-multilingual-train](https://huggingface.co/datasets/llamaindex/vdr-multilingual-train) | Public | Multilingual document retrieval |
| VAGO Multilingual Dataset 1 | **In-house** | Proprietary multilingual document-query pairs |
| VAGO Multilingual Dataset 2 | **In-house** | Proprietary multilingual document-query pairs |

## Installation & Usage

> ⚠️ **Important**: Install our package first before loading the model:

```bash
pip install git+https://github.com/VAGOsolutions/sauerkrautlm-colpali
```

```python
import torch
from PIL import Image
from sauerkrautlm_colpali.models import ColQwen3, ColQwen3Processor

model_name = "VAGOsolutions/SauerkrautLM-ColQwen3-4b-v0.1"

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