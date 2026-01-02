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
  - ministral
  - pixtral
  - mistral
  - mteb
  - vidore
base_model: mistralai/Ministral-3B-Instruct
pipeline_tag: image-text-to-text
datasets:
  - vidore/colpali_train_set
  - openbmb/VisRAG-Ret-Train-In-domain-data
  - llamaindex/vdr-multilingual-train
metrics:
  - ndcg_at_5
---

# SauerkrautLM-ColMinistral3-3b-v0.1

<p align="center">
  <img src="https://vago-solutions.ai/wp-content/uploads/2024/03/vago-logo.webp" alt="VAGO Solutions Logo" width="200"/>
</p>

**🔬 Experimental Architecture** | **Mistral-Based Visual Retrieval**

SauerkrautLM-ColMinistral3-3b-v0.1 is an **experimental** model based on Ministral-3B-Instruct with the Pixtral vision encoder, exploring the Mistral architecture for document retrieval.

> ⚠️ **Note**: This is an experimental release. For production use, we recommend ColQwen3 or ColLFM2 models.

<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1.png" alt="ViDoRe v1 Benchmark - 128-dim Models" width="100%"/>
</p>

## 🎯 Why Visual Document Retrieval?

Traditional OCR-based retrieval **loses layout, tables, and visual context**. Our visual approach:
- ✅ **No OCR errors** - Direct visual understanding
- ✅ **Layout-aware** - Understands tables, forms, charts
- ✅ **End-to-end** - Single model, no pipeline complexity

## 📊 Benchmark Results

| Benchmark | Score | Rank (128-dim) |
|-----------|-------|----------------|
| ViDoRe v1 | 81.98 | - |
| MTEB v1+v2 | 71.93 | - |
| ViDoRe v3 | 40.50 | #11 |

### Large Category Comparison (3-5B, 128-dim)

| Model | Params | Dim | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----|-----------|------------|-----------|
| SauerkrautLM-ColQwen3-4b-v0.1 ⭐ | 4.0B | 128 | **90.80** | 81.97 | 56.03 |
| EvoQwen2.5-VL-Retriever-3B-v1 | 3.0B | 128 | 90.67 | **82.76** | - |
| colnomic-embed-multimodal-3b | 3.0B | 128 | 89.86 | 80.09 | **56.40** |
| **SauerkrautLM-ColMinistral3-3b-v0.1** | 3.0B | 128 | 81.98 | 71.93 | 40.50 |

### vs. ColPali Baseline

| Model | Params | ViDoRe v1 |
|-------|--------|-----------|
| **ColMinistral3-3b** | 3.0B | 81.98 |
| colpali-v1.1 | 2.9B | 81.61 |

*Slightly better than ColPali-v1.1 baseline.*

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

- **🔬 Novel Architecture**: First ColPali-style model based on Ministral/Pixtral
- **📷 Pixtral Vision**: Uses Mistral's Pixtral vision encoder
- **⚡ 128-dim Embeddings**: Compact embedding space
- **🌍 Multilingual**: 6 languages (EN, DE, FR, ES, IT, PT)

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | [mistralai/Ministral-3B-Instruct](https://huggingface.co/mistralai/Ministral-3B-Instruct) |
| **Vision Encoder** | Pixtral |
| **Parameters** | 3.0B |
| **Embedding Dimension** | 128 |
| **VRAM (bfloat16)** | ~6 GB |
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
| [llamaindex/vdr-multilingual-train](https://huggingface.co/datasets/llamaindex/vdr-multilingual-train) | Public | Multilingual retrieval |
| VAGO Multilingual Dataset 1 | **In-house** | Proprietary multilingual document-query pairs |
| VAGO Multilingual Dataset 2 | **In-house** | Proprietary multilingual document-query pairs |

## Installation & Usage

> ⚠️ **Important**: Install our package first (requires transformers 5.0.0+):

```bash
pip install "sauerkrautlm-colpali[ministral]"
# Or: pip install git+https://github.com/VAGOsolutions/sauerkrautlm-colpali && pip install transformers>=5.0.0rc0
```

## Usage

```python
import torch
from PIL import Image
from sauerkrautlm_colpali.models import ColMinistral3, ColMinistral3Processor

model_name = "VAGOsolutions/SauerkrautLM-ColMinistral3-3b-v0.1"

model = ColMinistral3.from_pretrained(model_name)
model = model.to(dtype=torch.bfloat16, device="cuda:0").eval()

processor = ColMinistral3Processor.from_pretrained(model_name)

images = [Image.open("document.png")]
queries = ["What is the main topic?"]

batch_images = processor.process_images(images).to(model.device)
batch_queries = processor.process_queries(queries).to(model.device)

with torch.no_grad():
    image_embeddings = model(**batch_images)
    query_embeddings = model(**batch_queries)

scores = processor.score(query_embeddings, image_embeddings)
```

## When to Use This Model

✅ **Consider when:**
- You need a Mistral-based architecture
- Exploring alternative vision encoders
- Research and experimentation

❌ **Use ColQwen3 instead when:**
- Maximum performance required
- Production deployment

## Experimental Status

This model represents architecture exploration. Key findings:
- Pixtral Vision Encoder works for document understanding
- Ministral backbone capable but not as optimized for retrieval as Qwen3-VL
- Future work: investigating larger Ministral variants

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
