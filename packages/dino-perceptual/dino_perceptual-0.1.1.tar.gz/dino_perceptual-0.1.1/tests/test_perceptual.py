"""Tests for DINO perceptual loss."""

import pytest
import torch


class TestDINOPerceptualImport:
    """Test that the package imports correctly."""

    def test_import_dino_perceptual(self):
        from dino_perceptual import DINOPerceptual
        assert DINOPerceptual is not None

    def test_import_dino_model(self):
        from dino_perceptual import DINOModel
        assert DINOModel is not None

    def test_version(self):
        import dino_perceptual
        assert hasattr(dino_perceptual, "__version__")
        assert dino_perceptual.__version__ == "0.1.1"


class TestDINOPerceptualInit:
    """Test DINOPerceptual initialization (no model loading)."""

    def test_init_default(self):
        from dino_perceptual import DINOPerceptual
        # Just test that init doesn't fail (model loads lazily or on first forward)
        loss_fn = DINOPerceptual(model_size="B")
        assert loss_fn is not None
        assert loss_fn.model_size == "B"
        assert loss_fn.version == "v3"

    def test_init_v2(self):
        from dino_perceptual import DINOPerceptual
        loss_fn = DINOPerceptual(model_size="B", version="v2")
        assert loss_fn.version == "v2"

    def test_init_custom_target_size(self):
        from dino_perceptual import DINOPerceptual
        loss_fn = DINOPerceptual(model_size="B", target_size=256)
        assert loss_fn.target_size == 256


class TestDINOModelInit:
    """Test DINOModel initialization."""

    def test_init_default(self):
        from dino_perceptual import DINOModel
        model = DINOModel(model_size="B")
        assert model is not None
        assert model.model_size == "B"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
class TestDINOPerceptualForward:
    """Test forward pass (requires GPU and model weights)."""

    def test_forward_same_image(self):
        from dino_perceptual import DINOPerceptual

        loss_fn = DINOPerceptual(model_size="B").cuda().eval()

        # Create random images in [-1, 1] range
        x = torch.randn(2, 3, 256, 256).cuda()
        x = x.clamp(-1, 1)

        # Same image should have zero loss
        loss = loss_fn(x, x)
        assert loss.shape == (2,)
        assert torch.allclose(loss, torch.zeros_like(loss), atol=1e-5)

    def test_forward_different_images(self):
        from dino_perceptual import DINOPerceptual

        loss_fn = DINOPerceptual(model_size="B").cuda().eval()

        x1 = torch.randn(2, 3, 256, 256).cuda().clamp(-1, 1)
        x2 = torch.randn(2, 3, 256, 256).cuda().clamp(-1, 1)

        loss = loss_fn(x1, x2)
        assert loss.shape == (2,)
        assert (loss > 0).all()

    def test_forward_gradient(self):
        from dino_perceptual import DINOPerceptual

        loss_fn = DINOPerceptual(model_size="B").cuda().eval()

        x1 = torch.randn(1, 3, 256, 256, requires_grad=True).cuda()
        x2 = torch.randn(1, 3, 256, 256).cuda()

        loss = loss_fn(x1, x2).mean()
        loss.backward()

        assert x1.grad is not None
        assert x1.grad.shape == x1.shape
