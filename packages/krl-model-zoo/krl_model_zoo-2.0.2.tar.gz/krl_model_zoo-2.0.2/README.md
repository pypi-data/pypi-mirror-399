<div align="center">
  <img src="./assets/images/KRLabs_WebLogo.png" alt="KR-Labs" width="300">
  
  # KR-Labs Model Zoo
  **Open Models. Trusted Intelligence. Shared Progress.**
  
  [![PyPI version](https://img.shields.io/pypi/v/krl-model-zoo.svg)](https://pypi.org/project/krl-model-zoo/)
  [![PyPI downloads](https://img.shields.io/pypi/dm/krl-model-zoo.svg)](https://pypi.org/project/krl-model-zoo/)
  [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
  [![Documentation](https://img.shields.io/badge/docs-readthedocs-brightgreen.svg)](https://krl-model-zoo.readthedocs.io)
  [![Status](https://img.shields.io/badge/status-production%20ready-success.svg)](https://github.com/KR-Labs/krl-model-zoo)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  
  [Documentation](https://krl-model-zoo.readthedocs.io) • [Quick Start](#quick-start) • [Examples](./examples) • [Pricing](#pricing) • [Contributing](CONTRIBUTING.md)
</div>

---

> ## 🎉 **NEW: KRL Model Zoo v2.0** - Choose Your Tier
> 
> We've restructured the Model Zoo into **three tiers** to better serve researchers, professionals, and enterprises:
> 
> | Tier | Models | Price | Best For |
> |------|--------|-------|----------|
> | **Community** 🌍 | 20 models | **FREE** | Learning, prototyping, open research |
> | **Professional** 💼 | 65 models | **$49/month** | Production apps, advanced analytics |
> | **Enterprise** 🏢 | 105 models | **$299/month** | Mission-critical systems, cutting-edge AI |
> 
> **→ You are viewing the Community tier (FREE forever)** 
>
> [**Upgrade to Professional →**](https://github.com/KR-Labs/krl-model-zoo-pro) | [**Explore Enterprise →**](https://github.com/KR-Labs/krl-model-zoo-enterprise) | [**Compare Tiers →**](#tier-comparison)

---

## Highlights

- **20 Production-Ready Models** - Essential open-source models for vision, NLP, time series, audio, and multimodal tasks
- **Built for Public Data** - Native integration with Census, BLS, FRED, CDC, HUD via [KRL Data Connectors](https://github.com/KR-Labs/krl-data-connectors)
- **Research-Grade Quality** - Peer-reviewed algorithms with comprehensive validation and testing
- **Production Ready** - Battle-tested in real-world policy analysis and forecasting applications
- **Fully Documented** - Complete API reference, tutorials, and mathematical formulations
- **Open Source** - Apache 2.0 License, community-driven development

---

## Overview

**KRL Model Zoo™** is an open-source library of socioeconomic and econometric models designed for **researchers, policymakers, analysts, and community organizations** seeking to turn data into actionable intelligence.  

It provides modular, production-grade tools for forecasting, regional analysis, anomaly detection, and policy evaluation — all engineered with transparency, reproducibility, and accessibility in mind.

Developed by **KR-Labs**, the Model Zoo bridges statistical rigor with public-interest purpose, transforming raw data into real-world insight.

### Integrated Ecosystem

The Model Zoo is designed to work seamlessly with **[KRL Data Connectors](https://github.com/KR-Labs/krl-data-connectors)**, our companion library for accessing public datasets. Together, they provide an end-to-end workflow:

**Data → Analysis → Insight**

- **KRL Data Connectors** pulls data from Census, BLS, FRED, CDC, HUD, and 20+ other federal sources
- **KRL Model Zoo** applies statistical models and analytical frameworks
- **Results** drive evidence-based decisions and policy evaluation

---

## Mission

We believe data science should serve humanity.  
The KRL Model Zoo exists to make **responsible, interpretable, and replicable analytics** accessible to everyone shaping economic, social, or community outcomes.  

Our models support research, governance, and education by standardizing open methods for understanding change.

---

## Core Capabilities

- **Unified Framework:** Econometric, causal, ML, and Bayesian models under one architecture.  
- **Transparency by Design:** Built-in provenance tracking, version control, and reproducibility.  
- **Seamless Data Integration:** Native compatibility with KRL Data Connectors for federal datasets.  
- **Community-Driven:** Collaborative ecosystem for model sharing, validation, and continuous improvement.  
- **Policy-Ready Tools:** Designed for public datasets like Census, BLS, FRED, CDC, and HUD.  
- **Educational Utility:** Ideal for universities, research institutes, and civic technology programs.  

---

## Community Tier Models (20 Models - FREE Forever)

| Category | Models Included | Use Case |
|----------|-----------------|----------|
| **Computer Vision (8)** | ResNet-50, MobileNetV2, EfficientNet-B0, YOLO-v5s, Faster R-CNN, U-Net, DeepLabV3, OpenPose | Image classification, object detection, segmentation, pose estimation |
| **NLP (6)** | BERT-base, DistilBERT, GPT-2-small, Word2Vec, TextCNN, Sentiment-RoBERTa | Text encoding, generation, classification, sentiment analysis |
| **Time Series (3)** | LSTM, GRU, TabNet | Sequential modeling, forecasting, tabular data |
| **Audio (2)** | Wav2Vec2-base, SpeechBrain-ASR | Speech recognition, audio processing |
| **Multimodal (1)** | CLIP (ViT-B/32) | Vision-language understanding, zero-shot classification |

**All models are open-source with permissive licenses (MIT/Apache 2.0).** Perfect for learning, prototyping, and open research.

> ### 🚀 Need More Models?
> 
> **[Professional Tier ($49/month)](https://github.com/KR-Labs/krl-model-zoo-pro)** adds 45 advanced models:
> - Larger model variants (ResNet-101/152, BERT-large, EfficientNet B1-B4)
> - Domain-specific models (forecasting, recommendation systems, GNNs)
> - Advanced architectures (Vision Transformers, T5, BART, XLNet)
> - **Total: 65 models** (20 Community + 45 Professional)
> 
> **[Enterprise Tier ($299/month)](https://github.com/KR-Labs/krl-model-zoo-enterprise)** includes cutting-edge models:
> - 7B LLMs (Llama-2, Mistral, Falcon, Code Llama)
> - Latest research (SAM, NeRF, AlphaFold2, Stable Diffusion)
> - Specialized models (protein folding, molecular property prediction)
> - **Total: 105 models** (Full catalog with SLA and dedicated support)
> 
> [**Compare All Tiers →**](#tier-comparison)

---

## Tier Comparison

| Feature | Community 🌍 | Professional 💼 | Enterprise 🏢 |
|---------|--------------|-----------------|---------------|
| **Price** | **FREE** | **$49/month** | **$299/month** |
| **Model Count** | 20 models | 65 models | 105 models |
| **Computer Vision** | 8 base models | +18 advanced models | +15 cutting-edge models |
| **NLP** | 6 base models | +12 advanced models | +10 large LLMs (7B+) |
| **Time Series** | 3 models | +6 forecasting models | +4 foundation models |
| **Audio/Speech** | 2 models | +4 models (Whisper, TTS) | — |
| **Multimodal** | CLIP-base | — | +4 models (BLIP, Flamingo, LLaVA) |
| **Specialized** | — | Recommendation, GNNs | AlphaFold2, ESM-2, Stable Diffusion |
| **License** | Open source (MIT/Apache) | Commercial license | Enterprise license |
| **Support** | Community (GitHub Issues) | Email support | Dedicated support + SLA |
| **Updates** | Major releases | Priority updates | Early access to new models |
| **Usage Tracking** | No tracking | Basic analytics | Advanced metrics + monitoring |
| **Code Obfuscation** | No | No | Yes (PyArmor protection) |
| **SLA** | No | No | 99.5% uptime guarantee |
| **Best For** | Students, researchers, hobbyists | Startups, production apps, consultancies | Enterprises, mission-critical systems |

### Why Upgrade?

**Community → Professional (+$49/month):**
- 3x more models (20 → 65)
- Advanced variants (BERT-large, ResNet-152, T5, BART)
- Domain-specific tools (forecasting, recommendations, GNNs)
- Email support for production issues
- **ROI:** Better accuracy = better decisions = business value

**Professional → Enterprise (+$250/month):**
- Full model catalog (65 → 105)
- Cutting-edge AI (7B LLMs, SAM, AlphaFold2, Stable Diffusion)
- 99.5% uptime SLA
- Dedicated support engineer
- Code protection (PyArmor obfuscation)
- **ROI:** Enterprise-grade reliability + exclusive models = competitive advantage

---

## Practical Impact

The Model Zoo powers work that matters:  

- **Labor & Employment:** Forecasting job trends, analyzing workforce shifts, and tracking equity gaps.  
- **Housing & Urban Development:** Modeling affordability, detecting displacement, and identifying price volatility.  
- **Income & Inequality:** Measuring economic disparity, mobility, and opportunity over time.  
- **Public Health:** Linking health indicators with economic and environmental conditions.  
- **Regional Development:** Assessing industrial strengths, resilience, and competitiveness.  

Each model is field-tested, policy-relevant, and community-accessible.

---

## Quick Start

### Installation

**Install from PyPI** (recommended):
```bash
pip install krl-model-zoo
```

> **📝 Note about PATH Warnings:**  
> During installation, you may see warnings like:  
> `WARNING: The scripts tqdm, transformers-cli are installed in '/path/to/bin' which is not on PATH.`
>
> **This is normal and can be safely ignored.** These warnings come from dependencies (like `transformers`, `tqdm`) installing command-line tools. The KRL Model Zoo library itself works perfectly via Python imports - you don't need these CLI tools.
>
> Only add the directory to PATH if you specifically need to use dependency CLI commands. See [INSTALLATION.md](INSTALLATION.md) for detailed solutions.
>
> **Check your environment:** Run `python -m krl_model_zoo.env_check` for diagnostics and recommendations.

**Install with optional dependencies**:
```bash
# For development
pip install krl-model-zoo[dev]

# For testing
pip install krl-model-zoo[test]

# For documentation
pip install krl-model-zoo[docs]

# All optional dependencies
pip install krl-model-zoo[all]
```

**Install from source**:
```bash
git clone https://github.com/KR-Labs/krl-model-zoo.git
cd krl-model-zoo
pip install -e .
```

**Complete ecosystem setup**:
```bash
# Install Model Zoo + Data Connectors for seamless data access
pip install krl-model-zoo krl-data-connectors
```

### Complete Workflow Example
```python
# Step 1: Fetch data using KRL Data Connectors
from krl_data_connectors import BLSConnector
from krl_models.econometric import SARIMAModel
from krl_models.core import ModelInputSchema, ModelMetadata
import numpy as np

# Get unemployment data from BLS
bls = BLSConnector()
unemployment_data = bls.get_series('LNS14000000', start_year=2015, end_year=2024)

# Step 2: Prepare data for modeling
# Create input schema with actual field names
schema = ModelInputSchema(
    y=unemployment_data['value'].values,  # Required: target as numpy array
    X=None,  # No exogenous variables for univariate series
    params={},
    feature_names=None
)

# Create model metadata
meta = ModelMetadata(
    name='unemployment_forecast',
    version='1.0.0',
    author='YourName',
    description='SARIMA forecast for US unemployment',
    tags=['unemployment', 'BLS', 'forecast']
)

# Step 3: Create and fit model
model = SARIMAModel(
    input_schema=schema,
    params={'order': (1, 1, 1), 'seasonal_order': (0, 0, 0, 0), 'trend': 'c'},
    meta=meta
)

# Fit and forecast
result = model.fit()
forecast = model.forecast(steps=12, confidence_level=0.95)

# Access forecast results
print(f"Forecast values: {forecast.forecast_values}")
print(f"Lower CI: {forecast.ci_lower}")
print(f"Upper CI: {forecast.ci_upper}")
```

### Standalone Usage (Without Data Connectors)
```python
from krl_models.econometric import SARIMAModel
from krl_models.core import ModelInputSchema, ModelMetadata
import pandas as pd
import numpy as np

# Use your own data
data = pd.read_csv('your_data.csv')

# Create input schema
schema = ModelInputSchema(
    y=data['value'].values,  # Your target variable
    X=None,  # Optional: exogenous features
    params={},
    feature_names=None
)

# Create metadata
meta = ModelMetadata(
    name='my_forecast',
    version='1.0.0',
    author='YourName',
    description='Custom SARIMA forecast',
    tags=['custom', 'forecast']
)

# Forecast with SARIMA
model = SARIMAModel(
    input_schema=schema,
    params={'order': (1, 1, 1), 'seasonal_order': (1, 1, 1, 12), 'trend': 'c'},
    meta=meta
)
result = model.fit()
forecast = model.forecast(steps=12)

print(f"12-month forecast: {forecast.forecast_values}")
```

### Explore Example Notebooks
Visit `/examples/notebooks/` for guided walkthroughs:  
- **End-to-End Workflows:** Fetching data with Connectors + analyzing with Model Zoo
- Forecasting labor market trends with BLS data
- Regional specialization analysis using Census CBP data  
- Housing market volatility with HUD Fair Market Rent data
- Anomaly detection in CDC health indicators
- Multi-source integration: combining FRED, BLS, and Census data  

---

## Community & Collaboration

KR-Labs thrives on **open collaboration** and shared intelligence.  

You can:
- Contribute new models, tutorials, or datasets  
- Report issues or propose features  
- Share research Mapplications and case studies  
- Join our growing community of open-data practitioners  

See our [Contributing Guide](./CONTRIBUTING.md) for details.  
Join the discussion at [GitHub Discussions](https://github.com/KR-Labs/krl-model-zoo/discussions).

---

## Governance & Roadmap

The Model Zoo evolves through the **KR-Labs Gate Framework**, ensuring transparent, high-quality development:

| Gate | Description | Status |
|------|--------------|---------|
| **Gate 1 – Foundation** | Time series & econometric core | Open-Source |
| **Gate 2 – Domain Models** | Regional & anomaly detection | Open-Source |
| **Gate 3 – Ensembles** | Meta-models and hybrid systems | Enterprise App|
| **Gate 4 – Advanced Extensions** | Causal inference, Bayesian, network models | Enterprise App |

Each Gate reflects a maturity milestone balancing innovation, stability, and community feedback.

---

## KR-Labs Ecosystem

The Model Zoo is part of a broader **open-source intelligence platform**:

| Repository | Purpose | Status |
|------------|---------|--------|
| **[krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo)** | Statistical models & analytical frameworks | Production |
| **[krl-data-connectors](https://github.com/KR-Labs/krl-data-connectors)** | Unified API for 20+ federal data sources | Production |

### Why This Matters

**Traditional Approach:**
1. Manually download CSVs from multiple government websites
2. Write custom parsers for each data format
3. Clean and normalize data structures
4. Finally begin analysis

**KR-Labs Approach:**
1. `pip install krl-data-connectors krl-model-zoo`
2. Write analysis code immediately
3. Results in minutes, not days

**Key Benefits:**
- **Single API** for Census, BLS, FRED, CDC, HUD, and more
- **Pre-validated data** compatible with Model Zoo methods
- **Reproducible workflows** from data fetch to final analysis
- **Version control** for both data retrieval and model parameters
- **Community support** for common use cases and patterns

---

## Documentation

📚 **[Full Documentation on ReadTheDocs](https://krl-model-zoo.readthedocs.io/)** *(Coming Soon)*

### Quick Links

- **[Quickstart Guide](./docs/quickstart.rst)** – Get started in 5 minutes
- **[User Guide](./docs/user_guide/index.rst)** – Comprehensive usage documentation
- **[API Reference](./docs/api/index.rst)** – Complete API documentation
- **[Contributing Guide](./docs/contributing.rst)** – Join our open-source community
- **[Development Guide](./docs/development.rst)** – Architecture and development practices
- **[Testing Guide](./docs/testing.rst)** – Quality assurance and test framework

### Example Code

- **[Python Examples](./examples/)** – Standalone Python scripts demonstrating model usage
- **[Jupyter Notebooks](./examples/notebooks/)** – Interactive tutorials with real datasets

### Related Documentation

- **[KRL Data Connectors](https://github.com/KR-Labs/krl-data-connectors)** – Integrate with 20+ federal data sources  

---

## Licensing

- **Software:** [Apache 2.0 License](./LICENSE) – Free for academic and commercial use  
- **Documentation:** [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)  

KR-Labs™ and KRL Model Zoo™ are trademarks of **Deloatch, Williams, Faison, & Parker, LLLP**.

---

## Citation

If you use the KRL Model Zoo in research or analysis, please cite:

```bibtex
@software{krl-model-zoo,
  author = {Deloatch, Brandon C.},
  title = {KRL Model Zoo: Open-Source Socioeconomic Modeling Framework},
  Year = {2025},
  publisher = {KR-Labs},
  version = {1.0.0},
  url = {https://github.com/KR-Labs/krl-model-zoo}
}
```

---

## Contact & Support

- **Website:** [krlabs.dev](https://krlabs.dev)  
- **Email:** support@krlabs.dev  
- **GitHub Discussions:** [Join the conversation](https://github.com/KR-Labs/krl-model-zoo/discussions)  

---

<div align="center">
  <img src="./assets/images/KRLabs_WebLogo.png" alt="KR-Labs" width="150">
  
  **KR-Labs™ | Building Open Intelligence for the Public Good**
  
  Version 1.0.0 • [Apache 2.0 License](./LICENSE)
  
</div>

---

## Legal & Trademark Notice

© 2025 KR-Labs. All rights reserved.

**KR-Labs™** and **KRL Model Zoo™** are trademarks of Deloatch, Williams, Faison, & Parker, LLLP

**Software License:** [Apache 2.0](./LICENSE) – Free for commercial and academic use  
**Documentation License:** [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)

---
