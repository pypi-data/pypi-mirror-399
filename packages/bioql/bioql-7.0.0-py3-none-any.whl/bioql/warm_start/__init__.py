# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Warm Start Module for VQE Parameter Initialization

This module implements Flow-VQE (npj Quantum Information 2025) for warm starting
VQE calculations using conditional normalizing flows trained on molecular families.

Key Features:
- Generative flow-based parameter interpolation
- Parameter database with molecular similarity search
- 50-80% reduction in VQE iterations
- Automatic parameter transfer for similar molecules

Components:
- flow_vqe: Conditional normalizing flows for parameter generation
- parameter_database: SQLite-based parameter storage with molecular descriptors
- similarity_matching: RDKit-based similarity search and interpolation

References:
- Flow-VQE: https://github.com/olsson-group/Flow-VQE
- npj Quantum Information (2025): "Warm-starting quantum optimization via normalizing flows"
"""

from .flow_vqe import FlowVQE, ConditionalNormalizingFlow
from .parameter_database import ParameterDatabase, MolecularDescriptor
from .similarity_matching import SimilarityMatcher, interpolate_parameters

__all__ = [
    "FlowVQE",
    "ConditionalNormalizingFlow",
    "ParameterDatabase",
    "MolecularDescriptor",
    "SimilarityMatcher",
    "interpolate_parameters",
]

__version__ = "1.0.0"
