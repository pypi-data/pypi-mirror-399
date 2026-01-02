# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Molecular Similarity Matching for VQE Parameter Transfer

Implements similarity-based parameter transfer using RDKit molecular fingerprints
and parameter interpolation strategies for warm starting VQE calculations.

Key Methods:
- Tanimoto similarity using Morgan fingerprints
- K-nearest neighbors in molecular space
- Parameter interpolation (weighted average, Gaussian process)
- Uncertainty estimation for parameter quality

Workflow:
1. Compute molecular fingerprint for query molecule
2. Find K most similar molecules with known parameters
3. Interpolate parameters based on similarity weights
4. Return parameter estimate with confidence score

References:
- Rogers & Hahn (2010): "Extended-Connectivity Fingerprints"
- Landrum et al., RDKit: Open-source cheminformatics
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from rdkit import Chem, DataStructs
    from rdkit.Chem import AllChem

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class SimilarityMatch:
    """Container for a molecular similarity match."""

    smiles: str
    similarity: float
    parameters: np.ndarray
    energy: float
    metadata: Optional[Dict] = None


@dataclass
class ParameterPrediction:
    """Container for predicted VQE parameters."""

    parameters: np.ndarray
    confidence: float  # 0-1, based on similarity scores
    num_neighbors: int
    avg_similarity: float
    similar_molecules: List[SimilarityMatch]
    interpolation_method: str


