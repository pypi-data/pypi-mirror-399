from typing import Iterable, List


class DeterministicScheduler:
    """
    Deterministic scheduler.

    TOON:
    - Graph controls order
    - Scheduler does not branch
    """

    def select_next(self, candidates: Iterable[str]) -> List[str]:
        return list(candidates)
