#!/usr/bin/env python3
# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Surface Code Implementation
===========================

Implements rotated surface codes for quantum error correction with distances d=3, 5, 7.

Mathematical Foundation:
-----------------------
Surface codes are topological quantum error-correcting codes defined on a 2D lattice.
For a distance-d code:
- n_data = d²  data qubits
- n_syndrome = d²-1  syndrome qubits (⌊d²/2⌋ X-type, ⌈d²/2⌉ Z-type)
- Code distance: d (corrects ⌊(d-1)/2⌋ errors)

Stabilizers:
-----------
X-type: S_X = X_i X_j X_k X_l  (detects Z errors)
Z-type: S_Z = Z_i Z_j Z_k Z_l  (detects X errors)

Logical Operators:
-----------------
Z_L = Z along vertical chain
X_L = X along horizontal chain

Error Correction Threshold:
--------------------------
For surface codes: p_th ≈ 1.1% (circuit-level)
Logical error rate: P_L ∝ (p/p_th)^((d+1)/2)
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import stim
from loguru import logger


@dataclass
class QubitLayout:
    """Physical layout of qubits in the surface code."""

    data_qubits: List[Tuple[int, int]]
    x_syndrome_qubits: List[Tuple[int, int]]
    z_syndrome_qubits: List[Tuple[int, int]]
    distance: int

    @property
    def n_data(self) -> int:
        return len(self.data_qubits)

    @property
    def n_syndrome(self) -> int:
        return len(self.x_syndrome_qubits) + len(self.z_syndrome_qubits)

    @property
    def total_qubits(self) -> int:
        return self.n_data + self.n_syndrome


@dataclass
class StabilizerSpec:
    """Specification of a stabilizer measurement."""

    type: str  # 'X' or 'Z'
    syndrome_qubit: Tuple[int, int]
    data_qubits: List[Tuple[int, int]]
    order: List[str]  # Order of gates: ['CNOT', 'CNOT', ...]

    def weight(self) -> int:
        """Weight of the stabilizer (number of data qubits involved)."""
        return len(self.data_qubits)


