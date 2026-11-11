"""
Shiny Pokémon Odds Analysis
===========================

How many encounters does a shiny hunt really take? Each encounter is an
independent trial with probability p = 1/odds, so encounters until the first
shiny follow a geometric distribution:

    P(at least 1 shiny in n)  = 1 - (1 - p)^n
    P(at least 2 shinies in n) = 1 - [(1 - p)^n + n p (1 - p)^(n - 1)]
    Encounters for a q chance  = ln(1 - q) / ln(1 - p)

The expected number of encounters is 1/p, but the median is about 31% lower,
which is why most hunts finish "early" while a few run very long.

Usage
    python shiny_odds.py            # prints tables and saves shiny_odds.png
"""

import numpy as np
import pandas as pd

# Common rates in modern games (Gen 6+); exact methods vary by game
RATES = {
    "Base (1/4096)": 4096,
    "Shiny Charm (1/1365)": 4096 / 3,
    "Masuda + Charm (1/512)": 512,
}


def prob_at_least_one(n, odds):
    p = 1 / odds
    return 1 - (1 - p) ** n


def prob_at_least_two(n, odds):
    p = 1 / odds
    return 1 - ((1 - p) ** n + n * p * (1 - p) ** (n - 1))


def encounters_for_chance(q, odds):
    """Encounters needed to reach a probability q of at least one shiny."""
    p = 1 / odds
    return int(np.ceil(np.log(1 - q) / np.log(1 - p)))


def milestone_table() -> pd.DataFrame:
    """Encounters needed to hit common confidence levels, by rate."""
    rows = []
    for label, odds in RATES.items():
        rows.append({
            "Method": label,
            "Expected (mean)": round(odds),
            "50% chance": encounters_for_chance(0.50, odds),
            "75% chance": encounters_for_chance(0.75, odds),
            "90% chance": encounters_for_chance(0.90, odds),
            "99% chance": encounters_for_chance(0.99, odds),
        })
    return pd.DataFrame(rows)


def probability_table(odds: float = 4096, n_max: int = 10_000, step: int = 1_000) -> pd.DataFrame:
    n = np.arange(step, n_max + 1, step)
    return pd.DataFrame({
        "Encounters": n,
        "P(>=1 shiny)": (prob_at_least_one(n, odds) * 100).round(1),
        "P(>=2 shinies)": (prob_at_least_two(n, odds) * 100).round(1),
    })


def plot(path: str = "shiny_odds.png", n_max: int = 15_000) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = np.arange(0, n_max + 1)
    fig, ax = plt.subplots(figsize=(9, 5))
    for label, odds in RATES.items():
        ax.plot(n, prob_at_least_one(n, odds) * 100, label=label)
    ax.axhline(50, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Chance of at least one shiny by number of encounters")
    ax.set_xlabel("Encounters")
    ax.set_ylabel("Probability (%)")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"\nSaved chart to {path}")


def main():
    print("Encounters needed to reach each probability")
    print(milestone_table().to_string(index=False))

    print("\nFull-odds hunt (1/4096) by encounter count")
    print(probability_table().to_string(index=False))

    plot()


if __name__ == "__main__":
    main()
