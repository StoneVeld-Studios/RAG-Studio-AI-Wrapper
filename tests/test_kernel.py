import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from lib.kernel import Kernel, KernelState, Observation


def make_observation(**overrides):
    data = {
        "files_discovered": 10,
        "files_included": 8,
        "files_excluded": 2,
        "read_failures": 0,
        "redaction_count": 0,
        "token_count": 1000,
        "token_limit": 4096,
    }
    data.update(overrides)
    return Observation(**data)


def test_safe_observation_is_allowed():
    kernel = Kernel()

    result = kernel.evaluate(make_observation())

    assert result.state == KernelState.SAFE
    assert result.allowed is True


def test_warning_observation_is_allowed():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            token_count=3700,
            token_limit=4096,
        )
    )

    assert result.state == KernelState.WARNING
    assert result.allowed is True


def test_token_overflow_is_blocked():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            token_count=4500,
            token_limit=4096,
        )
    )

    assert result.state == KernelState.BLOCKED
    assert result.allowed is False


def test_inconsistent_file_counts_are_invalid():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            files_discovered=10,
            files_included=12,
            files_excluded=0,
        )
    )

    assert result.state == KernelState.INVALID
    assert result.allowed is False


def test_negative_values_are_invalid():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            redaction_count=-1,
        )
    )

    assert result.state == KernelState.INVALID
    assert result.allowed is False


def test_negative_token_count_is_invalid():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            token_count=-100,
        )
    )

    assert result.state == KernelState.INVALID
    assert result.allowed is False


def test_zero_token_limit_is_invalid():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            token_count=0,
            token_limit=0,
        )
    )

    assert result.state == KernelState.INVALID
    assert result.allowed is False


def test_read_failures_block_transmission():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            read_failures=1,
        )
    )

    assert result.state == KernelState.BLOCKED
    assert result.allowed is False


def test_file_counts_must_balance():
    kernel = Kernel()

    result = kernel.evaluate(
        make_observation(
            files_discovered=10,
            files_included=6,
            files_excluded=1,
        )
    )

    assert result.state == KernelState.INVALID
    assert result.allowed is False


def test_result_contains_observations():
    kernel = Kernel()

    observation = make_observation(
        files_discovered=20,
        files_included=15,
        files_excluded=5,
        redaction_count=3,
        token_count=2000,
    )

    result = kernel.evaluate(observation)

    assert result.observations["files_discovered"] == 20
    assert result.observations["files_included"] == 15
    assert result.observations["files_excluded"] == 5
    assert result.observations["redaction_count"] == 3
    assert result.observations["token_count"] == 2000


def test_safe_evaluation_is_deterministic():
    kernel = Kernel()
    observation = make_observation()

    first = kernel.evaluate(observation)
    second = kernel.evaluate(observation)

    assert first.state == second.state
    assert first.allowed == second.allowed
    assert first.reasons == second.reasons
    assert first.observations == second.observations


def test_kernel_does_not_modify_observation():
    kernel = Kernel()
    observation = make_observation()

    original = observation.__dict__.copy()

    kernel.evaluate(observation)

    assert observation.__dict__ == original
