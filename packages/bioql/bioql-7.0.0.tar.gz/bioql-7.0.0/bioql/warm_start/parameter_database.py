# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
VQE Parameter Database for Warm Starting

Implements a persistent SQLite database for caching converged VQE parameters
along with molecular descriptors for similarity-based parameter retrieval.

Key Features:
- SQLite-based storage for parameters and metadata
- Molecular descriptor calculation (MW, logP, TPSA, etc.)
- SMILES canonicalization for consistent lookups
- Similarity search integration
- Automatic parameter versioning

Database Schema:
- molecules: SMILES, canonical_smiles, fingerprint, descriptors
- vqe_parameters: molecule_id, parameters, energy, metadata
- training_runs: timestamp, configuration, performance metrics

Usage:
    >>> db = ParameterDatabase("vqe_params.db")
    >>> db.store_parameters("CCO", params, energy=-1.5, metadata={...})
    >>> params = db.get_parameters("CCO")
    >>> similar = db.find_similar_molecules("CC(C)O", top_k=5)
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class MolecularDescriptor:
    """Molecular descriptors for characterizing molecules."""

    smiles: str
    canonical_smiles: str
    molecular_weight: float
    num_atoms: int
    num_heavy_atoms: int
    num_bonds: int
    num_aromatic_rings: int
    num_rotatable_bonds: int
    logp: float  # Partition coefficient
    tpsa: float  # Topological polar surface area
    num_hba: int  # Hydrogen bond acceptors
    num_hbd: int  # Hydrogen bond donors
    num_heteroatoms: int
    formal_charge: int
    fingerprint: np.ndarray = field(repr=False)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "smiles": self.smiles,
            "canonical_smiles": self.canonical_smiles,
            "molecular_weight": self.molecular_weight,
            "num_atoms": self.num_atoms,
            "num_heavy_atoms": self.num_heavy_atoms,
            "num_bonds": self.num_bonds,
            "num_aromatic_rings": self.num_aromatic_rings,
            "num_rotatable_bonds": self.num_rotatable_bonds,
            "logp": self.logp,
            "tpsa": self.tpsa,
            "num_hba": self.num_hba,
            "num_hbd": self.num_hbd,
            "num_heteroatoms": self.num_heteroatoms,
            "formal_charge": self.formal_charge,
            "fingerprint": self.fingerprint.tolist(),
        }


