from dataclasses import dataclass


@dataclass(frozen=True)
class Cost:
    """
    Cost metadata for an LLM call.
    """
    tokens: int
    usd: float


class CostCalculator:
    """
    Estimates cost based on tokens.
    """

    def estimate(self, tokens: int, price_per_1k: float) -> Cost:
        usd = (tokens / 1000.0) * price_per_1k
        return Cost(tokens=tokens, usd=usd)
