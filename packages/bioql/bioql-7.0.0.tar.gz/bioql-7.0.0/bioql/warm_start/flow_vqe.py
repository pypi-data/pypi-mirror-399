# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Flow-VQE: Warm Starting VQE with Conditional Normalizing Flows

Implements the Flow-VQE method from npj Quantum Information (2025) for generating
optimal initial VQE parameters using conditional normalizing flows trained on
molecular families.

Key Concepts:
- Normalizing flows learn the distribution p(θ|molecule) of optimal parameters
- Conditional on molecular features (SMILES, fingerprints, descriptors)
- Generates parameters for new molecules by sampling from learned distribution
- Dramatically reduces VQE iterations (50-80% reduction)

Architecture:
- Coupling layers with affine transformations
- Conditional on molecular Morgan fingerprints
- Trained on families: alkanes, aromatics, peptides
- Temperature-based sampling for exploration

References:
- Olsson et al., "Flow-based generative models for Markov chain Monte Carlo in lattice field theory"
- Blunt et al., "Perspective on the Current State-of-the-Art of Quantum Computing"
- Flow-VQE GitHub: https://github.com/olsson-group/Flow-VQE
"""

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.distributions import Normal

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class FlowVQEConfig:
    """Configuration for Flow-VQE model."""

    num_coupling_layers: int = 8
    hidden_dim: int = 128
    num_hidden_layers: int = 3
    fingerprint_dim: int = 2048  # Morgan fingerprint dimension
    learning_rate: float = 1e-3
    batch_size: int = 32
    num_epochs: int = 100
    temperature: float = 1.0  # Sampling temperature
    activation: str = "relu"


class AffineCouplingLayer(nn.Module):
    """
    Affine coupling layer for normalizing flow.

    Implements x_out = x_in * exp(s(x_in, c)) + t(x_in, c)
    where s and t are neural networks conditioned on molecular features c.
    """

    def __init__(
        self, input_dim: int, condition_dim: int, hidden_dim: int = 128, num_layers: int = 3
    ):
        """
        Initialize affine coupling layer.

        Args:
            input_dim: Dimension of input parameters
            condition_dim: Dimension of conditioning information (fingerprint)
            hidden_dim: Hidden layer dimension
            num_layers: Number of hidden layers
        """
        super().__init__()
        self.input_dim = input_dim
        self.split_dim = input_dim // 2

        # Scale network s(x, c)
        layers_s = []
        layers_s.append(nn.Linear(self.split_dim + condition_dim, hidden_dim))
        layers_s.append(nn.ReLU())
        for _ in range(num_layers - 1):
            layers_s.append(nn.Linear(hidden_dim, hidden_dim))
            layers_s.append(nn.ReLU())
        layers_s.append(nn.Linear(hidden_dim, input_dim - self.split_dim))
        self.scale_net = nn.Sequential(*layers_s)

        # Translation network t(x, c)
        layers_t = []
        layers_t.append(nn.Linear(self.split_dim + condition_dim, hidden_dim))
        layers_t.append(nn.ReLU())
        for _ in range(num_layers - 1):
            layers_t.append(nn.Linear(hidden_dim, hidden_dim))
            layers_t.append(nn.ReLU())
        layers_t.append(nn.Linear(hidden_dim, input_dim - self.split_dim))
        self.translation_net = nn.Sequential(*layers_t)

    def forward(self, x: torch.Tensor, condition: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass (data to noise).

        Args:
            x: Input parameters [batch, input_dim]
            condition: Molecular fingerprint [batch, condition_dim]

        Returns:
            z: Latent variables
            log_det: Log determinant of Jacobian
        """
        x1, x2 = torch.split(x, [self.split_dim, x.shape[1] - self.split_dim], dim=1)

        # Concatenate x1 with condition
        x1_cond = torch.cat([x1, condition], dim=1)

        # Compute affine transformation for x2
        s = self.scale_net(x1_cond)
        t = self.translation_net(x1_cond)

        # Apply transformation: z2 = (x2 - t) * exp(-s)
        z2 = (x2 - t) * torch.exp(-s)
        z = torch.cat([x1, z2], dim=1)

        # Log determinant of Jacobian
        log_det = -torch.sum(s, dim=1)

        return z, log_det

    def inverse(self, z: torch.Tensor, condition: torch.Tensor) -> torch.Tensor:
        """
        Inverse pass (noise to data) for sampling.

        Args:
            z: Latent variables [batch, input_dim]
            condition: Molecular fingerprint [batch, condition_dim]

        Returns:
            x: Generated parameters
        """
        z1, z2 = torch.split(z, [self.split_dim, z.shape[1] - self.split_dim], dim=1)

        # Concatenate z1 with condition
        z1_cond = torch.cat([z1, condition], dim=1)

        # Compute affine transformation
        s = self.scale_net(z1_cond)
        t = self.translation_net(z1_cond)

        # Apply inverse: x2 = z2 * exp(s) + t
        x2 = z2 * torch.exp(s) + t
        x = torch.cat([z1, x2], dim=1)

        return x