class RotatedSurfaceCode:
    """
    Rotated surface code implementation.

    The rotated layout provides better error correction properties and
    simpler boundary conditions than the standard layout.

    Layout for d=3:
    ---------------
        Z   X   Z
      D   D   D
        X   Z   X
      D   D   D
        Z   X   Z

    Where:
    - D = Data qubit
    - X = X-type syndrome qubit
    - Z = Z-type syndrome qubit
    """

    def __init__(self, distance: int, rounds: int = 1):
        """
        Initialize rotated surface code.

        Args:
            distance: Code distance (3, 5, 7, ...)
            rounds: Number of QEC cycles
        """
        if distance % 2 == 0:
            raise ValueError("Distance must be odd for rotated surface code")
        if distance < 3:
            raise ValueError("Minimum distance is 3")

        self.distance = distance
        self.rounds = rounds
        self.layout = self._generate_layout()
        self.stabilizers = self._generate_stabilizers()

        logger.info(
            f"Initialized rotated surface code: "
            f"d={distance}, "
            f"data_qubits={self.layout.n_data}, "
            f"syndrome_qubits={self.layout.n_syndrome}"
        )

    def _generate_layout(self) -> QubitLayout:
        """
        Generate qubit layout for rotated surface code.

        Mathematical derivation:
        -----------------------
        For distance d:
        - Data qubits: d²
        - X-syndrome: (d²-1)/2  (checkerboard pattern)
        - Z-syndrome: (d²-1)/2
        """
        d = self.distance

        # Data qubits on a d×d grid
        data_qubits = []
        for i in range(d):
            for j in range(d):
                data_qubits.append((i, j))

        # Syndrome qubits on edges (checkerboard pattern)
        x_syndrome = []
        z_syndrome = []

        # X-type syndrome qubits (white squares)
        for i in range(d - 1):
            for j in range(d - 1):
                if (i + j) % 2 == 0:
                    x_syndrome.append((i + 0.5, j + 0.5))

        # Z-type syndrome qubits (black squares)
        for i in range(d - 1):
            for j in range(d - 1):
                if (i + j) % 2 == 1:
                    z_syndrome.append((i + 0.5, j + 0.5))

        # Boundary syndrome qubits
        # Top and bottom edges
        for j in range(d - 1):
            if j % 2 == 0:
                z_syndrome.append((-0.5, j + 0.5))
                z_syndrome.append((d - 0.5, j + 0.5))
            else:
                x_syndrome.append((-0.5, j + 0.5))
                x_syndrome.append((d - 0.5, j + 0.5))

        # Left and right edges
        for i in range(d - 1):
            if i % 2 == 0:
                x_syndrome.append((i + 0.5, -0.5))
                x_syndrome.append((i + 0.5, d - 0.5))
            else:
                z_syndrome.append((i + 0.5, -0.5))
                z_syndrome.append((i + 0.5, d - 0.5))

        return QubitLayout(
            data_qubits=data_qubits,
            x_syndrome_qubits=x_syndrome,
            z_syndrome_qubits=z_syndrome,
            distance=d,
        )

    def _generate_stabilizers(self) -> List[StabilizerSpec]:
        """
        Generate stabilizer specifications.

        Each stabilizer involves 4 data qubits arranged in a plaquette:
            D - D
            |   |
            D - D

        X-type: Detects Z errors (phase flips)
        Z-type: Detects X errors (bit flips)
        """
        stabilizers = []

        # X-type stabilizers
        for sx, sy in self.layout.x_syndrome_qubits:
            data_qubits = self._get_adjacent_data_qubits(sx, sy)
            if len(data_qubits) >= 2:  # At least 2 for boundary
                stabilizers.append(
                    StabilizerSpec(
                        type="X",
                        syndrome_qubit=(sx, sy),
                        data_qubits=data_qubits,
                        order=["H", "CNOT"] * len(data_qubits) + ["H"],
                    )
                )

        # Z-type stabilizers
        for sx, sy in self.layout.z_syndrome_qubits:
            data_qubits = self._get_adjacent_data_qubits(sx, sy)
            if len(data_qubits) >= 2:
                stabilizers.append(
                    StabilizerSpec(
                        type="Z",
                        syndrome_qubit=(sx, sy),
                        data_qubits=data_qubits,
                        order=["CNOT"] * len(data_qubits),
                    )
                )

        return stabilizers

    def _get_adjacent_data_qubits(self, sx: float, sy: float) -> List[Tuple[int, int]]:
        """
        Get data qubits adjacent to syndrome qubit at (sx, sy).

        For a syndrome qubit at fractional coordinates (i+0.5, j+0.5),
        the adjacent data qubits are at integer coordinates:
        (i, j), (i+1, j), (i, j+1), (i+1, j+1)
        """
        adjacent = []
        i_base = int(sx)
        j_base = int(sy)

        for di in [0, 1]:
            for dj in [0, 1]:
                i = i_base + di
                j = j_base + dj
                if (i, j) in self.layout.data_qubits:
                    adjacent.append((i, j))

        return adjacent

    def build_stim_circuit(self, noise_model: Optional["NoiseModel"] = None) -> stim.Circuit:
        """
        Build Stim circuit for surface code QEC.

        Circuit structure:
        -----------------
        1. Initialize data qubits to |0⟩
        2. Initialize syndrome qubits to |+⟩ (X-type) or |0⟩ (Z-type)
        3. For each round:
            a. Measure stabilizers (with noise)
            b. Record detectors
        4. Final data qubit measurement
        5. Define observable (logical Z or X)

        Returns:
            Stim circuit object
        """
        circuit = stim.Circuit()

        # Qubit indexing: data qubits first, then syndrome qubits
        data_qubit_map = {pos: idx for idx, pos in enumerate(self.layout.data_qubits)}
        syndrome_qubit_map = {
            pos: len(data_qubit_map) + idx
            for idx, pos in enumerate(self.layout.x_syndrome_qubits + self.layout.z_syndrome_qubits)
        }

        # 1. Initialization
        circuit.append("R", [data_qubit_map[pos] for pos in self.layout.data_qubits])

        # Initialize X-type syndrome qubits to |+⟩
        x_syndrome_indices = [syndrome_qubit_map[pos] for pos in self.layout.x_syndrome_qubits]
        circuit.append("RX", x_syndrome_indices)

        # Initialize Z-type syndrome qubits to |0⟩
        z_syndrome_indices = [syndrome_qubit_map[pos] for pos in self.layout.z_syndrome_qubits]
        circuit.append("R", z_syndrome_indices)

        # Add noise after initialization
        if noise_model:
            circuit += noise_model.after_reset_noise(self.layout.total_qubits)

        # 2. QEC cycles
        for round_idx in range(self.rounds):
            circuit.append("TICK")

            # Measure X-type stabilizers
            for stabilizer in self.stabilizers:
                if stabilizer.type == "X":
                    self._append_x_stabilizer_measurement(
                        circuit, stabilizer, data_qubit_map, syndrome_qubit_map, noise_model
                    )

            circuit.append("TICK")

            # Measure Z-type stabilizers
            for stabilizer in self.stabilizers:
                if stabilizer.type == "Z":
                    self._append_z_stabilizer_measurement(
                        circuit, stabilizer, data_qubit_map, syndrome_qubit_map, noise_model
                    )

            circuit.append("TICK")

            # Record detectors (compare current round with previous)
            # This implements temporal correlation in syndrome extraction
            for stab_idx, stabilizer in enumerate(self.stabilizers):
                syndrome_idx = syndrome_qubit_map[stabilizer.syndrome_qubit]
                if round_idx == 0:
                    # First round: detector is just the measurement
                    circuit.append("DETECTOR", [stim.target_rec(-len(self.stabilizers) + stab_idx)])
                else:
                    # Subsequent rounds: XOR with previous round
                    circuit.append(
                        "DETECTOR",
                        [
                            stim.target_rec(-len(self.stabilizers) + stab_idx),
                            stim.target_rec(-2 * len(self.stabilizers) + stab_idx),
                        ],
                    )

        # 3. Final measurement of data qubits
        circuit.append("TICK")
        circuit.append(
            "MX" if self.measure_basis == "X" else "MZ",
            [data_qubit_map[pos] for pos in self.layout.data_qubits],
        )

        # Add measurement noise
        if noise_model:
            circuit += noise_model.measurement_noise(self.layout.n_data)

        # 4. Define logical observable
        # Logical Z: product of Z measurements along a vertical line
        # Logical X: product of X measurements along a horizontal line
        logical_qubits = self._get_logical_operator_qubits()
        circuit.append(
            "OBSERVABLE_INCLUDE",
            [stim.target_rec(-self.layout.n_data + data_qubit_map[pos]) for pos in logical_qubits],
            0,
        )

        return circuit

    def _append_x_stabilizer_measurement(
        self,
        circuit: stim.Circuit,
        stabilizer: StabilizerSpec,
        data_map: Dict,
        syndrome_map: Dict,
        noise_model: Optional["NoiseModel"],
    ):
        """
        Append X-type stabilizer measurement to circuit.

        X-stabilizer circuit:
        -------------------
        syndrome: ---H---●---●---●---●---H---M---
                         |   |   |   |
        data_1:   -------X---|---|---|------
        data_2:   -----------X---|---|------
        data_3:   ---------------X---|------
        data_4:   -------------------X------
        """
        syndrome_idx = syndrome_map[stabilizer.syndrome_qubit]
        data_indices = [data_map[pos] for pos in stabilizer.data_qubits]

        # Hadamard on syndrome qubit
        circuit.append("H", [syndrome_idx])

        # CNOT gates from syndrome to data
        for data_idx in data_indices:
            circuit.append("CNOT", [syndrome_idx, data_idx])
            if noise_model:
                circuit += noise_model.two_qubit_gate_noise([syndrome_idx, data_idx])

        # Hadamard and measurement
        circuit.append("H", [syndrome_idx])
        circuit.append("MR", [syndrome_idx])  # Measure and reset

    def _append_z_stabilizer_measurement(
        self,
        circuit: stim.Circuit,
        stabilizer: StabilizerSpec,
        data_map: Dict,
        syndrome_map: Dict,
        noise_model: Optional["NoiseModel"],
    ):
        """
        Append Z-type stabilizer measurement to circuit.

        Z-stabilizer circuit:
        -------------------
        syndrome: ---●---●---●---●---M---
                     |   |   |   |
        data_1:   ---X---|---|---|------
        data_2:   -------X---|---|------
        data_3:   -----------X---|------
        data_4:   ---------------X------
        """
        syndrome_idx = syndrome_map[stabilizer.syndrome_qubit]
        data_indices = [data_map[pos] for pos in stabilizer.data_qubits]

        # CNOT gates from data to syndrome
        for data_idx in data_indices:
            circuit.append("CNOT", [data_idx, syndrome_idx])
            if noise_model:
                circuit += noise_model.two_qubit_gate_noise([data_idx, syndrome_idx])

        # Measurement
        circuit.append("MR", [syndrome_idx])

    def _get_logical_operator_qubits(self) -> List[Tuple[int, int]]:
        """Get qubits for logical operator (Z_L or X_L)."""
        d = self.distance
        if self.measure_basis == "Z":
            # Logical Z: vertical line at column 0
            return [(i, 0) for i in range(d)]
        else:
            # Logical X: horizontal line at row 0
            return [(0, j) for j in range(d)]

    @property
    def measure_basis(self) -> str:
        """Basis for final measurement (default: Z)."""
        return getattr(self, "_measure_basis", "Z")

    @measure_basis.setter
    def measure_basis(self, value: str):
        if value not in ["X", "Z"]:
            raise ValueError("Measure basis must be 'X' or 'Z'")
        self._measure_basis = value

    def adaptive_distance(self, current_error_rate: float) -> int:
        """
        Determine optimal code distance based on current error rate.

        Implements Google Willow-inspired adaptive distance selection.
        Uses below-threshold error correction strategy.

        Args:
            current_error_rate: Current physical error rate per cycle

        Returns:
            Optimal code distance (3, 5, or 7)

        Mathematical basis:
        ------------------
        For below-threshold operation:
        - P_L ∝ (p/p_th)^((d+1)/2)  where p < p_th ≈ 1.1%
        - Error suppression factor: λ ≈ 2.14× per distance increase

        Distance selection strategy:
        - d=3: Low noise (p < 0.1%), minimal overhead
        - d=5: Medium noise (0.1% ≤ p < 0.5%), balanced
        - d=7: High noise (0.5% ≤ p < 1.1%), maximum protection

        Example:
            >>> code = RotatedSurfaceCode(distance=5, rounds=5)
            >>> measured_error = 0.003  # 0.3% error
            >>> optimal_d = code.adaptive_distance(measured_error)
            >>> print(f"Optimal distance: {optimal_d}")
            Optimal distance: 5
        """
        if current_error_rate < 0:
            raise ValueError("Error rate must be non-negative")

        if current_error_rate >= SURFACE_CODE_THRESHOLD:
            logger.warning(
                f"Error rate {current_error_rate:.4f} exceeds threshold "
                f"{SURFACE_CODE_THRESHOLD:.4f}. QEC may not be effective."
            )
            return 7  # Maximum distance

        # Adaptive distance selection based on Willow benchmarks
        if current_error_rate < 0.001:
            # Ultra-low noise: d=3 sufficient
            optimal_distance = 3
            logger.info(f"Low noise regime (p={current_error_rate:.6f}): selecting d=3")
        elif current_error_rate < 0.005:
            # Medium noise: d=5 optimal
            optimal_distance = 5
            logger.info(f"Medium noise regime (p={current_error_rate:.6f}): selecting d=5")
        else:
            # High noise (but below threshold): d=7 required
            optimal_distance = 7
            logger.info(f"High noise regime (p={current_error_rate:.6f}): selecting d=7")

        return optimal_distance

    def estimate_logical_error_rate(
        self, physical_error_rate: float, distance: Optional[int] = None
    ) -> float:
        """
        Estimate logical error rate from physical error rate.

        Uses empirical formula for surface codes:
        P_L ≈ A * (p/p_th)^((d+1)/2)

        where:
        - p: physical error rate
        - p_th: threshold error rate (≈1.1%)
        - d: code distance
        - A: prefactor (≈0.1 for typical surface codes)

        Args:
            physical_error_rate: Physical error probability per cycle
            distance: Code distance (uses self.distance if None)

        Returns:
            Estimated logical error rate

        Example:
            >>> code = RotatedSurfaceCode(distance=5, rounds=5)
            >>> p_physical = 0.001
            >>> p_logical = code.estimate_logical_error_rate(p_physical)
            >>> print(f"Suppression: {p_physical / p_logical:.1f}x")
        """
        d = distance or self.distance

        if physical_error_rate >= SURFACE_CODE_THRESHOLD:
            # Above threshold: logical error rate increases
            return 1.0  # Pessimistic estimate

        # Below-threshold scaling
        exponent = (d + 1) / 2
        prefactor = 0.1  # Empirical prefactor
        p_logical = prefactor * (physical_error_rate / SURFACE_CODE_THRESHOLD) ** exponent

        return min(p_logical, 1.0)  # Cap at 1.0

    def calculate_suppression_factor(
        self, physical_error_rate: float, distance: Optional[int] = None
    ) -> float:
        """
        Calculate error suppression factor.

        Suppression factor λ = p_physical / p_logical

        For Willow-class devices: λ ≈ 2.14 per distance increase

        Args:
            physical_error_rate: Physical error rate
            distance: Code distance (uses self.distance if None)

        Returns:
            Error suppression factor

        Example:
            >>> code = RotatedSurfaceCode(distance=7, rounds=7)
            >>> suppression = code.calculate_suppression_factor(0.001)
            >>> print(f"Error suppression: {suppression:.2f}x")
        """
        p_logical = self.estimate_logical_error_rate(physical_error_rate, distance)

        if p_logical == 0:
            return float("inf")

        return physical_error_rate / p_logical

    def is_below_threshold(self, physical_error_rate: float) -> bool:
        """
        Check if operating in below-threshold regime.

        Below threshold: P_L < P_physical (error correction is effective)

        Args:
            physical_error_rate: Physical error rate

        Returns:
            True if below threshold

        Example:
            >>> code = RotatedSurfaceCode(distance=5, rounds=5)
            >>> code.is_below_threshold(0.001)
            True
            >>> code.is_below_threshold(0.02)
            False
        """
        if physical_error_rate >= SURFACE_CODE_THRESHOLD:
            return False

        p_logical = self.estimate_logical_error_rate(physical_error_rate)
        return p_logical < physical_error_rate


