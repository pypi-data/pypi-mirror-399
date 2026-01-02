---
language:
- en
- de
- fr
- es
- it
- pt
license: other
license_name: lfm1.0
license_link: https://huggingface.co/LiquidAI/LFM2-VL-450M/blob/main/LICENSE
library_name: sauerkrautlm-colpali
tags:
- document-retrieval
- vision-language-model
- multi-vector
- colpali
- late-interaction
- visual-retrieval
- lfm2
- small-model
- efficient
- curriculum-learning
- hierarchical-merge
- mteb
- vidore
base_model: LiquidAI/LFM2-VL-450M
pipeline_tag: image-text-to-text
datasets:
- vidore/colpali_train_set
- openbmb/VisRAG-Ret-Train-In-domain-data
- llamaindex/vdr-multilingual-train
- unicamp-dl/mmarco
metrics:
- ndcg_at_5
---

# SauerkrautLM-ColLFM2-450M-v0.1

<p align="center">
  <img src="https://vago-solutions.ai/wp-content/themes/vago/images/vago_logo.png" alt="VAGO Solutions Logo" width="200"/>
</p>

**🏆 #1 Small Model (<1B)** | **Best-in-Class Efficiency**

SauerkrautLM-ColLFM2-450M-v0.1 is the **#1 small model** for visual document retrieval, achieving **83.56 NDCG@5** on ViDoRe v1 - beating colSmol-500M (82.49) with **10% fewer parameters**!

<p align="center">
  <img src="https://raw.githubusercontent.com/VAGOsolutions/sauerkrautlm-colpali/main/assets/benchmark_128dim_v1.png" alt="ViDoRe v1 Benchmark - 128-dim Models" width="100%"/>
</p>

## 🎯 Why Visual Document Retrieval?

Traditional OCR-based retrieval **loses layout, tables, and visual context**. Our visual approach:
- ✅ **No OCR errors** - Direct visual understanding
- ✅ **Layout-aware** - Understands tables, forms, charts
- ✅ **End-to-end** - Single model, no pipeline complexity

## 🏆 Key Achievements

| Benchmark | Score | Rank (Small <1B) |
|-----------|-------|------------------|
| **ViDoRe v1** | **83.56** | **🥇 #1** |
| **MTEB v1+v2** | **74.33** | **🥇 #1** |
| **ViDoRe v3** | **43.32** | **🥇 #1** |

### Small Category Comparison (<1B, 128-dim)

| Model | Params | Dim | ViDoRe v1 | MTEB v1+v2 | ViDoRe v3 |
|-------|--------|-----|-----------|------------|-----------|
| **SauerkrautLM-ColLFM2-450M-v0.1** ⭐ | 450M | 128 | **83.56** | **74.33** | **43.32** |
| colSmol-500M | 500M | 128 | 82.49 | 71.17 | - |
| colSmol-256M | 256M | 128 | 79.74 | 66.90 | 20.73 |

*#1 in ALL benchmarks for small models!*

### Detailed Benchmark Results

<details>
<summary><b>📊 ViDoRe v1 (NDCG@5) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ArxivQA | 76.11 |
| DocVQA | 59.11 |
| InfoVQA | 88.36 |
| ShiftProject | 73.14 |
| SyntheticDocQA-AI | 98.76 |
| SyntheticDocQA-Energy | 94.39 |
| SyntheticDocQA-Gov | 94.61 |
| SyntheticDocQA-Health | 97.32 |
| TabFQuAD | 80.91 |
| TATDQA | 72.88 |
| **Average** | **83.56** |

</details>

<details>
<summary><b>📊 MTEB v1+v2 (NDCG@5) - Click to expand</b></summary>

**ViDoRe v1 Tasks:**
| Task | Score |
|------|-------|
| ArxivQA | 76.11 |
| DocVQA | 59.11 |
| InfoVQA | 88.36 |
| ShiftProject | 73.14 |
| SyntheticDocQA-AI | 98.76 |
| SyntheticDocQA-Energy | 94.39 |
| SyntheticDocQA-Gov | 94.61 |
| SyntheticDocQA-Health | 97.32 |
| TabFQuAD | 80.91 |
| TATDQA | 72.88 |

**ViDoRe v2 Tasks (Multilingual):**
| Task | Score |
|------|-------|
| ViDoRe-v2-2BioMed | 51.00 |
| ViDoRe-v2-2Econ | 48.35 |
| ViDoRe-v2-2ESG-HL | 54.87 |
| ViDoRe-v2-2ESG | 50.80 |
| **Combined Average** | **74.33** |

</details>

<details>
<summary><b>📊 ViDoRe v3 (NDCG@10) - Click to expand</b></summary>

