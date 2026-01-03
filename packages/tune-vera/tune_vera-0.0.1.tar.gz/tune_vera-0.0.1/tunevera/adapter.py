"""
VERA - ResNet Adapter with Bottleneck blocks

The adapter transforms embeddings using a residual network with bottleneck blocks
to reduce parameter count while maintaining expressiveness.

Parameter comparison (embedding_dim=1536, bottleneck_dim=256):
- Direct connection: 1536 * 1536 + bias = 2,360,832 params
- Bottleneck: (1536 * 256 + 256) + (256 * 1536 + 1536) = 788,224 params
- Reduction: ~66% fewer parameters per block
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from typing import Optional, List, Union, Tuple
import numpy as np
from tqdm import tqdm

from .data import EmbeddingDataset


class BottleneckBlock(nn.Module):
    """
    Residual block with bottleneck architecture.

    Architecture:
        x -> Linear(dim -> bottleneck) -> ReLU -> Dropout -> Linear(bottleneck -> dim) -> + x
                                                                                           |
        x ---------------------------------------------------------------------->---------+
    """

    def __init__(
        self,
        embedding_dim: int,
        bottleneck_dim: int,
        dropout: float = 0.1
    ):
        super().__init__()

        self.down = nn.Linear(embedding_dim, bottleneck_dim)
        self.up = nn.Linear(bottleneck_dim, embedding_dim)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(embedding_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        # Bottleneck transformation
        x = self.down(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.up(x)

        # Residual connection
        x = x + residual
        x = self.layer_norm(x)

        return x


class ImprovedBottleneckBlock(nn.Module):
    """
    Improved residual block with Pre-LayerNorm architecture.

    Architecture (Pre-LN):
        x -> LayerNorm -> Linear(down) -> GELU -> Dropout -> Linear(up) -> Dropout -> (*scale) -> (+x)

    Improvements over standard block:
    - Pre-LayerNorm: More stable training, better gradient flow
    - GELU activation: Smoother than ReLU, better for embeddings
    - Double dropout: After activation and after up projection
    - Residual scaling: Scale by 1/sqrt(num_blocks) for deep networks
    """

    def __init__(
        self,
        embedding_dim: int,
        bottleneck_dim: int,
        dropout: float = 0.1,
        residual_scale: float = 1.0
    ):
        super().__init__()

        self.layer_norm = nn.LayerNorm(embedding_dim)
        self.down = nn.Linear(embedding_dim, bottleneck_dim)
        self.up = nn.Linear(bottleneck_dim, embedding_dim)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.residual_scale = residual_scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        # Pre-LayerNorm
        x = self.layer_norm(x)

        # Bottleneck transformation with GELU
        x = self.down(x)
        x = F.gelu(x)
        x = self.dropout1(x)
        x = self.up(x)
        x = self.dropout2(x)

        # Scaled residual connection
        x = residual + x * self.residual_scale

        return x


class FullDimBlock(nn.Module):
    """
    Residual block WITHOUT bottleneck - maintains full dimensionality.

    Architecture:
        x -> LayerNorm -> Linear(dim -> dim) -> GELU -> Dropout -> Linear(dim -> dim) -> Dropout -> (*scale) -> (+x)

    This block avoids the information compression of bottleneck blocks,
    which can cause embedding space collapse when training with only positive pairs.
    """

    def __init__(
        self,
        embedding_dim: int,
        dropout: float = 0.1,
        residual_scale: float = 1.0
    ):
        super().__init__()

        self.layer_norm = nn.LayerNorm(embedding_dim)
        self.fc1 = nn.Linear(embedding_dim, embedding_dim)
        self.fc2 = nn.Linear(embedding_dim, embedding_dim)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.residual_scale = residual_scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        # Pre-LayerNorm
        x = self.layer_norm(x)

        # Full dimension transformation
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = self.dropout2(x)

        # Scaled residual connection
        x = residual + x * self.residual_scale

        return x


# =============================================================================
# Convolutional blocks (Conv1d on embeddings)
# =============================================================================

class ResNet2Block(nn.Module):
    """
    ResNet2 block with tanh activation and learnable scale.

    Architecture:
        x -> Linear(down) -> GELU -> Dropout -> LayerNorm -> Linear(up) -> tanh -> (*learnable_scale) -> (+x)

    Key features:
    - tanh activation before scaling (bounds output to [-1, 1])
    - Learnable scale parameter per block (initialized to 0.5)
    - LayerNorm in bottleneck space before up-projection
    - Up layer initialized to zero for near-identity start
    """

    def __init__(
        self,
        embedding_dim: int,
        bottleneck_dim: int,
        dropout: float = 0.1,
        initial_scale: float = 0.5
    ):
        super().__init__()

        self.down = nn.Linear(embedding_dim, bottleneck_dim)
        self.up = nn.Linear(bottleneck_dim, embedding_dim)
        self.dropout = nn.Dropout(dropout)
        self.bottleneck_norm = nn.LayerNorm(bottleneck_dim)

        # Learnable scale parameter, initialized to initial_scale
        self.scale = nn.Parameter(torch.tensor(initial_scale))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Current input (output from previous block)

        Returns:
            Transformed tensor: x + tanh(transform(x)) * scale
        """
        # Bottleneck transformation
        h = self.down(x)
        h = F.gelu(h)
        h = self.dropout(h)

        # LayerNorm in bottleneck space before up-projection
        h = self.bottleneck_norm(h)

        h = self.up(h)

        # tanh activation before scaling
        h = torch.tanh(h)

        # Scale by learnable parameter and add to block input
        return x + h * self.scale


