import numpy as np
import pytest

from parity.domain.correlation import (
    CorrelationMatrixError,
    joint_state_probabilities,
    nearest_correlation,
)


def test_identity_correlation_matches_independence() -> None:
    result = joint_state_probabilities([0.6, 0.5], np.eye(2), seed=7)
    assert result[(1, 1)] == pytest.approx(0.3, abs=2e-5)
    assert result[(0, 0)] == pytest.approx(0.2, abs=2e-5)
    assert sum(result.values()) == pytest.approx(1.0)


def test_positive_and_negative_dependence_move_joint_success_in_expected_direction() -> None:
    independent = joint_state_probabilities([0.5, 0.5], np.eye(2), seed=7)[(1, 1)]
    positive = joint_state_probabilities([0.5, 0.5], [[1, 0.6], [0.6, 1]], seed=7)[(1, 1)]
    negative = joint_state_probabilities([0.5, 0.5], [[1, -0.6], [-0.6, 1]], seed=7)[(1, 1)]
    assert positive > independent > negative


def test_boundary_marginals_are_exact() -> None:
    result = joint_state_probabilities([1.0, 0.0], np.eye(2), seed=7)
    assert result == {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 1.0, (1, 1): 0.0}


def test_nearest_correlation_repairs_small_negative_eigenvalue() -> None:
    matrix = np.array([[1.0, 0.9, 0.9], [0.9, 1.0, 0.61], [0.9, 0.61, 1.0]])
    repaired, metadata = nearest_correlation(matrix, acceptance_threshold=0.2)
    assert metadata.converged
    assert np.linalg.eigvalsh(repaired).min() >= -1e-9
    assert np.diag(repaired) == pytest.approx(np.ones(3))


def test_material_repair_is_rejected() -> None:
    matrix = np.array([[1.0, 0.99, 0.99], [0.99, 1.0, -0.99], [0.99, -0.99, 1.0]])
    with pytest.raises(CorrelationMatrixError, match="materially"):
        nearest_correlation(matrix, acceptance_threshold=0.05)


@pytest.mark.parametrize(
    "matrix",
    [
        [[1, 0.2, 0.1], [0.2, 1, 0.1]],
        [[1, 1.2], [1.2, 1]],
        [[1, 0.3], [0.2, 1]],
    ],
)
def test_malformed_matrices_are_rejected(matrix: list[list[float]]) -> None:
    with pytest.raises(CorrelationMatrixError):
        joint_state_probabilities([0.5, 0.5], matrix, seed=7)