| Task | Score |
|------|-------|
| ViDoRe-v3-CS | 58.08 |
| ViDoRe-v3-Energy | 47.92 |
| ViDoRe-v3-FinanceEn | 47.72 |
| ViDoRe-v3-FinanceFr | 33.00 |
| ViDoRe-v3-HR | 43.37 |
| ViDoRe-v3-Industry | 30.21 |
| ViDoRe-v3-Pharma | 51.42 |
| ViDoRe-v3-Physics | 34.83 |
| **Average** | **43.32** |

</details>

### Efficiency Comparison

| Metric | ColLFM2-450M | colSmol-500M | Advantage |
|--------|--------------|--------------|-----------|
| Parameters | **450M** | 500M | **-10%** |
| ViDoRe v1 | **83.56** | 82.49 | **+1.07** |
| MTEB v1+v2 | **74.33** | 71.17 | **+3.16** |

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

- **🏆 Best Small Model**: #1 in ALL benchmarks for <1B models
- **⚡ Ultra Efficient**: Only 450M parameters, ~0.9GB VRAM
- **🎓 Curriculum Learning**: Trained with progressive difficulty
- **🔀 Hierarchical Merge**: Advanced model merging for optimal performance
- **📐 Native 512x512**: Optimized for document resolution
- **🌍 Multilingual**: 6 languages (EN, DE, FR, ES, IT, PT)

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | [LiquidAI/LFM2-VL-450M](https://huggingface.co/LiquidAI/LFM2-VL-450M) |
| **Parameters** | 450M |
| **Embedding Dimension** | 128 |
| **VRAM (bfloat16)** | ~0.9 GB |
| **Max Context Length** | 32,768 tokens |
| **Image Resolution** | 512×512 native |
| **Image Tokens** | 64-256 (dynamic) |
| **Vision Encoder** | SigLIP2 (86M) |
| **License** | LFM 1.0 |

## 🎓 Advanced Training Methodology

### 1. Curriculum Learning

Unlike standard training, ColLFM2 was trained with curriculum learning:

```
Stage 1: Easy examples (high-quality, clear documents)
    ↓
Stage 2: Medium examples (mixed quality)
    ↓
Stage 3: Hard examples (complex layouts, noisy scans)
    ↓
Stage 4: Full mixture with hard negatives
```

### 2. Hierarchical Model Merging

```
Base LFM2-VL-450M
        ↓
    ┌───┴───┐
    ↓       ↓
mMARCO   Retrieval
Specialist  Model
    ↓       ↓
    └───┬───┘
        ↓
  Hierarchical Merge
        ↓
   Final Model
```

- **mMARCO Specialist**: Sub-model trained on mMARCO for retrieval fundamentals
- **Retrieval Model**: Trained on document retrieval datasets
- **Hierarchical Merge**: Combined using learned merge weights

### Hardware & Configuration

| Setting | Value |
|---------|-------|
| **GPUs** | 4x NVIDIA RTX 6000 Ada (48GB) |
| **Effective Batch Size** | 256 |
| **Precision** | bfloat16 |
| **Curriculum Stages** | 4 |

### Datasets

| Dataset | Description |
|---------|-------------|
| [vidore/colpali_train_set](https://huggingface.co/datasets/vidore/colpali_train_set) | ColPali training data |
| [openbmb/VisRAG-Ret-Train-In-domain-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data) | Visual RAG training data |
| [llamaindex/vdr-multilingual-train](https://huggingface.co/datasets/llamaindex/vdr-multilingual-train) | Multilingual retrieval (with curriculum) |
| [unicamp-dl/mmarco](https://huggingface.co/datasets/unicamp-dl/mmarco) | mMARCO for specialist model |
| VAGO Multilingual Datasets | Proprietary multilingual data |

## Installation & Usage

> ⚠️ **Important**: Install our package first before loading the model:

```bash
pip install git+https://github.com/VAGOsolutions/sauerkrautlm-colpali
```

```python
import torch
from PIL import Image
from sauerkrautlm_colpali.models import ColLFM2, ColLFM2Processor

model_name = "VAGOsolutions/SauerkrautLM-ColLFM2-450M-v0.1"

model = ColLFM2.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
).eval()

processor = ColLFM2Processor.from_pretrained(model_name)

images = [Image.open("document.png")]
queries = ["What is the main topic?"]

batch_images = processor.process_images(images).to(model.device)
batch_queries = processor.process_queries(queries).to(model.device)

with torch.no_grad():
    image_embeddings = model(**batch_images)
    query_embeddings = model(**batch_queries)

scores = processor.score(query_embeddings, image_embeddings)
```

## Use Cases

✅ **Perfect for:**
- Edge deployment (Raspberry Pi, Jetson)
- Mobile applications
- High-throughput batch processing
- Cost-sensitive deployments
- Real-time retrieval systems

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

## License

This model is licensed under the **LFM 1.0 License** from LiquidAI.
Please review the [full license](https://huggingface.co/LiquidAI/LFM2-VL-450M/blob/main/LICENSE) before commercial use.

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