"""Gaussian-copula primitives for two-to-four settlement indicators."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import multivariate_normal, norm

from parity.domain.settlement import State


class CorrelationMatrixError(ValueError):
    """Raised when a dependence matrix cannot be used without material invention."""


@dataclass(frozen=True, slots=True)
class RepairMetadata:
    iterations: int
    converged: bool
    original_min_eigenvalue: float
    repaired_min_eigenvalue: float
    frobenius_norm: float
    max_entry_change: float
    acceptance_threshold: float


def _validated_matrix(matrix: ArrayLike, dimension: int | None = None) -> NDArray[np.float64]:
    result = np.asarray(matrix, dtype=float)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise CorrelationMatrixError("correlation matrix must be square")
    if dimension is not None and result.shape != (dimension, dimension):
        raise CorrelationMatrixError("correlation matrix dimension does not match probabilities")
    if not np.isfinite(result).all():
        raise CorrelationMatrixError("correlation matrix must contain finite values")
    if not np.allclose(result, result.T, atol=1e-12):
        raise CorrelationMatrixError("correlation matrix must be symmetric")
    if not np.allclose(np.diag(result), 1.0, atol=1e-12):
        raise CorrelationMatrixError("correlation matrix must have a unit diagonal")
    if np.any(result < -1.0) or np.any(result > 1.0):
        raise CorrelationMatrixError("correlations must be between -1 and 1")
    return result


def _project_psd(matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2.0)
    return (vectors * np.maximum(values, 0.0)) @ vectors.T


def nearest_correlation(
    matrix: ArrayLike,
    *,
    acceptance_threshold: float = 0.05,
    tolerance: float = 1e-10,
    max_iterations: int = 100,
) -> tuple[NDArray[np.float64], RepairMetadata]:
    """Return a bounded Higham/Dykstra nearest-correlation repair and diagnostics."""
    original = _validated_matrix(matrix)
    original_min = float(np.linalg.eigvalsh(original).min())
    if original_min >= -tolerance:
        metadata = RepairMetadata(
            iterations=1,
            converged=True,
            original_min_eigenvalue=original_min,
            repaired_min_eigenvalue=original_min,
            frobenius_norm=0.0,
            max_entry_change=0.0,
            acceptance_threshold=acceptance_threshold,
        )
        return original.copy(), metadata

    y = original.copy()
    dykstra = np.zeros_like(original)
    converged = False
    iterations = 0
    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        residual = y - dykstra
        projected = _project_psd(residual)
        dykstra = projected - residual
        previous = y
        y = projected.copy()
        np.fill_diagonal(y, 1.0)
        y = (y + y.T) / 2.0
        scale = max(float(np.linalg.norm(y, ord="fro")), 1.0)
        if float(np.linalg.norm(y - previous, ord="fro")) / scale <= tolerance:
            converged = True
            break

    repaired_min = float(np.linalg.eigvalsh(y).min())
    difference = y - original
    frobenius = float(np.linalg.norm(difference, ord="fro"))
    maximum = float(np.max(np.abs(difference)))
    metadata = RepairMetadata(
        iterations=iterations,
        converged=converged and repaired_min >= -10 * tolerance,
        original_min_eigenvalue=original_min,
        repaired_min_eigenvalue=repaired_min,
        frobenius_norm=frobenius,
        max_entry_change=maximum,
        acceptance_threshold=acceptance_threshold,
    )
    if not metadata.converged:
        raise CorrelationMatrixError("nearest-correlation repair did not converge")
    if maximum > acceptance_threshold:
        raise CorrelationMatrixError("correlation matrix requires a materially large repair")
    return y, metadata


def joint_state_probabilities(
    probabilities: list[float],
    correlation: ArrayLike,
    *,
    seed: int,
    maxpts: int = 1_000_000,
    abseps: float = 1e-8,
    releps: float = 1e-8,
) -> dict[State, float]:
    """Evaluate Gaussian-copula rectangle probabilities in lexicographic state order."""
    if not 2 <= len(probabilities) <= 4:
        raise ValueError("supported combos contain two to four probabilities")
    if any(not 0 <= probability <= 1 for probability in probabilities):
        raise ValueError("probabilities must be between 0 and 1")
    matrix = _validated_matrix(correlation, len(probabilities))
    if float(np.linalg.eigvalsh(matrix).min()) < -1e-10:
        raise CorrelationMatrixError("correlation matrix is not positive semidefinite")

    all_states = tuple(product((0, 1), repeat=len(probabilities)))
    active = [index for index, probability in enumerate(probabilities) if 0 < probability < 1]
    deterministic = {
        index: int(probability == 1.0)
        for index, probability in enumerate(probabilities)
        if index not in active
    }
    result: dict[State, float] = {}
    if not active:
        winning_state = tuple(deterministic[index] for index in range(len(probabilities)))
        return {state: float(state == winning_state) for state in all_states}

    submatrix = matrix[np.ix_(active, active)]
    thresholds = norm.ppf([probabilities[index] for index in active])
    for state_index, state in enumerate(all_states):
        if any(state[index] != outcome for index, outcome in deterministic.items()):
            result[state] = 0.0
            continue
        lower = np.array(
            [-np.inf if state[index] else thresholds[offset] for offset, index in enumerate(active)]
        )
        upper = np.array(
            [thresholds[offset] if state[index] else np.inf for offset, index in enumerate(active)]
        )
        probability = float(
            multivariate_normal.cdf(
                upper,
                mean=np.zeros(len(active)),
                cov=submatrix,
                allow_singular=True,
                maxpts=maxpts,
                abseps=abseps,
                releps=releps,
                lower_limit=lower,
                rng=np.random.default_rng(seed + state_index),
            )
        )
        if not np.isfinite(probability) or probability < -1e-8 or probability > 1 + 1e-8:
            raise CorrelationMatrixError("Gaussian rectangle integration returned an invalid value")
        result[state] = min(1.0, max(0.0, probability))

    total = sum(result.values())
    if abs(total - 1.0) > 1e-5:
        raise CorrelationMatrixError("joint state probabilities do not sum to one")
    return {state: probability / total for state, probability in result.items()}