class SurfaceCode:
    """
    Factory class for creating surface codes of various distances.
    """

    @staticmethod
    def distance_3(rounds: int = 1) -> RotatedSurfaceCode:
        """Create distance-3 surface code (9 data qubits)."""
        return RotatedSurfaceCode(distance=3, rounds=rounds)

    @staticmethod
    def distance_5(rounds: int = 1) -> RotatedSurfaceCode:
        """Create distance-5 surface code (25 data qubits)."""
        return RotatedSurfaceCode(distance=5, rounds=rounds)

    @staticmethod
    def distance_7(rounds: int = 1) -> RotatedSurfaceCode:
        """Create distance-7 surface code (49 data qubits)."""
        return RotatedSurfaceCode(distance=7, rounds=rounds)

    @staticmethod
    def custom_distance(distance: int, rounds: int = 1) -> RotatedSurfaceCode:
        """Create surface code with custom distance."""
        return RotatedSurfaceCode(distance=distance, rounds=rounds)


@dataclass
class SimulationResult:
    """Results from surface code simulation."""

    distance: int
    rounds: int
    shots: int
    physical_error_rate: float
    logical_error_rate: float
    logical_errors: int
    detection_events: np.ndarray
    observable_flips: np.ndarray
    runtime_seconds: float
    decoder_time_seconds: float

    @property
    def is_below_threshold(self) -> bool:
        """Check if logical error rate is below physical error rate."""
        return self.logical_error_rate < self.physical_error_rate

    @property
    def suppression_factor(self) -> float:
        """Error suppression factor: physical / logical."""
        if self.logical_error_rate == 0:
            return float("inf")
        return self.physical_error_rate / self.logical_error_rate

    @property
    def avg_latency_us(self) -> float:
        """Average latency per shot in microseconds."""
        return (self.runtime_seconds / self.shots) * 1e6

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "distance": self.distance,
            "rounds": self.rounds,
            "shots": self.shots,
            "physical_error_rate": float(self.physical_error_rate),
            "logical_error_rate": float(self.logical_error_rate),
            "logical_errors": int(self.logical_errors),
            "is_below_threshold": self.is_below_threshold,
            "suppression_factor": float(self.suppression_factor),
            "runtime_seconds": float(self.runtime_seconds),
            "decoder_time_seconds": float(self.decoder_time_seconds),
            "avg_latency_us": float(self.avg_latency_us),
        }