class ConditionalNormalizingFlow(nn.Module):
    """
    Conditional normalizing flow for VQE parameter generation.

    Architecture:
    - Multiple affine coupling layers
    - Conditioned on molecular Morgan fingerprints
    - Learns distribution p(θ|molecule)
    - Enables efficient sampling of optimal parameters
    """

    def __init__(self, config: FlowVQEConfig, param_dim: int):
        """
        Initialize conditional normalizing flow.

        Args:
            config: Flow-VQE configuration
            param_dim: Dimension of VQE parameter space
        """
        super().__init__()
        self.config = config
        self.param_dim = param_dim

        # Stack of coupling layers
        self.coupling_layers = nn.ModuleList()
        for i in range(config.num_coupling_layers):
            layer = AffineCouplingLayer(
                input_dim=param_dim,
                condition_dim=config.fingerprint_dim,
                hidden_dim=config.hidden_dim,
                num_layers=config.num_hidden_layers,
            )
            self.coupling_layers.append(layer)

        # Base distribution (standard normal)
        self.base_dist = Normal(0, 1)

    def forward(
        self, parameters: torch.Tensor, fingerprint: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass: parameters -> latent.

        Args:
            parameters: VQE parameters [batch, param_dim]
            fingerprint: Molecular fingerprint [batch, fingerprint_dim]

        Returns:
            z: Latent variables
            log_prob: Log probability
        """
        z = parameters
        log_det_sum = 0.0

        # Pass through coupling layers
        for layer in self.coupling_layers:
            z, log_det = layer(z, fingerprint)
            log_det_sum += log_det

        # Compute log probability under base distribution
        log_prob_base = torch.sum(self.base_dist.log_prob(z), dim=1)
        log_prob = log_prob_base + log_det_sum

        return z, log_prob

    def inverse(self, fingerprint: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        """
        Inverse pass: sample parameters given molecular fingerprint.

        Args:
            fingerprint: Molecular fingerprint [batch, fingerprint_dim]
            temperature: Sampling temperature (higher = more exploration)

        Returns:
            parameters: Generated VQE parameters [batch, param_dim]
        """
        batch_size = fingerprint.shape[0]

        # Sample from base distribution with temperature
        z = torch.randn(batch_size, self.param_dim) * temperature

        # Pass through coupling layers in reverse
        for layer in reversed(self.coupling_layers):
            z = layer.inverse(z, fingerprint)

        return z

    def sample(
        self, smiles: str, num_samples: int = 1, temperature: float = 1.0
    ) -> np.ndarray:
        """
        Sample VQE parameters for a molecule.

        Args:
            smiles: SMILES string of molecule
            num_samples: Number of parameter sets to sample
            temperature: Sampling temperature

        Returns:
            parameters: Sampled parameters [num_samples, param_dim]
        """
        # Compute molecular fingerprint
        fingerprint = compute_morgan_fingerprint(smiles, nbits=self.config.fingerprint_dim)
        fingerprint_tensor = (
            torch.tensor(fingerprint, dtype=torch.float32).unsqueeze(0).repeat(num_samples, 1)
        )

        # Sample parameters
        with torch.no_grad():
            params = self.inverse(fingerprint_tensor, temperature=temperature)

        return params.numpy()


class FlowVQE:
    """
    Flow-VQE: Warm starting VQE with conditional normalizing flows.

    This class manages:
    - Training flows on molecular families
    - Generating initial parameters for new molecules
    - Tracking performance improvements

    Workflow:
    1. Train on molecular family (e.g., small peptides)
    2. For new molecule, generate parameters from flow
    3. Use as initial guess for VQE optimization
    4. Achieve 50-80% reduction in iterations
    """

    def __init__(self, config: Optional[FlowVQEConfig] = None):
        """
        Initialize Flow-VQE.

        Args:
            config: Flow-VQE configuration (uses defaults if None)
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for Flow-VQE. Install: pip install torch")
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for Flow-VQE. Install: pip install rdkit")

        self.config = config or FlowVQEConfig()
        self.flow_model: Optional[ConditionalNormalizingFlow] = None
        self.param_dim: Optional[int] = None
        self.training_history: List[float] = []

    def train(
        self,
        training_data: List[Tuple[str, np.ndarray]],
        validation_split: float = 0.2,
        verbose: bool = True,
    ) -> Dict[str, List[float]]:
        """
        Train conditional normalizing flow on molecular family.

        Args:
            training_data: List of (SMILES, optimal_parameters) tuples
            validation_split: Fraction of data for validation
            verbose: Print training progress

        Returns:
            Training history dict with losses

        Example:
            >>> training_data = [
            ...     ("CCO", np.array([0.5, 1.2, 0.3, 0.8])),
            ...     ("CCCO", np.array([0.6, 1.1, 0.4, 0.7])),
            ... ]
            >>> flow_vqe = FlowVQE()
            >>> history = flow_vqe.train(training_data)
        """
        if len(training_data) == 0:
            raise ValueError("Training data cannot be empty")

        # Determine parameter dimension
        self.param_dim = len(training_data[0][1])
        logger.info(f"Training Flow-VQE on {len(training_data)} molecules, {self.param_dim} parameters")

        # Initialize flow model
        self.flow_model = ConditionalNormalizingFlow(self.config, self.param_dim)
        optimizer = optim.Adam(self.flow_model.parameters(), lr=self.config.learning_rate)

        # Prepare training data
        smiles_list = [item[0] for item in training_data]
        params_list = [item[1] for item in training_data]

        # Compute fingerprints
        fingerprints = np.array(
            [
                compute_morgan_fingerprint(smiles, nbits=self.config.fingerprint_dim)
                for smiles in smiles_list
            ]
        )
        parameters = np.array(params_list)

        # Split into train/validation
        num_train = int(len(training_data) * (1 - validation_split))
        indices = np.random.permutation(len(training_data))
        train_indices = indices[:num_train]
        val_indices = indices[num_train:]

        train_fingerprints = torch.tensor(fingerprints[train_indices], dtype=torch.float32)
        train_parameters = torch.tensor(parameters[train_indices], dtype=torch.float32)
        val_fingerprints = torch.tensor(fingerprints[val_indices], dtype=torch.float32)
        val_parameters = torch.tensor(parameters[val_indices], dtype=torch.float32)

        # Training loop
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(self.config.num_epochs):
            # Training
            self.flow_model.train()
            optimizer.zero_grad()

            # Forward pass
            _, log_prob = self.flow_model(train_parameters, train_fingerprints)

            # Negative log likelihood loss
            loss = -torch.mean(log_prob)

            # Backward pass
            loss.backward()
            optimizer.step()

            history["train_loss"].append(loss.item())

            # Validation
            self.flow_model.eval()
            with torch.no_grad():
                _, val_log_prob = self.flow_model(val_parameters, val_fingerprints)
                val_loss = -torch.mean(val_log_prob)
                history["val_loss"].append(val_loss.item())

            if verbose and (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch+1}/{self.config.num_epochs}: "
                    f"Train Loss = {loss.item():.4f}, Val Loss = {val_loss.item():.4f}"
                )

        self.training_history = history["train_loss"]
        logger.success(f"Flow-VQE training complete. Final loss: {history['train_loss'][-1]:.4f}")

        return history

    def generate_initial_parameters(
        self, smiles: str, num_samples: int = 5, temperature: float = 0.8
    ) -> np.ndarray:
        """
        Generate initial VQE parameters for a molecule.

        Args:
            smiles: SMILES string of molecule
            num_samples: Number of candidate parameter sets
            temperature: Sampling temperature (0.5-1.5 range)

        Returns:
            Best parameter set [param_dim]

        Example:
            >>> flow_vqe = FlowVQE()
            >>> # ... train flow_vqe ...
            >>> params = flow_vqe.generate_initial_parameters("CC(C)O", num_samples=10)
            >>> # Use params as initial guess for VQE
        """
        if self.flow_model is None:
            raise ValueError("Flow model not trained. Call train() first.")

        logger.info(f"Generating initial parameters for {smiles} (sampling {num_samples} candidates)")

        # Sample multiple parameter sets
        params_candidates = self.flow_model.sample(smiles, num_samples=num_samples, temperature=temperature)

        # Return best candidate (could use heuristic or ensemble)
        # Here we use the mean of samples for stability
        best_params = np.mean(params_candidates, axis=0)

        return best_params

    def save(self, path: str):
        """Save trained flow model to disk."""
        if self.flow_model is None:
            raise ValueError("No model to save")

        save_dict = {
            "config": self.config.__dict__,
            "param_dim": self.param_dim,
            "model_state_dict": self.flow_model.state_dict(),
            "training_history": self.training_history,
        }

        torch.save(save_dict, path)
        logger.info(f"Flow-VQE model saved to {path}")

    def load(self, path: str):
        """Load trained flow model from disk."""
        checkpoint = torch.load(path)

        # Restore configuration
        self.config = FlowVQEConfig(**checkpoint["config"])
        self.param_dim = checkpoint["param_dim"]

        # Restore model
        self.flow_model = ConditionalNormalizingFlow(self.config, self.param_dim)
        self.flow_model.load_state_dict(checkpoint["model_state_dict"])
        self.training_history = checkpoint["training_history"]

        logger.info(f"Flow-VQE model loaded from {path}")


