# InterpUseCases_v2

Mechanical Interpretation Use Cases - A comprehensive collection of interpretability research and applications.

## Overview

This repository contains various use cases for mechanical interpretation, including:

- **AgenticTracing**: Tool-intent tracing with SAE features for financial agents
- **FinbertSentiment**: Sentiment analysis using FinBERT and SAE features
- **COT_Reasoning**: Chain-of-thought reasoning analysis
- **EndtoEnd**: End-to-end training pipelines
- **hallucination_token_level**: Token-level hallucination detection
- **SearchSteer**: Search and steering features
- **Trading**: Trading-related use cases
- **Trading_with_stats**: Trading with statistical analysis

## Repository Structure

```
InterpUseCases_v2/
├── AgenticTracing/          # Agent tool-intent tracing
├── FinbertSentiment/        # Financial sentiment analysis
├── COT_Reasoning/           # Chain-of-thought reasoning
├── EndtoEnd/                # End-to-end training
├── hallucination_token_level/  # Hallucination detection
├── SearchSteer/             # Search and steering
├── Trading/                 # Trading use cases
├── Trading_with_stats/      # Trading with statistics
├── saetrain/                # SAE training utilities
└── requirements.txt         # Python dependencies
```

## Excluded Files

The following are excluded from this repository (see `.gitignore`):

- Large model files (`.safetensors`, `.pt`, `.pth`, `.bin`)
- Cache directories (`__pycache__`, `.cache`, `wandb/`)
- Archive folders
- Large image files (except documentation)
- Virtual environments
- IDE configuration files

## Setup

1. Clone the repository:
```bash
git clone https://github.com/tatsath/InterpUseCases_v2.git
cd InterpUseCases_v2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Each subdirectory contains its own README with specific setup instructions.

## Documentation

See `UNIFIED_PAPER.md` for comprehensive documentation of all use cases.

## License

[Add your license here]

## Contact

[Add contact information here]










