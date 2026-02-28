# Pretrained Model Weights

This directory stores pretrained neural network weights for the platform's simulated models.

## Directory Structure

```
pretrained_weights/
├── bert/
│   ├── bert-base-uncased.bin      # BERT base weights (~440MB)
│   ├── bert-large-uncased.bin     # BERT large weights (~1.3GB)
│   └── bert-base-multilingual.bin # Multilingual BERT (~680MB)
├── gpt/
│   ├── gpt2-small.bin             # GPT-2 small weights (~548MB)
│   ├── gpt2-medium.bin            # GPT-2 medium weights (~1.5GB)
│   └── gpt3-simulated.bin         # Simulated GPT-3 weights
├── t5/
│   ├── t5-small.bin               # T5 small weights (~242MB)
│   └── t5-base.bin                # T5 base weights (~892MB)
└── domain_specific/
    ├── infra-bert.bin             # Infrastructure-tuned BERT
    ├── ops-gpt.bin                # DevOps-tuned GPT
    └── ml-t5.bin                  # ML-domain-tuned T5
```

## Downloading Weights

Since this is a simulated platform, the neural network models use heuristic
implementations that do not require actual weight files.

For production deployments with real neural networks, download weights from:

### Hugging Face Hub

```bash
# Install huggingface-hub
pip install huggingface-hub

# Download BERT base
python -c "from huggingface_hub import hf_hub_download; hf_hub_download('bert-base-uncased', 'pytorch_model.bin', local_dir='bert/')"

# Download GPT-2
python -c "from huggingface_hub import hf_hub_download; hf_hub_download('gpt2', 'pytorch_model.bin', local_dir='gpt/')"

# Download T5 small
python -c "from huggingface_hub import hf_hub_download; hf_hub_download('t5-small', 'pytorch_model.bin', local_dir='t5/')"
```

### Manual Download Links

| Model | Source | Size |
|-------|--------|------|
| BERT Base Uncased | https://huggingface.co/bert-base-uncased | 440MB |
| GPT-2 Small | https://huggingface.co/gpt2 | 548MB |
| T5 Small | https://huggingface.co/t5-small | 242MB |

## Weight Format

All weights should be saved in PyTorch `.bin` format or ONNX `.onnx` format
for cross-framework compatibility.

## Versioning

Weight files follow semantic versioning in the format:
`{model_name}-v{major}.{minor}.{patch}.bin`

## License

Pretrained weights are subject to their respective model licenses.
Check individual model cards on Hugging Face for license details.