def compute_morgan_fingerprint(smiles: str, radius: int = 2, nbits: int = 2048) -> np.ndarray:
    """
    Compute Morgan (circular) fingerprint for a molecule.

    Args:
        smiles: SMILES string
        radius: Fingerprint radius
        nbits: Number of bits in fingerprint

    Returns:
        Binary fingerprint vector
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
    return np.array(fp)


# Example usage
if __name__ == "__main__":
    print("Flow-VQE Example: Training on alkane family")
    print("=" * 80)

    # Simulate training data: (SMILES, optimal_parameters)
    # In practice, these would come from converged VQE runs
    training_molecules = [
        ("C", np.array([0.1, 0.5, 0.3, 0.7])),  # Methane
        ("CC", np.array([0.2, 0.6, 0.4, 0.8])),  # Ethane
        ("CCC", np.array([0.3, 0.7, 0.5, 0.9])),  # Propane
        ("CCCC", np.array([0.4, 0.8, 0.6, 1.0])),  # Butane
        ("CC(C)C", np.array([0.35, 0.75, 0.55, 0.95])),  # Isobutane
    ]

    # Initialize and train Flow-VQE
    config = FlowVQEConfig(num_epochs=50, batch_size=4)
    flow_vqe = FlowVQE(config)

    if TORCH_AVAILABLE and RDKIT_AVAILABLE:
        history = flow_vqe.train(training_molecules, verbose=True)

        # Generate parameters for new molecule
        new_molecule = "CCCCC"  # Pentane
        initial_params = flow_vqe.generate_initial_parameters(new_molecule, num_samples=10)

        print(f"\nGenerated initial parameters for {new_molecule}:")
        print(f"  Parameters: {initial_params}")
        print(f"\nExpected 50-80% reduction in VQE iterations when using these parameters")

        # Save model
        # flow_vqe.save("flow_vqe_alkanes.pt")
    else:
        print("PyTorch and RDKit required for Flow-VQE")