class ResNet2Model(nn.Module):
    """
    ResNet2 model: stacks ResNet2Blocks with tanh and learnable scale.

    Each block adds to its own input (like standard ResNet), but uses
    tanh activation and a learnable scale parameter for controlled updates.
    """

    def __init__(
        self,
        embedding_dim: int,
        bottleneck_dim: int,
        num_blocks: int = 5,
        dropout: float = 0.1,
        initial_scale: float = 0.5
    ):
        super().__init__()

        self.embedding_dim = embedding_dim
        self.bottleneck_dim = bottleneck_dim
        self.num_blocks = num_blocks

        self.blocks = nn.ModuleList([
            ResNet2Block(embedding_dim, bottleneck_dim, dropout, initial_scale)
            for _ in range(num_blocks)
        ])

        self.final_norm = nn.LayerNorm(embedding_dim)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize up weights to zero (before tanh) for near-identity start"""
        for block in self.blocks:
            # Only zero the up layer (immediately before tanh)
            nn.init.zeros_(block.up.weight)
            if block.up.bias is not None:
                nn.init.zeros_(block.up.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Transform embeddings through ResNet2.

        Args:
            x: Input embeddings of shape (batch_size, embedding_dim)

        Returns:
            Transformed embeddings of shape (batch_size, embedding_dim)
        """
        for block in self.blocks:
            x = block(x)

        x = self.final_norm(x)
        return x

    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class ConvBottleneckBlock(nn.Module):
    """
    Residual block with 1D convolutions and bottleneck.

    Uses Conv1d to capture local patterns in the embedding space.
    Nearby dimensions in embeddings often encode related information.

    Architecture:
        x -> LayerNorm -> Conv1d(down) -> GELU -> Dropout -> Conv1d(up) -> Dropout -> (*scale) -> (+x)

    Input shape: (batch, embedding_dim)
    Internal: (batch, 1, embedding_dim) for Conv1d
    """

    def __init__(
        self,
        embedding_dim: int,
        bottleneck_dim: int,
        kernel_size: int = 3,
        dropout: float = 0.1,
        residual_scale: float = 1.0
    ):
        super().__init__()

        self.layer_norm = nn.LayerNorm(embedding_dim)
        padding = kernel_size // 2  # Same padding to preserve length

        # Down projection: 1 channel -> bottleneck_dim channels
        self.conv_down = nn.Conv1d(1, bottleneck_dim, kernel_size=kernel_size, padding=padding)
        # Up projection: bottleneck_dim channels -> 1 channel
        self.conv_up = nn.Conv1d(bottleneck_dim, 1, kernel_size=kernel_size, padding=padding)

        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.residual_scale = residual_scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, embedding_dim)
        residual = x

        # Pre-LayerNorm
        x = self.layer_norm(x)

        # Reshape for Conv1d: (batch, 1, embedding_dim)
        x = x.unsqueeze(1)

        # Convolution transformation
        x = self.conv_down(x)  # (batch, bottleneck_dim, embedding_dim)
        x = F.gelu(x)
        x = self.dropout1(x)
        x = self.conv_up(x)    # (batch, 1, embedding_dim)
        x = self.dropout2(x)

        # Reshape back: (batch, embedding_dim)
        x = x.squeeze(1)

        # Scaled residual connection
        x = residual + x * self.residual_scale

        return x


class ConvFullDimBlock(nn.Module):
    """
    Residual block with 1D convolutions without bottleneck.

    Uses multiple Conv1d layers with the same channel dimension.
    Captures local patterns while maintaining full expressiveness.

    Architecture:
        x -> LayerNorm -> Conv1d -> GELU -> Dropout -> Conv1d -> Dropout -> (*scale) -> (+x)
    """

    def __init__(
        self,
        embedding_dim: int,
        num_channels: int = 64,
        kernel_size: int = 3,
        dropout: float = 0.1,
        residual_scale: float = 1.0
    ):
        super().__init__()

        self.layer_norm = nn.LayerNorm(embedding_dim)
        padding = kernel_size // 2

        # Expand to multiple channels, then back to 1
        self.conv1 = nn.Conv1d(1, num_channels, kernel_size=kernel_size, padding=padding)
        self.conv2 = nn.Conv1d(num_channels, 1, kernel_size=kernel_size, padding=padding)

        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.residual_scale = residual_scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        # Pre-LayerNorm
        x = self.layer_norm(x)

        # Reshape for Conv1d
        x = x.unsqueeze(1)  # (batch, 1, embedding_dim)

        # Convolution transformation
        x = self.conv1(x)   # (batch, num_channels, embedding_dim)
        x = F.gelu(x)
        x = self.dropout1(x)
        x = self.conv2(x)   # (batch, 1, embedding_dim)
        x = self.dropout2(x)

        # Reshape back
        x = x.squeeze(1)    # (batch, embedding_dim)

        # Scaled residual connection
        x = residual + x * self.residual_scale

        return x


# =============================================================================
# Alternative architectures (simpler than ResNet, less prone to overfitting)
# =============================================================================