class SurfaceCodeSimulator:
    """
    High-level simulator for surface code quantum error correction.

    Example:
    -------
    >>> sim = SurfaceCodeSimulator(distance=5, physical_error_rate=0.001)
    >>> result = sim.run(shots=10000, decoder='pymatching')
    >>> print(f"Logical error rate: {result.logical_error_rate:.6f}")
    """

    def __init__(
        self,
        distance: int,
        physical_error_rate: float = 0.001,
        rounds: int = None,
        noise_model: str = "depolarizing",
    ):
        """
        Initialize surface code simulator.

        Args:
            distance: Code distance (3, 5, 7, ...)
            physical_error_rate: Physical error probability
            rounds: Number of QEC cycles (default: distance)
            noise_model: Type of noise ('depolarizing', 'bitflip', etc.)
        """
        self.distance = distance
        self.physical_error_rate = physical_error_rate
        self.rounds = rounds if rounds is not None else distance
        self.noise_model_type = noise_model

        # Create surface code
        self.code = RotatedSurfaceCode(distance=distance, rounds=self.rounds)

        # Create noise model
        from .noise_models import get_noise_model

        self.noise_model = get_noise_model(noise_model, error_rate=physical_error_rate)

        # Build circuit
        self.circuit = self.code.build_stim_circuit(noise_model=self.noise_model)

        logger.info(
            f"Initialized simulator: d={distance}, p={physical_error_rate:.4f}, "
            f"rounds={self.rounds}"
        )

    def run(
        self, shots: int = 10000, decoder: str = "pymatching", backend: str = "stim", **kwargs
    ) -> SimulationResult:
        """
        Run surface code simulation.

        Args:
            shots: Number of shots to simulate
            decoder: Decoder type ('pymatching', 'unionfind', etc.)
            backend: Backend for simulation ('stim', 'qiskit', etc.)
            **kwargs: Additional arguments for decoder/backend

        Returns:
            SimulationResult object
        """
        start_time = time.time()

        logger.info(f"Starting simulation: {shots} shots, decoder={decoder}")

        # 1. Sample circuit to get detection events and observables
        sampler = self.circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(shots=shots, separate_observables=True)

        sampling_time = time.time() - start_time
        logger.info(f"Sampling completed in {sampling_time:.3f}s")

        # 2. Decode syndromes
        decoder_start = time.time()

        from ..decoders import get_decoder

        decoder_obj = get_decoder(decoder, **kwargs)
        predicted_observables = decoder_obj.decode_batch(detection_events, self.circuit)

        decoder_time = time.time() - decoder_start
        logger.info(f"Decoding completed in {decoder_time:.3f}s")

        # 3. Compute logical error rate
        logical_errors = np.sum(predicted_observables != observable_flips[:, 0])
        logical_error_rate = logical_errors / shots

        runtime = time.time() - start_time

        result = SimulationResult(
            distance=self.distance,
            rounds=self.rounds,
            shots=shots,
            physical_error_rate=self.physical_error_rate,
            logical_error_rate=logical_error_rate,
            logical_errors=logical_errors,
            detection_events=detection_events,
            observable_flips=observable_flips,
            runtime_seconds=runtime,
            decoder_time_seconds=decoder_time,
        )

        logger.success(
            f"Simulation complete: "
            f"P_L={logical_error_rate:.6f}, "
            f"suppression={result.suppression_factor:.2f}x, "
            f"below_threshold={result.is_below_threshold}"
        )

        return result

    def estimate_logical_error_rate(self, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Estimate logical error rate with confidence interval.

        Uses Wilson score interval for binomial proportion.

        Returns:
            (lower_bound, estimate, upper_bound)
        """
        from scipy import stats

        # Quick sampling for estimate
        result = self.run(shots=1000)
        p = result.logical_error_rate
        n = result.shots

        # Wilson score interval
        z = stats.norm.ppf((1 + confidence) / 2)
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator

        return (center - margin, p, center + margin)


# Physical constants and thresholds
SURFACE_CODE_THRESHOLD = 0.0109  # ~1.1% circuit-level threshold
WILLOW_TARGET_ERROR_RATE = 0.001  # 0.1% per cycle

# Google Willow benchmarks (Dec 2024)
WILLOW_ERROR_RATES = {
    3: 0.00299,  # d=3: 0.299% error per cycle
    5: 0.00143,  # d=5: 0.143% error per cycle
    7: 0.00143,  # d=7: 0.143% error per cycle (below-threshold regime)
}

WILLOW_SUPPRESSION_FACTOR = 2.14  # Error suppression per distance increase


@dataclass
class ErrorMonitoringResult:
    """Real-time error monitoring results."""

    cycle: int
    physical_error_rate: float
    logical_error_rate: float
    suppression_factor: float
    is_below_threshold: bool
    recommended_distance: int
    current_distance: int
    syndrome_weight: float  # Average syndrome weight
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "cycle": self.cycle,
            "physical_error_rate": float(self.physical_error_rate),
            "logical_error_rate": float(self.logical_error_rate),
            "suppression_factor": float(self.suppression_factor),
            "is_below_threshold": self.is_below_threshold,
            "recommended_distance": self.recommended_distance,
            "current_distance": self.current_distance,
            "syndrome_weight": float(self.syndrome_weight),
            "timestamp": self.timestamp,
        }


class WillowAdaptiveQEC:
    """
    Google Willow-inspired adaptive quantum error correction.

    Implements real-time error monitoring and adaptive code distance selection
    based on measured error rates, following Google's December 2024 Willow
    chip demonstrations.

    Key features:
    - Real-time syndrome extraction and error tracking
    - Below-threshold validation (error rate < 1.1%)
    - Adaptive distance selection (d=3,5,7)
    - Error suppression factor monitoring (target: >2× per distance)

    Mathematical foundation:
    -----------------------
    Logical error rate scaling:
        P_L ≈ A * (p/p_th)^((d+1)/2)

    where:
        - p: physical error rate
        - p_th ≈ 1.1%: surface code threshold
        - d: code distance
        - A ≈ 0.1: prefactor

    Willow benchmarks:
    - d=3: 0.299% error/cycle
    - d=5: 0.143% error/cycle
    - d=7: 0.143% error/cycle (below threshold)
    - Suppression: 2.14× per distance increase

    Example:
        >>> # Initialize adaptive QEC
        >>> adaptive_qec = WillowAdaptiveQEC(
        ...     initial_distance=5,
        ...     target_error_rate=0.001,
        ...     monitoring_window=10
        ... )
        >>>
        >>> # Run QEC cycles with monitoring
        >>> for cycle in range(100):
        ...     result = adaptive_qec.monitor_cycle(
        ...         detection_events=syndromes[cycle],
        ...         observable_flip=observables[cycle]
        ...     )
        ...
        ...     if result.recommended_distance != result.current_distance:
        ...         print(f"Adapting distance: {result.current_distance} → {result.recommended_distance}")
        ...         adaptive_qec.adapt_distance(result.recommended_distance)
    """

    def __init__(
        self,
        initial_distance: int = 5,
        target_error_rate: float = WILLOW_TARGET_ERROR_RATE,
        monitoring_window: int = 10,
        adaptation_enabled: bool = True,
    ):
        """
        Initialize Willow adaptive QEC.

        Args:
            initial_distance: Starting code distance (3, 5, or 7)
            target_error_rate: Target physical error rate
            monitoring_window: Number of cycles for error rate estimation
            adaptation_enabled: Enable automatic distance adaptation

        Example:
            >>> qec = WillowAdaptiveQEC(initial_distance=5, target_error_rate=0.001)
        """
        if initial_distance not in [3, 5, 7]:
            raise ValueError("Distance must be 3, 5, or 7")

        self.current_distance = initial_distance
        self.target_error_rate = target_error_rate
        self.monitoring_window = monitoring_window
        self.adaptation_enabled = adaptation_enabled

        # Create surface code
        self.code = RotatedSurfaceCode(distance=initial_distance, rounds=1)

        # Monitoring state
        self._error_history: List[ErrorMonitoringResult] = []
        self._detection_events_buffer: List[np.ndarray] = []
        self._observable_flips_buffer: List[bool] = []
        self._cycle_count = 0

        logger.info(
            f"Initialized Willow Adaptive QEC: "
            f"d={initial_distance}, "
            f"target_error={target_error_rate:.6f}, "
            f"window={monitoring_window}"
        )

    def monitor_cycle(
        self, detection_events: np.ndarray, observable_flip: bool
    ) -> ErrorMonitoringResult:
        """
        Monitor a single QEC cycle.

        Tracks error rates and syndrome patterns in real-time.

        Args:
            detection_events: Binary syndrome measurements for this cycle
            observable_flip: Whether logical observable flipped

        Returns:
            ErrorMonitoringResult with current statistics

        Example:
            >>> result = qec.monitor_cycle(syndromes[0], observables[0])
            >>> print(f"Physical error: {result.physical_error_rate:.6f}")
            >>> print(f"Below threshold: {result.is_below_threshold}")
        """
        self._cycle_count += 1

        # Buffer detection events
        self._detection_events_buffer.append(detection_events)
        self._observable_flips_buffer.append(observable_flip)

        # Trim buffer to monitoring window
        if len(self._detection_events_buffer) > self.monitoring_window:
            self._detection_events_buffer.pop(0)
            self._observable_flips_buffer.pop(0)

        # Estimate error rates
        physical_error_rate = self._estimate_physical_error_rate()
        logical_error_rate = self._estimate_logical_error_rate()

        # Calculate suppression
        if logical_error_rate > 0:
            suppression_factor = physical_error_rate / logical_error_rate
        else:
            suppression_factor = float("inf")

        # Check threshold
        is_below_threshold = self.code.is_below_threshold(physical_error_rate)

        # Recommend distance
        recommended_distance = self.code.adaptive_distance(physical_error_rate)

        # Calculate syndrome weight
        syndrome_weight = np.mean([ev.sum() for ev in self._detection_events_buffer])

        result = ErrorMonitoringResult(
            cycle=self._cycle_count,
            physical_error_rate=physical_error_rate,
            logical_error_rate=logical_error_rate,
            suppression_factor=suppression_factor,
            is_below_threshold=is_below_threshold,
            recommended_distance=recommended_distance,
            current_distance=self.current_distance,
            syndrome_weight=syndrome_weight,
        )

        self._error_history.append(result)

        # Log warnings
        if not is_below_threshold:
            logger.warning(
                f"Cycle {self._cycle_count}: Above threshold! "
                f"p_phys={physical_error_rate:.6f} > p_th={SURFACE_CODE_THRESHOLD:.6f}"
            )

        if suppression_factor < 1.0:
            logger.warning(
                f"Cycle {self._cycle_count}: Error amplification! "
                f"Suppression={suppression_factor:.3f}x < 1.0"
            )

        return result

    def _estimate_physical_error_rate(self) -> float:
        """
        Estimate physical error rate from syndrome weight.

        Uses syndrome density as proxy for physical error rate.
        """
        if not self._detection_events_buffer:
            return 0.0

        # Average syndrome density over window
        total_detections = sum(ev.sum() for ev in self._detection_events_buffer)
        total_checks = sum(len(ev) for ev in self._detection_events_buffer)

        if total_checks == 0:
            return 0.0

        # Syndrome density approximates 2× error rate for surface codes
        syndrome_density = total_detections / total_checks
        estimated_error_rate = syndrome_density / 2.0

        return min(estimated_error_rate, 1.0)

    def _estimate_logical_error_rate(self) -> float:
        """
        Estimate logical error rate from observable flips.

        Counts fraction of cycles with logical errors.
        """
        if not self._observable_flips_buffer:
            return 0.0

        logical_errors = sum(self._observable_flips_buffer)
        total_cycles = len(self._observable_flips_buffer)

        return logical_errors / total_cycles

    def adapt_distance(self, new_distance: int):
        """
        Adapt code distance based on measured error rates.

        Args:
            new_distance: New code distance (3, 5, or 7)

        Example:
            >>> qec.adapt_distance(7)  # Increase protection
        """
        if new_distance not in [3, 5, 7]:
            raise ValueError("Distance must be 3, 5, or 7")

        if new_distance == self.current_distance:
            return

        old_distance = self.current_distance
        self.current_distance = new_distance

        # Recreate surface code
        self.code = RotatedSurfaceCode(distance=new_distance, rounds=1)

        logger.info(f"Adapted code distance: d={old_distance} → d={new_distance}")

    def get_statistics(self) -> Dict:
        """
        Get aggregate statistics from monitoring history.

        Returns:
            Dictionary with error statistics

        Example:
            >>> stats = qec.get_statistics()
            >>> print(f"Average suppression: {stats['avg_suppression_factor']:.2f}x")
        """
        if not self._error_history:
            return {
                "cycles_monitored": 0,
                "avg_physical_error_rate": 0.0,
                "avg_logical_error_rate": 0.0,
                "avg_suppression_factor": 0.0,
                "below_threshold_fraction": 0.0,
            }

        physical_errors = [r.physical_error_rate for r in self._error_history]
        logical_errors = [r.logical_error_rate for r in self._error_history]
        suppressions = [
            r.suppression_factor for r in self._error_history if r.suppression_factor != float("inf")
        ]
        below_threshold = [r.is_below_threshold for r in self._error_history]

        return {
            "cycles_monitored": len(self._error_history),
            "avg_physical_error_rate": float(np.mean(physical_errors)),
            "avg_logical_error_rate": float(np.mean(logical_errors)),
            "avg_suppression_factor": float(np.mean(suppressions)) if suppressions else float("inf"),
            "below_threshold_fraction": sum(below_threshold) / len(below_threshold),
            "current_distance": self.current_distance,
            "error_history": [r.to_dict() for r in self._error_history],
        }

    def validate_below_threshold(self) -> bool:
        """
        Validate that QEC is operating below threshold.

        Checks:
        1. Physical error rate < 1.1%
        2. Logical error rate < Physical error rate
        3. Suppression factor > 1.0

        Returns:
            True if all validation checks pass

        Example:
            >>> if qec.validate_below_threshold():
            ...     print("QEC operating correctly!")
        """
        stats = self.get_statistics()

        if stats["cycles_monitored"] == 0:
            return False

        checks = {
            "physical_below_threshold": stats["avg_physical_error_rate"] < SURFACE_CODE_THRESHOLD,
            "effective_suppression": stats["avg_suppression_factor"] > 1.0,
            "below_threshold_majority": stats["below_threshold_fraction"] > 0.5,
        }

        all_pass = all(checks.values())

        if all_pass:
            logger.success(
                f"Below-threshold validation PASSED: "
                f"p_phys={stats['avg_physical_error_rate']:.6f}, "
                f"suppression={stats['avg_suppression_factor']:.2f}x"
            )
        else:
            logger.error(f"Below-threshold validation FAILED: {checks}")

        return all_pass
