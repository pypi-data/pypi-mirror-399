# DINO Perceptual Loss

A drop-in replacement for LPIPS using DINOv2/v3 features. Achieves comparable perceptual quality to VGG-based LPIPS while using modern self-supervised features—no human perceptual judgments required.

**[Read the full documentation and benchmarks](https://na-vae.github.io/dino_perceptual/)**

## Installation

```bash
pip install dino-perceptual
```

## Quick Start

```python
import torch
from dino_perceptual import DINOPerceptual

# Initialize loss function (uses DINOv3 by default)
loss_fn = DINOPerceptual(model_size="B").cuda().bfloat16().eval()
loss_fn = torch.compile(loss_fn, fullgraph=True)

# Compute perceptual loss between two images
# Images should be tensors in [-1, 1] range with shape (B, 3, H, W)
loss = loss_fn(predicted, target).mean()
```

## Usage in Autoencoder Training

```python
import torch
import torch.nn as nn
from dino_perceptual import DINOPerceptual

autoencoder = MyAutoencoder().cuda().bfloat16()
perceptual_loss = DINOPerceptual(model_size="B").cuda().bfloat16().eval()
perceptual_loss = torch.compile(perceptual_loss, fullgraph=True)
optimizer = torch.optim.Adam(autoencoder.parameters(), lr=1e-4)

for images in dataloader:
    images = images.cuda().bfloat16()
    reconstructed = autoencoder(images)

    l1_loss = nn.functional.l1_loss(reconstructed, images)
    dino_loss = perceptual_loss(reconstructed, images).mean()

    # DINO weight ~250-1000 works well
    total_loss = l1_loss + 250.0 * dino_loss

    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()
```

## HuggingFace Authentication

DINOv2/v3 models require accepting the license on HuggingFace:

1. Accept the license at [DINOv2](https://huggingface.co/facebook/dinov2-base) or [DINOv3](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m)
2. Create a token at https://huggingface.co/settings/tokens
3. Set `HF_TOKEN` environment variable or run `huggingface-cli login`

## API Reference

```python
DINOPerceptual(
    model_size: str = "B",   # "S", "B", "L", "H", or "G"
    version: str = "v3",     # "v2" or "v3"
    target_size: int = 512,  # Resize images before computing features
    layers: str = "all",     # Which transformer layers to use
)
```

For feature extraction (e.g., computing FDD):

```python
from dino_perceptual import DINOModel

extractor = DINOModel(model_size="B").cuda().bfloat16().eval()
features, cls_token = extractor(images)  # features: (B, feature_dim)
```

## License

MIT

## Citation

```bibtex
@software{dino_perceptual,
  title={DINO Perceptual Loss},
  author={Hansen-Estruch, Philippe and Chen, Jiahui and Ramanujan, Vivek and Zohar, Orr and Ping, Yan and Sinha, Animesh and Georgopoulos, Markos and Schoenfeld, Edgar and Hou, Ji and Juefei-Xu, Felix and Vishwanath, Sriram and Thabet, Ali},
  year={2025},
  url={https://github.com/Na-VAE/dino-perceptual}
}
```
