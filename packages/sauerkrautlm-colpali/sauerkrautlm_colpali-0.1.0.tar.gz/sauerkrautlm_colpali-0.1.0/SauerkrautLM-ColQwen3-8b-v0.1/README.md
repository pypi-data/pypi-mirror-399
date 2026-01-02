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
base_model: Qwen/Qwen3-VL-8B
pipeline_tag: image-text-to-text
datasets:
  - vidore/colpali_train_set
  - openbmb/VisRAG-Ret-Train-In-domain-data
  - llamaindex/vdr-multilingual-train
metrics:
  - ndcg_at_5
---

# SauerkrautLM-ColQwen3-8b-v0.1

<p align="center">
  <img src="https://vago-solutions.ai/wp-content/uploads/2024/03/vago-logo.webp" alt="VAGO Solutions Logo" width="200"/>
</p>

**🏆 #1 among 128-dim Models** | **State-of-the-Art Visual Document Retrieval**

SauerkrautLM-ColQwen3-8b-v0.1 is the **best-performing 128-dimensional embedding model** for visual document retrieval, achieving **91.08 NDCG@5** on ViDoRe v1 - the highest score among all models with 128-dim embeddings.

<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1.png" alt="ViDoRe v1 Benchmark - 128-dim Models" width="100%"/>
</p>

## 🎯 Why Visual Document Retrieval?

Traditional OCR-based retrieval **loses layout, tables, and visual context**. Our visual approach:
- ✅ **No OCR errors** - Direct visual understanding
- ✅ **Layout-aware** - Understands tables, forms, charts
- ✅ **End-to-end** - Single model, no pipeline complexity

## 🏆 Key Achievements

| Benchmark | Score | Rank (128-dim) | Rank (All) |
|-----------|-------|----------------|------------|
| **ViDoRe v1** | **91.08** | **🥇 #1** | #1 |
| MTEB v1+v2 | 82.91 | #2 | #5 |
| **ViDoRe v3** | **58.55** | **🥇 #1** | #3 |

### 128-dim Models Comparison (XLarge Category)

| Model | Params | Dim | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----|-----------|------------|-----------|
| **SauerkrautLM-ColQwen3-8b-v0.1** ⭐ | 8.0B | 128 | **91.08** | 82.91 | **58.55** |
| EvoQwen2.5-VL-Retriever-7B-v1 | 7.0B | 128 | 90.68 | **83.41** | - |
| colnomic-embed-multimodal-7b | 7.0B | 128 | 89.72 | 81.30 | 57.64 |

*Our 8B model achieves the highest ViDoRe v1 and v3 scores among ALL 128-dim models!*

### Detailed Benchmark Results

<details>
<summary><b>📊 ViDoRe v1 (NDCG@5) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ArxivQA | **93.80** 🥇 |
| DocVQA | 64.69 |
| InfoVQA | 94.51 |
| ShiftProject | 90.41 |
| SyntheticDocQA-AI | 98.65 |
| SyntheticDocQA-Energy | 96.52 |
| SyntheticDocQA-Gov | 96.79 |
| SyntheticDocQA-Health | 99.26 |
| TabFQuAD | 92.18 |
| TATDQA | **84.04** 🥇 |
| **Average** | **91.08** 🥇 |

</details>

<details>
<summary><b>📊 MTEB v1+v2 (NDCG@5) - Click to expand</b></summary>

**ViDoRe v1 Tasks:**
| Task | Score |
|------|-------|
| ArxivQA | **93.80** 🥇 |
| DocVQA | 64.69 |
| InfoVQA | 94.51 |
| ShiftProject | 90.41 |
| SyntheticDocQA-AI | 98.65 |
| SyntheticDocQA-Energy | 96.52 |
| SyntheticDocQA-Gov | 96.79 |
| SyntheticDocQA-Health | 99.26 |
| TabFQuAD | 92.18 |
| TATDQA | **84.04** 🥇 |