class LinearAdapter(nn.Module):
    """
    Simple linear projection + normalization.

    The simplest possible adapter - just rotates/scales the embedding space.
    Use this when embeddings are already high quality and only need minor adjustment.

    Parameters: dim * dim + dim (bias) ≈ 2.3M for dim=1536
    """

    def __init__(self, embedding_dim: int = 1536):
        super().__init__()
        self.proj = nn.Linear(embedding_dim, embedding_dim)
        self.norm = nn.LayerNorm(embedding_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        x = self.norm(x)
        return F.normalize(x, p=2, dim=-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class PEFTAdapter(nn.Module):
    """
    PEFT-style adapter with very small bottleneck.

    Used in parameter-efficient fine-tuning of LLMs. The key insight is:
    - Near-identity initialization: starts as almost passthrough
    - Small bottleneck: forces learning only essential transformations
    - Skip connection: preserves original embedding quality

    Parameters: 2 * dim * bottleneck ≈ 200K for dim=1536, bottleneck=64
    """

    def __init__(
        self,
        embedding_dim: int = 1536,
        bottleneck_dim: int = 64,
        dropout: float = 0.1
    ):
        super().__init__()
        self.down = nn.Linear(embedding_dim, bottleneck_dim)
        self.up = nn.Linear(bottleneck_dim, embedding_dim)
        self.norm = nn.LayerNorm(embedding_dim)
        self.dropout = nn.Dropout(dropout)

        # Near-identity initialization - crucial for PEFT adapters
        # Start with almost passthrough, let training find small adjustments
        nn.init.xavier_uniform_(self.down.weight)
        nn.init.zeros_(self.down.bias)
        nn.init.zeros_(self.up.weight)  # Output starts at zero
        nn.init.zeros_(self.up.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x

        x = self.norm(x)
        x = self.down(x)
        x = F.gelu(x)
        x = self.dropout(x)
        x = self.up(x)

        # Skip connection - starts as identity due to zero init
        x = residual + x
        return F.normalize(x, p=2, dim=-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class TwoLayerMLP(nn.Module):
    """
    Simple 2-layer MLP - maximum depth before overfitting becomes severe.

    A middle ground between linear projection and ResNet.
    Hidden dimension controls capacity.

    Parameters: dim * hidden + hidden * dim ≈ 1.5M for dim=1536, hidden=512
    """

    def __init__(
        self,
        embedding_dim: int = 1536,
        hidden_dim: int = 512,
        dropout: float = 0.1
    ):
        super().__init__()
        self.norm = nn.LayerNorm(embedding_dim)
        self.fc1 = nn.Linear(embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embedding_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.norm(x)
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return F.normalize(x, p=2, dim=-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class VeraAdapterModel(nn.Module):
    """
    ResNet adapter model for transforming embeddings.

    The model consists of multiple residual blocks stacked together,
    each with a skip connection to enable gradient flow.
    """

    def __init__(
        self,
        embedding_dim: int = 1536,
        bottleneck_dim: int = 256,
        num_blocks: int = 5,
        dropout: float = 0.1,
        use_improved_arch: bool = False,
        use_bottleneck: bool = True,
        use_conv: bool = False,
        kernel_size: int = 3,
        num_channels: int = 64
    ):
        super().__init__()

        self.embedding_dim = embedding_dim
        self.bottleneck_dim = bottleneck_dim
        self.num_blocks = num_blocks
        self.use_improved_arch = use_improved_arch
        self.use_bottleneck = use_bottleneck
        self.use_conv = use_conv

        residual_scale = 1.0 / (num_blocks ** 0.5)

        # Stack of blocks
        if use_conv:
            # Convolutional blocks
            if use_bottleneck:
                self.blocks = nn.ModuleList([
                    ConvBottleneckBlock(embedding_dim, bottleneck_dim, kernel_size, dropout, residual_scale)
                    for _ in range(num_blocks)
                ])
            else:
                self.blocks = nn.ModuleList([
                    ConvFullDimBlock(embedding_dim, num_channels, kernel_size, dropout, residual_scale)
                    for _ in range(num_blocks)
                ])
            self.final_norm = nn.LayerNorm(embedding_dim)
        elif not use_bottleneck:
            # Full dimension blocks (no bottleneck) - recommended to avoid embedding collapse
            self.blocks = nn.ModuleList([
                FullDimBlock(embedding_dim, dropout, residual_scale)
                for _ in range(num_blocks)
            ])
            self.final_norm = nn.LayerNorm(embedding_dim)
        elif use_improved_arch:
            # Improved architecture with Pre-LN, GELU, and residual scaling
            self.blocks = nn.ModuleList([
                ImprovedBottleneckBlock(embedding_dim, bottleneck_dim, dropout, residual_scale)
                for _ in range(num_blocks)
            ])
            self.final_norm = nn.LayerNorm(embedding_dim)
        else:
            # Original architecture
            self.blocks = nn.ModuleList([
                BottleneckBlock(embedding_dim, bottleneck_dim, dropout)
                for _ in range(num_blocks)
            ])
            self.final_norm = None

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights for better training"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Conv1d):
                nn.init.kaiming_uniform_(module.weight, nonlinearity='relu')
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Transform embeddings through the ResNet.

        Args:
            x: Input embeddings of shape (batch_size, embedding_dim)

        Returns:
            Transformed embeddings of shape (batch_size, embedding_dim)
        """
        for block in self.blocks:
            x = block(x)

        # Apply final normalization for improved architecture
        if self.final_norm is not None:
            x = self.final_norm(x)

        return x

    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class VeraAdapter:
    """
    High-level adapter class for training and inference.

    Trains the adapter to transform question embeddings to be similar
    to their corresponding answer embeddings.
    """

    # Valid architecture types
    ARCH_TYPES = ["resnet", "resnet2", "linear", "adapter", "mlp"]

    # Valid loss types
    LOSS_TYPES = [
        "cosine",           # Original cosine + MSE loss
        "contrastive",      # InfoNCE in-batch contrastive
        "triplet",          # Triplet margin loss with hard negative mining
        "mnrl",             # Multiple Negatives Ranking Loss (symmetric)
        "circle",           # Circle Loss (dynamic weighting)
        "hard_negative",    # Hard negative contrastive (top-k hardest)
        "cosine_margin",    # CosFace-style angular margin
        "poly",             # PolyLoss (polynomial expansion)
        "ntxent",           # NT-Xent (SimCLR style)
    ]

    def __init__(
        self,
        embedding_dim: int = 1536,
        bottleneck_dim: int = 256,
        num_blocks: int = 5,
        epochs: int = 10,
        batch_size: int = 32,
        dropout: float = 0.1,
        learning_rate: float = 1e-4,
        cosine_weight: float = 1.0,
        use_improved_arch: bool = False,
        use_bottleneck: bool = True,
        use_conv: bool = False,
        kernel_size: int = 3,
        num_channels: int = 64,
        loss_type: str = "cosine",
        temperature: float = 0.1,
        label_smoothing: float = 0.1,
        weight_decay: float = 0.01,
        early_stopping_patience: int = 0,
        arch_type: str = "resnet",
        hidden_dim: int = 512,
        initial_scale: float = 0.5,
        margin: float = 0.2,
        hard_neg_k: int = 5,
        poly_epsilon: float = 1.0,
        device: Optional[str] = None
    ):
        """
        Initialize the VERA adapter.

        Args:
            embedding_dim: Dimension of input/output embeddings
            bottleneck_dim: Dimension of bottleneck layer (for resnet/adapter architectures)
            num_blocks: Number of residual blocks (only for resnet architecture)
            epochs: Number of training epochs
            batch_size: Training batch size
            dropout: Dropout rate
            learning_rate: Optimizer learning rate
            cosine_weight: Weight for cosine loss (0-1). Only used when loss_type="cosine".
            use_improved_arch: Use improved ResNet architecture. Only for arch_type="resnet".
            use_bottleneck: Use bottleneck blocks in ResNet. Only for arch_type="resnet".
            use_conv: Use Conv1d instead of Linear layers. Only for arch_type="resnet".
                     Captures local patterns in embedding dimensions.
            kernel_size: Kernel size for Conv1d layers. Only used if use_conv=True.
            num_channels: Number of channels for ConvFullDimBlock. Only used if use_conv=True.
            loss_type: Loss function to use. Options:
                      - "cosine": Original cosine + MSE loss
                      - "contrastive": InfoNCE in-batch contrastive (recommended, prevents collapse)
                      - "triplet": Triplet margin loss with in-batch hard negative mining
                      - "mnrl": Multiple Negatives Ranking Loss (symmetric, robust)
                      - "circle": Circle Loss (dynamic weighting, state-of-the-art)
                      - "hard_negative": Hard negative contrastive (focuses on top-k hardest)
                      - "cosine_margin": CosFace-style angular margin loss
                      - "poly": PolyLoss (polynomial expansion of CE)
                      - "ntxent": NT-Xent loss (SimCLR style, bidirectional)
            temperature: Temperature for contrastive losses. Higher = softer predictions.
            label_smoothing: Smoothing for contrastive losses. Reduces overconfidence.
            weight_decay: L2 regularization strength.
            early_stopping_patience: Stop if val_loss doesn't improve for N epochs. 0 = disabled.
            arch_type: Architecture type. Options:
                      - "resnet": Original ResNet with residual blocks (most parameters)
                      - "resnet2": ResNet that always adds to original input, with tanh and learnable scale
                      - "linear": Simple linear projection (simplest, ~2.3M params)
                      - "adapter": PEFT-style adapter with small bottleneck (~200K params) [RECOMMENDED]
                      - "mlp": 2-layer MLP (~1.5M params)
            hidden_dim: Hidden dimension for MLP architecture.
            initial_scale: Initial value for learnable scale in resnet2 (default 0.5).
            margin: Margin for triplet, circle, and cosine_margin losses (default 0.2).
            hard_neg_k: Number of hard negatives for hard_negative loss (default 5).
            poly_epsilon: Epsilon coefficient for PolyLoss (default 1.0).
            device: Device to use ("cuda" or "cpu")
        """
        if arch_type not in self.ARCH_TYPES:
            raise ValueError(f"arch_type must be one of {self.ARCH_TYPES}, got '{arch_type}'")

        if loss_type not in self.LOSS_TYPES:
            raise ValueError(f"loss_type must be one of {self.LOSS_TYPES}, got '{loss_type}'")

        self.embedding_dim = embedding_dim
        self.bottleneck_dim = bottleneck_dim
        self.num_blocks = num_blocks
        self.epochs = epochs
        self.batch_size = batch_size
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.cosine_weight = cosine_weight
        self.use_improved_arch = use_improved_arch
        self.use_bottleneck = use_bottleneck
        self.use_conv = use_conv
        self.kernel_size = kernel_size
        self.num_channels = num_channels
        self.loss_type = loss_type
        self.temperature = temperature
        self.label_smoothing = label_smoothing
        self.weight_decay = weight_decay
        self.early_stopping_patience = early_stopping_patience
        self.arch_type = arch_type
        self.hidden_dim = hidden_dim
        self.initial_scale = initial_scale
        self.margin = margin
        self.hard_neg_k = hard_neg_k
        self.poly_epsilon = poly_epsilon

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Create model based on architecture type
        self.model = self._create_model()

        # Training state
        self.is_trained = False
        self.train_history = []

    def _create_model(self) -> nn.Module:
        """Create the model based on arch_type."""
        if self.arch_type == "linear":
            model = LinearAdapter(embedding_dim=self.embedding_dim)
        elif self.arch_type == "adapter":
            model = PEFTAdapter(
                embedding_dim=self.embedding_dim,
                bottleneck_dim=self.bottleneck_dim,
                dropout=self.dropout
            )
        elif self.arch_type == "mlp":
            model = TwoLayerMLP(
                embedding_dim=self.embedding_dim,
                hidden_dim=self.hidden_dim,
                dropout=self.dropout
            )
        elif self.arch_type == "resnet2":
            model = ResNet2Model(
                embedding_dim=self.embedding_dim,
                bottleneck_dim=self.bottleneck_dim,
                num_blocks=self.num_blocks,
                dropout=self.dropout,
                initial_scale=self.initial_scale
            )
        else:  # resnet (default)
            model = VeraAdapterModel(
                embedding_dim=self.embedding_dim,
                bottleneck_dim=self.bottleneck_dim,
                num_blocks=self.num_blocks,
                dropout=self.dropout,
                use_conv=self.use_conv,
                kernel_size=self.kernel_size,
                num_channels=self.num_channels,
                use_improved_arch=self.use_improved_arch,
                use_bottleneck=self.use_bottleneck
            )
        return model.to(self.device)

    def _compute_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Compute loss based on loss_type.

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Loss value
        """
        if self.loss_type == "contrastive":
            return self._contrastive_loss(queries, docs)
        elif self.loss_type == "triplet":
            return self._triplet_loss(queries, docs)
        elif self.loss_type == "mnrl":
            return self._mnrl_loss(queries, docs)
        elif self.loss_type == "circle":
            return self._circle_loss(queries, docs)
        elif self.loss_type == "hard_negative":
            return self._hard_negative_loss(queries, docs)
        elif self.loss_type == "cosine_margin":
            return self._cosine_margin_loss(queries, docs)
        elif self.loss_type == "poly":
            return self._poly_loss(queries, docs)
        elif self.loss_type == "ntxent":
            return self._ntxent_loss(queries, docs)
        else:
            # Default: original cosine + MSE loss
            cos_sim = F.cosine_similarity(queries, docs)
            cosine_loss = 1 - cos_sim.mean()
            mse_loss = F.mse_loss(queries, docs)
            return self.cosine_weight * cosine_loss + (1 - self.cosine_weight) * mse_loss

    def _contrastive_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        In-batch contrastive loss (InfoNCE) with label smoothing.

        Uses other examples in the batch as negatives. This prevents embedding
        space collapse by teaching the model to distinguish correct pairs from
        incorrect ones.

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Contrastive loss value
        """
        # Normalize for cosine similarity
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix between all queries and all docs
        sim_matrix = torch.matmul(queries, docs.T) / self.temperature  # [batch, batch]

        # Diagonal contains correct pairs (query_i should match doc_i)
        labels = torch.arange(sim_matrix.size(0), device=sim_matrix.device)

        # Cross entropy with label smoothing to reduce overconfidence
        return F.cross_entropy(sim_matrix, labels, label_smoothing=self.label_smoothing)

    def _triplet_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Triplet Margin Loss with in-batch hard negative mining.

        For each query, selects the hardest negative (most similar non-matching doc)
        from the batch. Classic contrastive learning approach.

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Triplet loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix
        sim_matrix = torch.matmul(queries, docs.T)  # [batch, batch]

        # Positive similarities (diagonal)
        pos_sim = sim_matrix.diag()  # [batch]

        # Mask diagonal to find hard negatives
        batch_size = sim_matrix.size(0)
        mask = ~torch.eye(batch_size, dtype=torch.bool, device=sim_matrix.device)

        # Hard negative: highest similarity among non-matching pairs
        neg_sim = sim_matrix.masked_fill(~mask, float('-inf')).max(dim=1).values  # [batch]

        # Triplet margin loss: max(0, margin - pos + neg)
        margin = self.margin
        loss = F.relu(margin - pos_sim + neg_sim).mean()

        return loss

    def _mnrl_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Multiple Negatives Ranking Loss (MNRL).

        Popular in sentence-transformers. Uses symmetric cross-entropy:
        both query->doc and doc->query directions.

        This is more robust than standard InfoNCE as it considers both perspectives.

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            MNRL loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix scaled by temperature
        sim_matrix = torch.matmul(queries, docs.T) / self.temperature

        # Labels: diagonal is the correct match
        labels = torch.arange(sim_matrix.size(0), device=sim_matrix.device)

        # Symmetric loss: query->doc and doc->query
        loss_q2d = F.cross_entropy(sim_matrix, labels, label_smoothing=self.label_smoothing)
        loss_d2q = F.cross_entropy(sim_matrix.T, labels, label_smoothing=self.label_smoothing)

        return (loss_q2d + loss_d2q) / 2

    def _circle_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Circle Loss for unified learning from similarity pairs.

        Dynamically weights positive and negative pairs based on their current
        optimization state. Hard negatives receive more weight automatically.

        Reference: "Circle Loss: A Unified Perspective of Pair Similarity Optimization"
        https://arxiv.org/abs/2002.10857

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Circle loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix
        sim_matrix = torch.matmul(queries, docs.T)  # [batch, batch]

        batch_size = sim_matrix.size(0)

        # Optimal points for positive and negative pairs
        O_p = 1 + self.margin  # Target for positives
        O_n = -self.margin     # Target for negatives

        # Delta thresholds
        delta_p = 1 - self.margin
        delta_n = self.margin

        # Positive mask (diagonal) and negative mask (off-diagonal)
        pos_mask = torch.eye(batch_size, dtype=torch.bool, device=sim_matrix.device)
        neg_mask = ~pos_mask

        # Positive similarities
        pos_sim = sim_matrix[pos_mask]  # [batch]

        # Negative similarities - all off-diagonal elements
        neg_sim = sim_matrix[neg_mask].view(batch_size, batch_size - 1)  # [batch, batch-1]

        # Dynamic weights: harder pairs get more weight
        alpha_p = F.relu(O_p - pos_sim.detach())  # Weight for positives
        alpha_n = F.relu(neg_sim.detach() - O_n)  # Weight for negatives

        # Scaled logits
        logit_p = -alpha_p * (pos_sim - delta_p) / self.temperature
        logit_n = alpha_n * (neg_sim - delta_n) / self.temperature

        # Circle loss formulation
        loss = F.softplus(
            torch.logsumexp(logit_n, dim=1) + torch.logsumexp(logit_p.unsqueeze(1), dim=1)
        ).mean()

        return loss

    def _hard_negative_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Hard Negative Contrastive Loss.

        Focuses on the hardest negatives in the batch by selecting top-k most
        similar non-matching pairs. More aggressive than standard InfoNCE.

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Hard negative contrastive loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        batch_size = queries.size(0)

        # Similarity matrix
        sim_matrix = torch.matmul(queries, docs.T) / self.temperature

        # Positive similarities (diagonal)
        pos_sim = sim_matrix.diag().unsqueeze(1)  # [batch, 1]

        # Mask diagonal for negatives
        mask = ~torch.eye(batch_size, dtype=torch.bool, device=sim_matrix.device)
        neg_sim = sim_matrix.masked_fill(~mask, float('-inf'))

        # Select top-k hardest negatives (k = min(hard_neg_k, batch_size-1))
        k = min(self.hard_neg_k, batch_size - 1)
        hard_neg_sim, _ = neg_sim.topk(k, dim=1)  # [batch, k]

        # Combine positive and hard negatives for softmax
        logits = torch.cat([pos_sim, hard_neg_sim], dim=1)  # [batch, 1+k]

        # Labels: positive is always index 0
        labels = torch.zeros(batch_size, dtype=torch.long, device=sim_matrix.device)

        return F.cross_entropy(logits, labels, label_smoothing=self.label_smoothing)

    def _cosine_margin_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        Cosine Margin Loss (ArcFace/CosFace style).

        Adds an angular margin to the positive pairs, making the model learn
        more discriminative embeddings with better separation.

        Reference: "ArcFace: Additive Angular Margin Loss for Deep Face Recognition"
        https://arxiv.org/abs/1801.07698

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            Cosine margin loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix (cosine similarities)
        sim_matrix = torch.matmul(queries, docs.T)  # [batch, batch]

        batch_size = sim_matrix.size(0)

        # Apply margin to positive pairs (diagonal)
        # CosFace: cos(theta) - margin
        margin_penalty = torch.zeros_like(sim_matrix)
        margin_penalty.fill_diagonal_(self.margin)
        sim_matrix_with_margin = sim_matrix - margin_penalty

        # Scale by temperature (like ArcFace scale parameter s)
        sim_matrix_scaled = sim_matrix_with_margin / self.temperature

        # Labels: diagonal is the correct match
        labels = torch.arange(batch_size, device=sim_matrix.device)

        return F.cross_entropy(sim_matrix_scaled, labels, label_smoothing=self.label_smoothing)

    def _poly_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        PolyLoss: A Polynomial Expansion Perspective of Classification Loss.

        Modifies cross-entropy with polynomial coefficients that adjust the
        contribution of different probability levels. Can improve training dynamics.

        Reference: "PolyLoss: A Polynomial Expansion Perspective of Classification Loss Functions"
        https://arxiv.org/abs/2204.12511

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            PolyLoss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        # Similarity matrix
        sim_matrix = torch.matmul(queries, docs.T) / self.temperature

        batch_size = sim_matrix.size(0)
        labels = torch.arange(batch_size, device=sim_matrix.device)

        # Standard cross-entropy
        ce_loss = F.cross_entropy(sim_matrix, labels, reduction='none')

        # Get probabilities
        probs = F.softmax(sim_matrix, dim=1)

        # Probability of correct class
        pt = probs[torch.arange(batch_size, device=sim_matrix.device), labels]

        # PolyLoss = CE + epsilon * (1 - pt)
        # epsilon controls the polynomial adjustment (default 1.0)
        poly_loss = ce_loss + self.poly_epsilon * (1 - pt)

        return poly_loss.mean()

    def _ntxent_loss(self, queries: torch.Tensor, docs: torch.Tensor) -> torch.Tensor:
        """
        NT-Xent Loss (Normalized Temperature-scaled Cross Entropy).

        Used in SimCLR. Treats both query and doc as augmented views and uses
        all other samples as negatives for both directions.

        Reference: "A Simple Framework for Contrastive Learning of Visual Representations"
        https://arxiv.org/abs/2002.05709

        Args:
            queries: Transformed query embeddings [batch, dim]
            docs: Target document embeddings [batch, dim]

        Returns:
            NT-Xent loss value
        """
        queries = F.normalize(queries, p=2, dim=1)
        docs = F.normalize(docs, p=2, dim=1)

        batch_size = queries.size(0)

        # Concatenate queries and docs as "augmented views"
        # representations: [2*batch, dim]
        representations = torch.cat([queries, docs], dim=0)

        # Full similarity matrix [2*batch, 2*batch]
        sim_matrix = torch.matmul(representations, representations.T) / self.temperature

        # Create labels: positive pairs are (i, i+batch_size) and (i+batch_size, i)
        labels = torch.cat([
            torch.arange(batch_size, 2 * batch_size, device=sim_matrix.device),
            torch.arange(batch_size, device=sim_matrix.device)
        ])

        # Mask out self-similarity (diagonal)
        mask = ~torch.eye(2 * batch_size, dtype=torch.bool, device=sim_matrix.device)
        sim_matrix = sim_matrix.masked_fill(~mask, float('-inf'))

        return F.cross_entropy(sim_matrix, labels, label_smoothing=self.label_smoothing)

    def fit(
        self,
        data: EmbeddingDataset,
        verbose: bool = True
    ) -> "VeraAdapter":
        """
        Train the adapter on the embedding dataset.

        Args:
            data: EmbeddingDataset with question and answer embeddings
            verbose: Show training progress

        Returns:
            self for method chaining
        """
        # Get training data
        q_train, a_train = data.get_train_data()
        q_val, a_val = data.get_val_data()

        # Convert to tensors
        q_train_t = torch.FloatTensor(q_train).to(self.device)
        a_train_t = torch.FloatTensor(a_train).to(self.device)

        # Create dataloader
        train_dataset = TensorDataset(q_train_t, a_train_t)
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            drop_last=True if self.loss_type == "contrastive" else False  # Need full batches for contrastive
        )

        # Validation data
        has_val = q_val is not None
        if has_val:
            q_val_t = torch.FloatTensor(q_val).to(self.device)
            a_val_t = torch.FloatTensor(a_val).to(self.device)

        # Optimizer with weight decay
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )

        # Learning rate scheduler - reduce LR when loss plateaus
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=3
        )

        # Best model tracking (always enabled when validation data exists)
        # Combined metric: 0.25 * train_loss + 0.75 * val_loss
        best_combined_loss = float('inf')
        best_epoch = 0
        patience_counter = 0
        best_model_state = None

        if verbose:
            print(f"Training VERA Adapter")
            print(f"  - Architecture: {self.arch_type}")
            print(f"  - Parameters: {self.model.count_parameters():,}")
            print(f"  - Device: {self.device}")
            print(f"  - Training samples: {len(q_train)}")
            print(f"  - Loss type: {self.loss_type}")
            if self.loss_type != "cosine":
                print(f"  - Temperature: {self.temperature}")
                print(f"  - Label smoothing: {self.label_smoothing}")
            if self.loss_type in ["triplet", "circle", "cosine_margin"]:
                print(f"  - Margin: {self.margin}")
            if self.loss_type == "hard_negative":
                print(f"  - Hard negatives k: {self.hard_neg_k}")
            if self.loss_type == "poly":
                print(f"  - Poly epsilon: {self.poly_epsilon}")
            print(f"  - Weight decay: {self.weight_decay}")
            if self.early_stopping_patience > 0:
                print(f"  - Early stopping patience: {self.early_stopping_patience}")
            if has_val:
                print(f"  - Validation samples: {len(q_val)}")
                print(f"  - Best model: Will restore best val_loss model")
            print()

        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            num_batches = 0

            iterator = train_loader
            if verbose:
                iterator = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{self.epochs}")

            for q_batch, a_batch in iterator:
                optimizer.zero_grad()

                # Forward pass
                q_transformed = self.model(q_batch)

                # Compute loss based on loss_type
                loss = self._compute_loss(q_transformed, a_batch)

                # Backward pass
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                num_batches += 1

                if verbose:
                    iterator.set_postfix({"loss": loss.item()})

            avg_train_loss = total_loss / num_batches

            # Validation
            val_loss = None
            if has_val:
                self.model.eval()
                with torch.no_grad():
                    q_val_transformed = self.model(q_val_t)
                    val_loss = self._compute_loss(q_val_transformed, a_val_t).item()
                self.model.train()

            # Update learning rate based on loss
            scheduler.step(val_loss if val_loss is not None else avg_train_loss)

            self.train_history.append({
                "epoch": epoch + 1,
                "train_loss": avg_train_loss,
                "val_loss": val_loss
            })

            if verbose:
                msg = f"Epoch {epoch + 1}: train_loss={avg_train_loss:.4f}"
                if val_loss is not None:
                    msg += f", val_loss={val_loss:.4f}"
                print(msg)

            # Best model tracking (always enabled when validation data exists)
            # Combined metric: 0.25 * train_loss + 0.75 * val_loss
            if has_val:
                combined_loss = 0.25 * avg_train_loss + 0.75 * val_loss
                if combined_loss < best_combined_loss:
                    best_combined_loss = combined_loss
                    best_epoch = epoch + 1
                    patience_counter = 0
                    # Save best model state
                    best_model_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                else:
                    patience_counter += 1
                    # Early stopping (only if patience is set)
                    if self.early_stopping_patience > 0 and patience_counter >= self.early_stopping_patience:
                        if verbose:
                            print(f"\nEarly stopping at epoch {epoch + 1} (no improvement for {self.early_stopping_patience} epochs)")
                        break

        self.is_trained = True
        self.model.eval()

        # Always restore best model when validation data exists
        if has_val and best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            if verbose:
                print(f"\nRestored best model from epoch {best_epoch} (combined_loss={best_combined_loss:.4f})")

        if verbose:
            print("\nTraining complete!")

        return self

    def transform_vect(
        self,
        vectors: Union[np.ndarray, List[List[float]]],
        batch_size: int = 256
    ) -> np.ndarray:
        """
        Transform embedding vectors through the adapter.

        Args:
            vectors: Embeddings of shape (n, embedding_dim)
            batch_size: Batch size for processing (to avoid OOM with large inputs)

        Returns:
            Transformed embeddings of shape (n, embedding_dim)
        """
        if not self.is_trained:
            raise RuntimeError("Adapter must be trained before transform. Call fit() first.")

        # Convert to tensor
        if isinstance(vectors, list):
            vectors = np.array(vectors)

        n = len(vectors)
        self.model.eval()

        # Process in batches to avoid OOM
        if n <= batch_size:
            x = torch.FloatTensor(vectors).to(self.device)
            with torch.no_grad():
                transformed = self.model(x)
            return transformed.cpu().numpy()

        # Batch processing
        results = []
        for i in range(0, n, batch_size):
            batch = vectors[i:i + batch_size]
            x = torch.FloatTensor(batch).to(self.device)
            with torch.no_grad():
                transformed = self.model(x)
            results.append(transformed.cpu().numpy())

        return np.vstack(results)

    def transform_text(
        self,
        texts: List[str],
        model_emb
    ) -> np.ndarray:
        """
        Embed texts and transform through the adapter.

        Args:
            texts: List of strings to embed and transform
            model_emb: Embedding model to use

        Returns:
            Transformed embeddings of shape (n, embedding_dim)
        """
        # Get embeddings
        embeddings = model_emb.embed(texts)

        # Transform
        return self.transform_vect(embeddings)

    def save(self, path: str):
        """Save the adapter model to a file"""
        torch.save({
            "model_state": self.model.state_dict(),
            "config": {
                "embedding_dim": self.embedding_dim,
                "bottleneck_dim": self.bottleneck_dim,
                "num_blocks": self.num_blocks,
                "dropout": self.dropout,
                "cosine_weight": self.cosine_weight,
                "use_improved_arch": self.use_improved_arch,
                "use_bottleneck": self.use_bottleneck,
                "use_conv": self.use_conv,
                "kernel_size": self.kernel_size,
                "num_channels": self.num_channels,
                "loss_type": self.loss_type,
                "temperature": self.temperature,
                "label_smoothing": self.label_smoothing,
                "weight_decay": self.weight_decay,
                "arch_type": self.arch_type,
                "hidden_dim": self.hidden_dim,
                "initial_scale": self.initial_scale,
                "margin": self.margin,
                "hard_neg_k": self.hard_neg_k,
                "poly_epsilon": self.poly_epsilon
            },
            "train_history": self.train_history
        }, path)

    @classmethod
    def load(cls, path: str, device: Optional[str] = None) -> "VeraAdapter":
        """Load an adapter model from a file"""
        checkpoint = torch.load(path, map_location=device or "cpu", weights_only=False)

        config = checkpoint["config"]
        adapter = cls(
            embedding_dim=config["embedding_dim"],
            bottleneck_dim=config["bottleneck_dim"],
            num_blocks=config["num_blocks"],
            dropout=config["dropout"],
            cosine_weight=config.get("cosine_weight", 1.0),
            use_improved_arch=config.get("use_improved_arch", False),
            use_bottleneck=config.get("use_bottleneck", True),
            use_conv=config.get("use_conv", False),
            kernel_size=config.get("kernel_size", 3),
            num_channels=config.get("num_channels", 64),
            loss_type=config.get("loss_type", "cosine"),
            temperature=config.get("temperature", 0.1),
            label_smoothing=config.get("label_smoothing", 0.1),
            weight_decay=config.get("weight_decay", 0.01),
            arch_type=config.get("arch_type", "resnet"),
            hidden_dim=config.get("hidden_dim", 512),
            initial_scale=config.get("initial_scale", 0.5),
            margin=config.get("margin", 0.2),
            hard_neg_k=config.get("hard_neg_k", 5),
            poly_epsilon=config.get("poly_epsilon", 1.0),
            device=device
        )

        adapter.model.load_state_dict(checkpoint["model_state"])
        adapter.train_history = checkpoint.get("train_history", [])
        adapter.is_trained = True
        adapter.model.eval()

        return adapter


def adapter(
    embedding_dim: int = 1536,
    bottleneck_dim: int = 256,
    num_blocks: int = 5,
    epochs: int = 10,
    batch_size: int = 32,
    dropout: float = 0.1,
    learning_rate: float = 1e-4,
    cosine_weight: float = 1.0,
    use_improved_arch: bool = False,
    use_bottleneck: bool = True,
    use_conv: bool = False,
    kernel_size: int = 3,
    num_channels: int = 64,
    loss_type: str = "cosine",
    temperature: float = 0.1,
    label_smoothing: float = 0.1,
    weight_decay: float = 0.01,
    early_stopping_patience: int = 0,
    arch_type: str = "resnet",
    hidden_dim: int = 512,
    initial_scale: float = 0.5,
    margin: float = 0.2,
    hard_neg_k: int = 5,
    poly_epsilon: float = 1.0,
    device: Optional[str] = None
) -> VeraAdapter:
    """
    Create a VERA adapter.

    Factory function that matches the API shown in test.py.

    Args:
        arch_type: Architecture type. Options:
                  - "resnet": Original ResNet with residual blocks (most capacity, may overfit)
                  - "resnet2": ResNet that always adds to original input, with tanh and learnable scale
                  - "linear": Simple linear projection (~2.3M params, simplest)
                  - "adapter": PEFT-style adapter (~200K params) [RECOMMENDED for most cases]
                  - "mlp": 2-layer MLP (~1.5M params, middle ground)
        use_conv: Use Conv1d instead of Linear layers in ResNet. Captures local patterns.
        kernel_size: Kernel size for Conv1d. Default 3.
        num_channels: Number of channels for ConvFullDimBlock. Default 64.
        loss_type: Loss function to use. Options:
                  - "cosine": Original cosine + MSE loss
                  - "contrastive": InfoNCE in-batch contrastive (recommended, prevents collapse)
                  - "triplet": Triplet margin loss with in-batch hard negative mining
                  - "mnrl": Multiple Negatives Ranking Loss (symmetric, robust)
                  - "circle": Circle Loss (dynamic weighting, state-of-the-art)
                  - "hard_negative": Hard negative contrastive (focuses on top-k hardest)
                  - "cosine_margin": CosFace-style angular margin loss
                  - "poly": PolyLoss (polynomial expansion of CE)
                  - "ntxent": NT-Xent loss (SimCLR style, bidirectional)
        temperature: Temperature for contrastive losses. Higher = softer predictions.
        label_smoothing: Smoothing factor for contrastive losses. Reduces overconfidence.
        weight_decay: L2 regularization strength.
        early_stopping_patience: Stop if val_loss doesn't improve for N epochs. 0 = disabled.
        hidden_dim: Hidden dimension for MLP architecture.
        initial_scale: Initial value for learnable scale in resnet2 (default 0.5).
        margin: Margin for triplet, circle, and cosine_margin losses (default 0.2).
        hard_neg_k: Number of hard negatives for hard_negative loss (default 5).
        poly_epsilon: Epsilon coefficient for PolyLoss (default 1.0).
    """
    return VeraAdapter(
        embedding_dim=embedding_dim,
        bottleneck_dim=bottleneck_dim,
        num_blocks=num_blocks,
        epochs=epochs,
        batch_size=batch_size,
        dropout=dropout,
        learning_rate=learning_rate,
        cosine_weight=cosine_weight,
        use_improved_arch=use_improved_arch,
        use_bottleneck=use_bottleneck,
        use_conv=use_conv,
        kernel_size=kernel_size,
        num_channels=num_channels,
        loss_type=loss_type,
        temperature=temperature,
        label_smoothing=label_smoothing,
        weight_decay=weight_decay,
        early_stopping_patience=early_stopping_patience,
        arch_type=arch_type,
        hidden_dim=hidden_dim,
        initial_scale=initial_scale,
        margin=margin,
        hard_neg_k=hard_neg_k,
        poly_epsilon=poly_epsilon,
        device=device
    )


def check_embedding_collapse(
    original_embeddings: np.ndarray,
    transformed_embeddings: np.ndarray,
    sample_size: int = 1000
) -> dict:
    """
    Check if the adapter is causing embedding space collapse.

    Compares the average pairwise distance before and after transformation.
    If the distance decreases significantly, embeddings are collapsing.

    Args:
        original_embeddings: Original embeddings before transformation
        transformed_embeddings: Embeddings after passing through the adapter
        sample_size: Number of samples to use for distance calculation

    Returns:
        Dictionary with collapse metrics
    """
    # Sample if needed
    n = len(original_embeddings)
    if n > sample_size:
        indices = np.random.choice(n, sample_size, replace=False)
        original_sample = original_embeddings[indices]
        transformed_sample = transformed_embeddings[indices]
    else:
        original_sample = original_embeddings
        transformed_sample = transformed_embeddings

    # Convert to torch
    orig_t = torch.FloatTensor(original_sample)
    trans_t = torch.FloatTensor(transformed_sample)

    # Normalize for cosine distance
    orig_norm = F.normalize(orig_t, p=2, dim=1)
    trans_norm = F.normalize(trans_t, p=2, dim=1)

    # Compute pairwise cosine distances (1 - similarity)
    orig_sim = torch.matmul(orig_norm, orig_norm.T)
    trans_sim = torch.matmul(trans_norm, trans_norm.T)

    # Mask diagonal (self-similarity = 1)
    mask = ~torch.eye(orig_sim.size(0), dtype=torch.bool)

    orig_dist = (1 - orig_sim[mask]).mean().item()
    trans_dist = (1 - trans_sim[mask]).mean().item()

    # Collapse ratio: if < 1, embeddings are getting closer together
    collapse_ratio = trans_dist / orig_dist if orig_dist > 0 else 0

    return {
        "original_avg_distance": orig_dist,
        "transformed_avg_distance": trans_dist,
        "collapse_ratio": collapse_ratio,
        "is_collapsing": collapse_ratio < 0.8,  # More than 20% reduction = collapse
        "message": (
            "WARNING: Embeddings are collapsing!" if collapse_ratio < 0.8
            else "OK: Embedding space is preserved."
        )
    }
