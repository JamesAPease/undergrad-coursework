"""
Dokkan Battle Damage Calculator
===============================

Models whether a unit survives an enemy super attack in Dragon Ball Z Dokkan
Battle, accounting for enemy attack stacking, super-attack defense boosts,
guard, damage reduction, critical hits, and enemy debuffs.

It also works backward: given an enemy attack, it solves for the minimum
start-of-turn defense a unit needs to survive.

Damage model used here
    Enemy super  = (base + base * actions * stack_rate) * (1 + attack_boost)
    Unit DEF     = SOT DEF * (1 + supers * boost_per_super) * (1 - DEF debuff)
    Normal hit   = max(0, super * (1 - DR) * guard - DEF), guard = 0.5 or 1.0
    Critical hit = max(0, super * (1 - DR))   (ignores guard and DEF)

Usage
    python dokkan_calculator.py
"""

from dataclasses import dataclass, replace


@dataclass
class Enemy:
    base_super: float
    actions: int = 0               # actions taken so far (for stacking supers)
    stack_rate: float = 0.0        # attack gained per action, e.g. 0.10 = 10%
    attack_boost: float = 0.0      # flat attack increase, e.g. 1.00 = +100%
    crit: bool = False
    hp_debuff: float = 0.0         # % of max HP cut at start of turn
    def_debuff: float = 0.0        # % of unit DEF lowered

    @property
    def super_attack(self) -> float:
        stacked = self.base_super * (1 + self.actions * self.stack_rate)
        return stacked * (1 + self.attack_boost)


@dataclass
class Unit:
    max_hp: float
    sot_defense: float             # DEF shown at start of turn
    supers: int = 1                # supers performed this turn
    boost_per_super: float = 0.30  # standard raise, 30% per super
    guard: bool = False
    damage_reduction: float = 0.0  # e.g. 0.40 = 40% DR

    def defense_multiplier(self, enemy: Enemy) -> float:
        return (1 + self.supers * self.boost_per_super) * (1 - enemy.def_debuff)


def simulate(unit: Unit, enemy: Enemy) -> dict:
    """Return the full breakdown of one enemy super against one unit."""
    atk = enemy.super_attack
    defense = unit.sot_defense * unit.defense_multiplier(enemy)
    starting_hp = unit.max_hp * (1 - enemy.hp_debuff)

    if enemy.crit:
        damage = max(0, atk * (1 - unit.damage_reduction))
    else:
        guard = 0.5 if unit.guard else 1.0
        damage = max(0, atk * (1 - unit.damage_reduction) * guard - defense)

    remaining = starting_hp - damage
    return {
        "enemy_super": atk,
        "final_defense": defense,
        "starting_hp": starting_hp,
        "damage_taken": damage,
        "remaining_hp": remaining,
        "survived": remaining > 0,
    }


def min_defense_to_survive(unit: Unit, enemy: Enemy) -> float | None:
    """Smallest start-of-turn DEF that survives this hit, or None if DEF can't help."""
    if enemy.crit:
        return None  # crits ignore DEF, so no amount of DEF changes the outcome
    guard = 0.5 if unit.guard else 1.0
    incoming = enemy.super_attack * (1 - unit.damage_reduction) * guard
    starting_hp = unit.max_hp * (1 - enemy.hp_debuff)
    needed_final_def = max(0, incoming - starting_hp)
    return needed_final_def / unit.defense_multiplier(enemy)


def report(label: str, unit: Unit, enemy: Enemy) -> None:
    r = simulate(unit, enemy)
    print(f"\n{label}")
    print("-" * 44)
    print(f"Enemy super attack:   {r['enemy_super']:>16,.0f}")
    print(f"Unit DEF (final):     {r['final_defense']:>16,.0f}")
    print(f"Damage taken:         {r['damage_taken']:>16,.0f}")
    print(f"Starting HP:          {r['starting_hp']:>16,.0f}")
    if r["survived"]:
        print(f"Result:  SURVIVED with {r['remaining_hp']:,.0f} HP "
              f"({r['remaining_hp'] / unit.max_hp:.1%} of max)")
    else:
        print(f"Result:  DEFEATED, over-killed by {-r['remaining_hp']:,.0f}")

    needed = min_defense_to_survive(unit, enemy)
    if needed is None:
        print("Min SOT DEF to survive: n/a (critical hits ignore DEF)")
    else:
        print(f"Min SOT DEF to survive: {needed:,.0f}")


def main():
    unit = Unit(max_hp=987_069, sot_defense=17_970_780, supers=2,
                guard=True, damage_reduction=0.30)

    # Compare the same boss attack across scenarios
    boss = Enemy(base_super=8_750_000, actions=16, stack_rate=0.10)
    report("Stacking boss, after 16 actions", unit, boss)
    report("Same boss, critical hit", unit, replace(boss, crit=True))
    report("Same boss, with DEF and HP debuffs", unit,
           replace(boss, def_debuff=0.30, hp_debuff=0.20))

    # How survival changes as the boss keeps stacking
    print("\nSurvival by number of enemy actions")
    print("-" * 44)
    for actions in range(0, 121, 20):
        r = simulate(unit, replace(boss, actions=actions))
        status = "survives" if r["survived"] else "defeated"
        print(f"{actions:>3} actions  super {r['enemy_super']:>12,.0f}  {status}")

    breaking_point = next(
        a for a in range(0, 1000)
        if not simulate(unit, replace(boss, actions=a))["survived"]
    )
    print(f"\nThis unit first goes down after {breaking_point} enemy actions.")


if __name__ == "__main__":
    main()