**ViDoRe v2 Tasks (Multilingual):**
| Task | Score |
|------|-------|
| ViDoRe-v2-2BioMed | 63.26 |
| ViDoRe-v2-2Econ | 57.98 |
| ViDoRe-v2-2ESG-HL | 70.77 |
| ViDoRe-v2-2ESG | 57.85 |
| **Combined Average** | **82.91** |

</details>

<details>
<summary><b>📊 ViDoRe v3 (NDCG@10) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ViDoRe-v3-CS | **77.52** 🥇 |
| ViDoRe-v3-Energy | 66.32 |
| ViDoRe-v3-FinanceEn | 55.79 |
| ViDoRe-v3-FinanceFr | 45.03 |
| ViDoRe-v3-HR | 59.96 |
| ViDoRe-v3-Industry | 50.39 |
| ViDoRe-v3-Pharma | 63.98 |
| ViDoRe-v3-Physics | 49.36 |
| **Average** | **58.55** |

</details>

### Overall Summary (128-dim Models)

| Model | Params | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----------|------------|-----------|
| **SauerkrautLM-ColQwen3-8b-v0.1** ⭐ | 8.0B | **91.08 (#1)** | 82.91 (#2) | **58.55 (#1)** |
| EvoQwen2.5-VL-Retriever-7B-v1 | 7.0B | 90.68 (#3) | **83.41 (#1)** | - |
| SauerkrautLM-ColQwen3-4b-v0.1 | 4.0B | 90.80 (#2) | 81.97 (#4) | 56.03 (#4) |
| EvoQwen2.5-VL-Retriever-3B-v1 | 3.0B | 90.67 (#4) | 82.76 (#3) | - |
| SauerkrautLM-ColQwen3-2b-v0.1 | 2.2B | 90.24 (#5) | 81.02 (#7) | 54.32 (#5) |
| colnomic-embed-multimodal-7b | 7.0B | 89.72 (#7) | 81.30 (#5) | 57.64 (#2) |
| colnomic-embed-multimodal-3b | 3.0B | 89.86 (#6) | 80.09 (#8) | 56.40 (#3) |
| colqwen2.5-v0.2 | 3.0B | 89.54 (#8) | 81.12 (#6) | 52.44 (#6) |
| colqwen2-v1.0 | 2.2B | 89.23 (#9) | 79.74 (#9) | 44.18 (#8) |

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

- **🏆 #1 in 128-dim Class**: Best ViDoRe v1 and v3 scores among all 128-dim models
- **⚡ Compact Embeddings**: 128-dimensional (same as ColPali, 2.5x smaller than tomoro)
- **🌍 Multilingual**: Trained on 6 languages (EN, DE, FR, ES, IT, PT)
- **📄 High Resolution**: Supports up to 1540 visual tokens per image
- **🔧 MTEB Compatible**: Standardized evaluation and easy integration
- **💻 Full Code**: [github.com/VAGOsolutions/sauerkrautlm-colpali](https://github.com/VAGOsolutions/sauerkrautlm-colpali)

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | [Qwen/Qwen3-VL-8B](https://huggingface.co/Qwen/Qwen3-VL-8B) |
| **Parameters** | 8.0B |
| **Embedding Dimension** | 128 |
| **VRAM (bfloat16)** | ~16 GB |
| **Max Context Length** | 262,144 tokens |
| **Image Resolution** | Dynamic (up to 1540 visual tokens) |
| **Supported Languages** | EN, DE, FR, ES, IT, PT |
| **License** | Apache 2.0 |

## Training

### Hardware & Configuration

| Setting | Value |
|---------|-------|
| **GPUs** | 4x NVIDIA A100 SXM (80GB) |
| **Effective Batch Size** | 256 |
| **Precision** | bfloat16 |
| **Optimizer** | AdamW |

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

model_name = "VAGOsolutions/SauerkrautLM-ColQwen3-8b-v0.1"

model = ColQwen3.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="cuda:0",
).eval()

processor = ColQwen3Processor.from_pretrained(model_name)

# Process inputs
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
- **Email**: info@vago-solutions.ai