class ParameterDatabase:
    """
    SQLite database for storing and retrieving VQE parameters.

    The database stores:
    - Molecular structures (SMILES, fingerprints, descriptors)
    - Converged VQE parameters with energies
    - Metadata (ansatz, optimizer, convergence info)
    - Training run history
    """

    def __init__(self, db_path: str = "vqe_parameters.db"):
        """
        Initialize parameter database.

        Args:
            db_path: Path to SQLite database file
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for parameter database. Install: pip install rdkit")

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_database()

        logger.info(f"Initialized VQE parameter database at {db_path}")

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Molecules table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS molecules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smiles TEXT NOT NULL,
                canonical_smiles TEXT UNIQUE NOT NULL,
                fingerprint BLOB NOT NULL,
                descriptors TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # VQE parameters table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vqe_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                molecule_id INTEGER NOT NULL,
                parameters BLOB NOT NULL,
                energy REAL NOT NULL,
                ansatz TEXT NOT NULL,
                num_layers INTEGER NOT NULL,
                optimizer TEXT NOT NULL,
                iterations INTEGER,
                convergence_threshold REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (molecule_id) REFERENCES molecules(id)
            )
        """
        )

        # Training runs table (for Flow-VQE)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS training_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_name TEXT NOT NULL,
                num_molecules INTEGER NOT NULL,
                config TEXT NOT NULL,
                final_loss REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indices for fast lookup
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_canonical_smiles " "ON molecules(canonical_smiles)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_molecule_id " "ON vqe_parameters(molecule_id)")

        self.conn.commit()

    def compute_descriptors(self, smiles: str) -> MolecularDescriptor:
        """
        Compute molecular descriptors from SMILES.

        Args:
            smiles: SMILES string

        Returns:
            MolecularDescriptor object with all computed properties
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")

        # Canonical SMILES
        canonical_smiles = Chem.MolToSmiles(mol, canonical=True)

        # Compute fingerprint (Morgan, radius 2, 2048 bits)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        fingerprint = np.array(fp)

        # Compute descriptors
        descriptors = MolecularDescriptor(
            smiles=smiles,
            canonical_smiles=canonical_smiles,
            molecular_weight=Descriptors.MolWt(mol),
            num_atoms=mol.GetNumAtoms(),
            num_heavy_atoms=mol.GetNumHeavyAtoms(),
            num_bonds=mol.GetNumBonds(),
            num_aromatic_rings=rdMolDescriptors.CalcNumAromaticRings(mol),
            num_rotatable_bonds=rdMolDescriptors.CalcNumRotatableBonds(mol),
            logp=Descriptors.MolLogP(mol),
            tpsa=Descriptors.TPSA(mol),
            num_hba=rdMolDescriptors.CalcNumHBA(mol),
            num_hbd=rdMolDescriptors.CalcNumHBD(mol),
            num_heteroatoms=rdMolDescriptors.CalcNumHeteroatoms(mol),
            formal_charge=Chem.GetFormalCharge(mol),
            fingerprint=fingerprint,
        )

        return descriptors

    def store_parameters(
        self,
        smiles: str,
        parameters: np.ndarray,
        energy: float,
        ansatz: str = "RealAmplitudes",
        num_layers: int = 2,
        optimizer: str = "COBYLA",
        iterations: Optional[int] = None,
        convergence_threshold: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> int:
        """
        Store VQE parameters in database.

        Args:
            smiles: SMILES string
            parameters: Converged VQE parameters
            energy: Final energy
            ansatz: Ansatz type used
            num_layers: Number of ansatz layers
            optimizer: Optimizer used
            iterations: Number of iterations to convergence
            convergence_threshold: Energy convergence threshold
            metadata: Additional metadata dict

        Returns:
            Parameter record ID

        Example:
            >>> db = ParameterDatabase()
            >>> params = np.array([0.5, 1.2, 0.3, 0.8])
            >>> record_id = db.store_parameters("CCO", params, energy=-1.5, iterations=42)
        """
        cursor = self.conn.cursor()

        # Compute descriptors
        descriptors = self.compute_descriptors(smiles)

        # Check if molecule exists
        cursor.execute(
            "SELECT id FROM molecules WHERE canonical_smiles = ?", (descriptors.canonical_smiles,)
        )
        row = cursor.fetchone()

        if row is None:
            # Insert new molecule
            cursor.execute(
                """
                INSERT INTO molecules (smiles, canonical_smiles, fingerprint, descriptors)
                VALUES (?, ?, ?, ?)
            """,
                (
                    smiles,
                    descriptors.canonical_smiles,
                    descriptors.fingerprint.tobytes(),
                    json.dumps(descriptors.to_dict()),
                ),
            )
            molecule_id = cursor.lastrowid
        else:
            molecule_id = row[0]

        # Insert parameters
        cursor.execute(
            """
            INSERT INTO vqe_parameters (
                molecule_id, parameters, energy, ansatz, num_layers, optimizer,
                iterations, convergence_threshold, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                molecule_id,
                parameters.tobytes(),
                energy,
                ansatz,
                num_layers,
                optimizer,
                iterations,
                convergence_threshold,
                json.dumps(metadata) if metadata else None,
            ),
        )

        param_id = cursor.lastrowid
        self.conn.commit()

        logger.info(f"Stored parameters for {descriptors.canonical_smiles} (ID: {param_id})")

        return param_id

    def get_parameters(
        self, smiles: str, ansatz: Optional[str] = None, num_layers: Optional[int] = None
    ) -> Optional[Tuple[np.ndarray, float, Dict]]:
        """
        Retrieve VQE parameters for a molecule.

        Args:
            smiles: SMILES string
            ansatz: Filter by ansatz type (optional)
            num_layers: Filter by number of layers (optional)

        Returns:
            Tuple of (parameters, energy, metadata) or None if not found

        Example:
            >>> db = ParameterDatabase()
            >>> result = db.get_parameters("CCO", ansatz="RealAmplitudes")
            >>> if result:
            ...     params, energy, metadata = result
        """
        # Canonicalize SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        canonical_smiles = Chem.MolToSmiles(mol, canonical=True)

        cursor = self.conn.cursor()

        # Build query
        query = """
            SELECT p.parameters, p.energy, p.metadata, p.iterations
            FROM vqe_parameters p
            JOIN molecules m ON p.molecule_id = m.id
            WHERE m.canonical_smiles = ?
        """
        params = [canonical_smiles]

        if ansatz:
            query += " AND p.ansatz = ?"
            params.append(ansatz)

        if num_layers is not None:
            query += " AND p.num_layers = ?"
            params.append(num_layers)

        query += " ORDER BY p.created_at DESC LIMIT 1"

        cursor.execute(query, params)
        row = cursor.fetchone()

        if row is None:
            return None

        parameters = np.frombuffer(row[0], dtype=np.float64)
        energy = row[1]
        metadata = json.loads(row[2]) if row[2] else {}
        metadata["iterations"] = row[3]

        return parameters, energy, metadata

    def find_similar_molecules(
        self, smiles: str, top_k: int = 5, min_similarity: float = 0.5
    ) -> List[Tuple[str, float, np.ndarray, float]]:
        """
        Find similar molecules with stored parameters using Tanimoto similarity.

        Args:
            smiles: Query SMILES string
            top_k: Number of similar molecules to return
            min_similarity: Minimum Tanimoto similarity threshold

        Returns:
            List of (smiles, similarity, parameters, energy) tuples

        Example:
            >>> db = ParameterDatabase()
            >>> similar = db.find_similar_molecules("CC(C)O", top_k=5)
            >>> for smiles, sim, params, energy in similar:
            ...     print(f"{smiles}: similarity={sim:.3f}, energy={energy:.4f}")
        """
        # Compute query fingerprint
        query_descriptors = self.compute_descriptors(smiles)
        query_fp = query_descriptors.fingerprint

        cursor = self.conn.cursor()

        # Get all molecules with parameters
        cursor.execute(
            """
            SELECT DISTINCT m.canonical_smiles, m.fingerprint
            FROM molecules m
            JOIN vqe_parameters p ON m.id = p.molecule_id
        """
        )

        similarities = []
        for row in cursor.fetchall():
            mol_smiles = row[0]
            mol_fp = np.frombuffer(row[1], dtype=np.uint8)

            # Compute Tanimoto similarity
            similarity = self._tanimoto_similarity(query_fp, mol_fp)

            if similarity >= min_similarity:
                similarities.append((mol_smiles, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:top_k]

        # Retrieve parameters for top matches
        results = []
        for mol_smiles, similarity in similarities:
            param_data = self.get_parameters(mol_smiles)
            if param_data:
                parameters, energy, metadata = param_data
                results.append((mol_smiles, similarity, parameters, energy))

        logger.info(f"Found {len(results)} similar molecules to {smiles}")

        return results

    def _tanimoto_similarity(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """
        Compute Tanimoto (Jaccard) similarity between fingerprints.

        Tanimoto = |A ∩ B| / |A ∪ B|
        """
        intersection = np.sum(fp1 & fp2)
        union = np.sum(fp1 | fp2)

        if union == 0:
            return 0.0

        return float(intersection) / float(union)

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM molecules")
        num_molecules = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vqe_parameters")
        num_parameter_sets = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(iterations) FROM vqe_parameters WHERE iterations IS NOT NULL")
        avg_iterations = cursor.fetchone()[0] or 0.0

        return {
            "num_molecules": num_molecules,
            "num_parameter_sets": num_parameter_sets,
            "avg_iterations": avg_iterations,
            "db_path": self.db_path,
        }

    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info(f"Closed database connection to {self.db_path}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example usage
if __name__ == "__main__":
    print("VQE Parameter Database Example")
    print("=" * 80)

    if RDKIT_AVAILABLE:
        # Initialize database
        db = ParameterDatabase("test_vqe_params.db")

        # Store some example parameters
        molecules = [
            ("CCO", np.array([0.5, 1.2, 0.3, 0.8]), -1.523),
            ("CCCO", np.array([0.6, 1.1, 0.4, 0.7]), -1.645),
            ("CC(C)O", np.array([0.55, 1.15, 0.35, 0.75]), -1.589),
            ("CCCCO", np.array([0.65, 1.05, 0.45, 0.65]), -1.712),
        ]

        print("\nStoring parameters for molecules:")
        for smiles, params, energy in molecules:
            db.store_parameters(smiles, params, energy, iterations=50, metadata={"test": True})
            print(f"  {smiles}: energy={energy:.4f}")

        # Retrieve parameters
        print("\nRetrieving parameters for CCO:")
        result = db.get_parameters("CCO")
        if result:
            params, energy, metadata = result
            print(f"  Parameters: {params}")
            print(f"  Energy: {energy:.4f}")
            print(f"  Iterations: {metadata.get('iterations')}")

        # Find similar molecules
        print("\nFinding molecules similar to CC(C)C:")
        similar = db.find_similar_molecules("CC(C)C", top_k=3)
        for smiles, similarity, params, energy in similar:
            print(f"  {smiles}: similarity={similarity:.3f}, energy={energy:.4f}")

        # Statistics
        print("\nDatabase statistics:")
        stats = db.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        db.close()
    else:
        print("RDKit not available")
