"""Custom neural network architectures for the vision module."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


def _require_torch():
    try:
        import torch
        import torch.nn as nn
        return torch, nn
    except ImportError as exc:
        raise ImportError(
            "torch is required for custom model architectures. "
            "Install with: pip install torch"
        ) from exc


class SimpleCNN:
    """Lightweight CNN for image classification.

    Architecture: 3 conv blocks (conv-BN-ReLU-pool) followed by two
    fully-connected layers.

    Example::

        model = SimpleCNN(num_classes=10)
        output = model(image_tensor)   # (B, num_classes)
    """

    def __new__(
        cls,
        num_classes: int = 10,
        in_channels: int = 3,
        hidden_dim: int = 256,
    ):
        """
        Args:
            num_classes: Number of output classes.
            in_channels: Number of input channels (3 for RGB).
            hidden_dim: Size of the hidden FC layer.
        """
        torch, nn = _require_torch()

        class _SimpleCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(in_channels, 32, 3, padding=1),
                    nn.BatchNorm2d(32),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(2),

                    nn.Conv2d(32, 64, 3, padding=1),
                    nn.BatchNorm2d(64),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(2),

                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.BatchNorm2d(128),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(2),
                )
                self.pool = nn.AdaptiveAvgPool2d((4, 4))
                self.classifier = nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(128 * 4 * 4, hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.Dropout(0.5),
                    nn.Linear(hidden_dim, num_classes),
                )

            def forward(self, x):
                x = self.features(x)
                x = self.pool(x)
                return self.classifier(x)

        return _SimpleCNN()


class UNet:
    """U-Net encoder-decoder for semantic segmentation.

    Uses skip connections from encoder to decoder.

    Example::

        model = UNet(in_channels=3, num_classes=21)
        seg_map = model(image_tensor)   # (B, num_classes, H, W)
    """

    def __new__(
        cls,
        in_channels: int = 3,
        num_classes: int = 21,
        features: Optional[List[int]] = None,
    ):
        """
        Args:
            in_channels: Input channels.
            num_classes: Number of segmentation classes.
            features: Channel counts for each encoder stage.
        """
        torch, nn = _require_torch()

        if features is None:
            features = [64, 128, 256, 512]

        class _DoubleConv(nn.Module):
            def __init__(self, in_ch, out_ch):
                super().__init__()
                self.net = nn.Sequential(
                    nn.Conv2d(in_ch, out_ch, 3, padding=1),
                    nn.BatchNorm2d(out_ch),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(out_ch, out_ch, 3, padding=1),
                    nn.BatchNorm2d(out_ch),
                    nn.ReLU(inplace=True),
                )

            def forward(self, x):
                return self.net(x)

        class _UNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoders = nn.ModuleList()
                self.pool = nn.MaxPool2d(2)
                ch = in_channels
                for f in features:
                    self.encoders.append(_DoubleConv(ch, f))
                    ch = f

                self.bottleneck = _DoubleConv(features[-1], features[-1] * 2)

                self.decoders = nn.ModuleList()
                self.up_convs = nn.ModuleList()
                rev_features = list(reversed(features))
                in_ch = features[-1] * 2
                for f in rev_features:
                    self.up_convs.append(
                        nn.ConvTranspose2d(in_ch, f, 2, stride=2)
                    )
                    self.decoders.append(_DoubleConv(f * 2, f))
                    in_ch = f

                self.head = nn.Conv2d(features[0], num_classes, 1)

            def forward(self, x):
                skips = []
                for enc in self.encoders:
                    x = enc(x)
                    skips.append(x)
                    x = self.pool(x)
                x = self.bottleneck(x)
                for up, dec, skip in zip(
                    self.up_convs, self.decoders, reversed(skips)
                ):
                    x = up(x)
                    # Handle size mismatch
                    if x.shape != skip.shape:
                        import torch.nn.functional as F
                        x = F.interpolate(x, size=skip.shape[2:])
                    x = torch.cat([skip, x], dim=1)
                    x = dec(x)
                return self.head(x)

        return _UNet()


class DetectionHead:
    """Anchor-free detection head for custom object detection backbones.

    Outputs class logits and bounding-box regression offsets.

    Example::

        head = DetectionHead(in_channels=256, num_classes=80)
        cls_out, box_out = head(feature_map)
    """

    def __new__(
        cls,
        in_channels: int = 256,
        num_classes: int = 80,
        num_anchors: int = 1,
    ):
        """
        Args:
            in_channels: Input feature map channels.
            num_classes: Number of object categories.
            num_anchors: Number of anchors per spatial location.
        """
        torch, nn = _require_torch()

        class _DetectionHead(nn.Module):
            def __init__(self):
                super().__init__()
                self.cls_conv = nn.Sequential(
                    nn.Conv2d(in_channels, in_channels, 3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels, num_classes * num_anchors, 1),
                )
                self.reg_conv = nn.Sequential(
                    nn.Conv2d(in_channels, in_channels, 3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels, 4 * num_anchors, 1),
                )

            def forward(self, x):
                return self.cls_conv(x), self.reg_conv(x)

        return _DetectionHead()
