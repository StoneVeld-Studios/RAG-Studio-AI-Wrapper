from dataclasses import dataclass
from enum import Enum


class KernelState(Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class Observation:
    files_discovered: int
    files_included: int
    files_excluded: int
    read_failures: int
    redaction_count: int
    token_count: int
    token_limit: int


@dataclass(frozen=True)
class KernelResult:
    state: KernelState
    allowed: bool
    reasons: tuple[str, ...]
    observations: dict


class Kernel:
    """
    Small deterministic decision kernel for RAG Studio.

    The kernel observes facts supplied by the application,
    validates their consistency, compares them against explicit
    limits, and returns a deterministic result.

    It does not access files, networks, GUI components, or AI models.
    """

    WARNING_RATIO = 0.90

    def evaluate(self, observation: Observation) -> KernelResult:
        observations = {
            "files_discovered": observation.files_discovered,
            "files_included": observation.files_included,
            "files_excluded": observation.files_excluded,
            "read_failures": observation.read_failures,
            "redaction_count": observation.redaction_count,
            "token_count": observation.token_count,
            "token_limit": observation.token_limit,
        }

        invalid_reasons = self._validate(observation)

        if invalid_reasons:
            return KernelResult(
                state=KernelState.INVALID,
                allowed=False,
                reasons=tuple(invalid_reasons),
                observations=observations,
            )

        if observation.read_failures > 0:
            return KernelResult(
                state=KernelState.BLOCKED,
                allowed=False,
                reasons=("File read failures detected.",),
                observations=observations,
            )

        if observation.token_count > observation.token_limit:
            return KernelResult(
                state=KernelState.BLOCKED,
                allowed=False,
                reasons=("Token count exceeds context limit.",),
                observations=observations,
            )

        warning_threshold = (
            observation.token_limit * self.WARNING_RATIO
        )

        if observation.token_count >= warning_threshold:
            return KernelResult(
                state=KernelState.WARNING,
                allowed=True,
                reasons=("Token count is approaching context limit.",),
                observations=observations,
            )

        return KernelResult(
            state=KernelState.SAFE,
            allowed=True,
            reasons=(
                "Token count is within context limit.",
                "File counts are consistent.",
                "No file read failures detected.",
            ),
            observations=observations,
        )

    @staticmethod
    def _validate(observation: Observation) -> list[str]:
        numeric_values = (
            observation.files_discovered,
            observation.files_included,
            observation.files_excluded,
            observation.read_failures,
            observation.redaction_count,
            observation.token_count,
            observation.token_limit,
        )

        if any(value < 0 for value in numeric_values):
            return ["Negative observation values are invalid."]

        if observation.token_limit <= 0:
            return ["Token limit must be greater than zero."]

        if (
            observation.files_included
            + observation.files_excluded
            + observation.read_failures
            != observation.files_discovered
        ):
            return ["File counts are inconsistent."]

        return []