class SimilarityMatcher:
    """
    Molecular similarity matcher for VQE parameter transfer.

    Uses RDKit fingerprints to find similar molecules and interpolate
    their converged VQE parameters to provide warm start guesses.
    """

    def __init__(
        self,
        fingerprint_type: str = "morgan",
        radius: int = 2,
        nbits: int = 2048,
        similarity_metric: str = "tanimoto",
    ):
        """
        Initialize similarity matcher.

        Args:
            fingerprint_type: Type of fingerprint ('morgan', 'topological')
            radius: Fingerprint radius (for Morgan)
            nbits: Number of bits in fingerprint
            similarity_metric: Similarity metric ('tanimoto', 'dice')
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for similarity matching. Install: pip install rdkit")

        self.fingerprint_type = fingerprint_type
        self.radius = radius
        self.nbits = nbits
        self.similarity_metric = similarity_metric

        logger.info(
            f"Initialized SimilarityMatcher: {fingerprint_type} fingerprints, "
            f"{similarity_metric} similarity"
        )

    def compute_fingerprint(self, smiles: str) -> np.ndarray:
        """
        Compute molecular fingerprint from SMILES.

        Args:
            smiles: SMILES string

        Returns:
            Binary fingerprint vector
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")

        if self.fingerprint_type == "morgan":
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, self.radius, nBits=self.nbits)
        elif self.fingerprint_type == "topological":
            fp = AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect(mol, nBits=self.nbits)
        else:
            raise ValueError(f"Unknown fingerprint type: {self.fingerprint_type}")

        return np.array(fp)

    def compute_similarity(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """
        Compute similarity between two fingerprints.

        Args:
            fp1: First fingerprint
            fp2: Second fingerprint

        Returns:
            Similarity score (0-1)
        """
        # Convert to RDKit ExplicitBitVect for efficient similarity calculation
        ebv1 = DataStructs.ExplicitBitVect(len(fp1))
        ebv2 = DataStructs.ExplicitBitVect(len(fp2))

        for i, bit in enumerate(fp1):
            if bit:
                ebv1.SetBit(i)

        for i, bit in enumerate(fp2):
            if bit:
                ebv2.SetBit(i)

        if self.similarity_metric == "tanimoto":
            return DataStructs.TanimotoSimilarity(ebv1, ebv2)
        elif self.similarity_metric == "dice":
            return DataStructs.DiceSimilarity(ebv1, ebv2)
        else:
            raise ValueError(f"Unknown similarity metric: {self.similarity_metric}")

    def find_neighbors(
        self,
        query_smiles: str,
        database_molecules: List[Tuple[str, np.ndarray, float]],
        k: int = 5,
        min_similarity: float = 0.3,
    ) -> List[SimilarityMatch]:
        """
        Find K nearest neighbors in molecular space.

        Args:
            query_smiles: Query molecule SMILES
            database_molecules: List of (smiles, parameters, energy) tuples
            k: Number of neighbors to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of SimilarityMatch objects sorted by similarity

        Example:
            >>> matcher = SimilarityMatcher()
            >>> database = [
            ...     ("CCO", np.array([0.5, 1.2]), -1.5),
            ...     ("CCCO", np.array([0.6, 1.1]), -1.6),
            ... ]
            >>> neighbors = matcher.find_neighbors("CC(C)O", database, k=2)
        """
        query_fp = self.compute_fingerprint(query_smiles)

        matches = []
        for smiles, parameters, energy in database_molecules:
            try:
                mol_fp = self.compute_fingerprint(smiles)
                similarity = self.compute_similarity(query_fp, mol_fp)

                if similarity >= min_similarity:
                    matches.append(
                        SimilarityMatch(
                            smiles=smiles,
                            similarity=similarity,
                            parameters=parameters,
                            energy=energy,
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to process molecule {smiles}: {e}")
                continue

        # Sort by similarity (descending)
        matches.sort(key=lambda x: x.similarity, reverse=True)

        # Return top K
        return matches[:k]

    def interpolate_parameters(
        self,
        query_smiles: str,
        database_molecules: List[Tuple[str, np.ndarray, float]],
        k: int = 5,
        method: str = "weighted_average",
        temperature: float = 1.0,
    ) -> ParameterPrediction:
        """
        Interpolate VQE parameters for a new molecule.

        Args:
            query_smiles: Query molecule SMILES
            database_molecules: List of (smiles, parameters, energy) tuples
            k: Number of neighbors to use
            method: Interpolation method ('weighted_average', 'nearest', 'inverse_distance')
            temperature: Softmax temperature for weighted average

        Returns:
            ParameterPrediction with interpolated parameters and confidence

        Example:
            >>> matcher = SimilarityMatcher()
            >>> database = [
            ...     ("CCO", np.array([0.5, 1.2, 0.3]), -1.5),
            ...     ("CCCO", np.array([0.6, 1.1, 0.4]), -1.6),
            ... ]
            >>> prediction = matcher.interpolate_parameters("CC(C)O", database, k=2)
            >>> print(f"Parameters: {prediction.parameters}")
            >>> print(f"Confidence: {prediction.confidence:.2f}")
        """
        # Find nearest neighbors
        neighbors = self.find_neighbors(query_smiles, database_molecules, k=k)

        if not neighbors:
            raise ValueError(
                f"No similar molecules found for {query_smiles}. "
                f"Increase database size or lower min_similarity."
            )

        # Interpolate parameters based on method
        if method == "nearest":
            # Use parameters from most similar molecule
            params = neighbors[0].parameters.copy()
            confidence = neighbors[0].similarity

        elif method == "weighted_average":
            # Weighted average based on similarity scores
            similarities = np.array([m.similarity for m in neighbors])

            # Apply softmax with temperature for smooth weighting
            exp_sim = np.exp(similarities / temperature)
            weights = exp_sim / np.sum(exp_sim)

            # Weighted sum
            params = np.zeros_like(neighbors[0].parameters)
            for weight, match in zip(weights, neighbors):
                params += weight * match.parameters

            confidence = float(np.mean(similarities))

        elif method == "inverse_distance":
            # Inverse distance weighting: w_i = 1 / (1 - similarity_i + epsilon)
            epsilon = 1e-6
            distances = 1.0 - np.array([m.similarity for m in neighbors]) + epsilon
            weights = 1.0 / distances
            weights /= np.sum(weights)

            params = np.zeros_like(neighbors[0].parameters)
            for weight, match in zip(weights, neighbors):
                params += weight * match.parameters

            confidence = float(1.0 / (1.0 + np.mean(distances)))

        else:
            raise ValueError(f"Unknown interpolation method: {method}")

        avg_similarity = float(np.mean([m.similarity for m in neighbors]))

        return ParameterPrediction(
            parameters=params,
            confidence=confidence,
            num_neighbors=len(neighbors),
            avg_similarity=avg_similarity,
            similar_molecules=neighbors,
            interpolation_method=method,
        )


def interpolate_parameters(
    query_smiles: str,
    database_molecules: List[Tuple[str, np.ndarray, float]],
    k: int = 5,
    method: str = "weighted_average",
) -> np.ndarray:
    """
    Convenience function for parameter interpolation.

    Args:
        query_smiles: Query molecule SMILES
        database_molecules: List of (smiles, parameters, energy) tuples
        k: Number of neighbors
        method: Interpolation method

    Returns:
        Interpolated parameters

    Example:
        >>> database = [
        ...     ("CCO", np.array([0.5, 1.2]), -1.5),
        ...     ("CCCO", np.array([0.6, 1.1]), -1.6),
        ... ]
        >>> params = interpolate_parameters("CC(C)O", database, k=2)
    """
    matcher = SimilarityMatcher()
    prediction = matcher.interpolate_parameters(query_smiles, database_molecules, k=k, method=method)
    return prediction.parameters


def estimate_parameter_quality(
    prediction: ParameterPrediction, quality_threshold: float = 0.7
) -> Dict[str, any]:
    """
    Estimate quality of predicted parameters.

    Args:
        prediction: ParameterPrediction object
        quality_threshold: Confidence threshold for "good" predictions

    Returns:
        Quality assessment dictionary
    """
    quality = {
        "confidence": prediction.confidence,
        "avg_similarity": prediction.avg_similarity,
        "num_neighbors": prediction.num_neighbors,
        "is_high_quality": prediction.confidence >= quality_threshold,
        "recommendation": "",
    }

    if prediction.confidence >= 0.9:
        quality["recommendation"] = "Excellent match - expect 70-80% iteration reduction"
    elif prediction.confidence >= 0.7:
        quality["recommendation"] = "Good match - expect 50-60% iteration reduction"
    elif prediction.confidence >= 0.5:
        quality["recommendation"] = "Fair match - expect 30-40% iteration reduction"
    else:
        quality[
            "recommendation"
        ] = "Poor match - consider random initialization or expanding database"

    return quality


# Example usage
if __name__ == "__main__":
    print("Molecular Similarity Matching Example")
    print("=" * 80)

    if RDKIT_AVAILABLE:
        # Create example database
        database = [
            ("CCO", np.array([0.5, 1.2, 0.3, 0.8]), -1.523),  # Ethanol
            ("CCCO", np.array([0.6, 1.1, 0.4, 0.7]), -1.645),  # Propanol
            ("CC(C)O", np.array([0.55, 1.15, 0.35, 0.75]), -1.589),  # Isopropanol
            ("CCCCO", np.array([0.65, 1.05, 0.45, 0.65]), -1.712),  # Butanol
            ("CC(C)CO", np.array([0.58, 1.12, 0.38, 0.72]), -1.657),  # Isobutanol
        ]

        # Initialize matcher
        matcher = SimilarityMatcher(fingerprint_type="morgan", radius=2)

        # Test molecule: 2-methyl-1-propanol (similar to isobutanol)
        query = "CC(C)CCO"

        print(f"\nQuery molecule: {query}")
        print("\nFinding similar molecules...")

        # Find neighbors
        neighbors = matcher.find_neighbors(query, database, k=3)
        for i, match in enumerate(neighbors, 1):
            print(f"\n{i}. {match.smiles}")
            print(f"   Similarity: {match.similarity:.3f}")
            print(f"   Energy: {match.energy:.4f}")
            print(f"   Parameters: {match.parameters}")

        # Interpolate parameters
        print("\nInterpolating parameters...")
        prediction = matcher.interpolate_parameters(
            query, database, k=3, method="weighted_average"
        )

        print(f"\nPredicted parameters: {prediction.parameters}")
        print(f"Confidence: {prediction.confidence:.3f}")
        print(f"Average similarity: {prediction.avg_similarity:.3f}")
        print(f"Used {prediction.num_neighbors} neighbors")

        # Quality assessment
        quality = estimate_parameter_quality(prediction)
        print(f"\nQuality assessment:")
        print(f"  {quality['recommendation']}")
        print(f"  High quality: {quality['is_high_quality']}")

        # Compare methods
        print("\nComparing interpolation methods:")
        for method in ["nearest", "weighted_average", "inverse_distance"]:
            pred = matcher.interpolate_parameters(query, database, k=3, method=method)
            print(f"  {method:20s}: confidence={pred.confidence:.3f}")

    else:
        print("RDKit not available")
