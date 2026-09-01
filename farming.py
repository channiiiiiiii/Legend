# -*- coding: utf-8 -*-
"""Engraving and gem farming domain rules."""

import random

GRADES = ["normal", "advanced", "rare", "hero", "legend", "relic", "ancient"]
GRADE_NAMES = dict(zip(GRADES, ["Normal", "Advanced", "Rare", "Hero", "Legend", "Relic", "Ancient"]))
TIER_NAMES = {1: "normal", 2: "hard", 3: "nightmare", 4: "mythic"}
GRADE_WEIGHTS = {
    1: (["normal", "advanced", "rare", "hero"], [45, 35, 15, 5]),
    2: (["advanced", "rare", "hero", "legend"], [42, 35, 18, 5]),
    3: (["rare", "hero", "legend", "relic"], [42, 35, 18, 5]),
    4: (["hero", "legend", "relic", "ancient"], [48, 33, 17, 2]),
}

RELIC_VALUES = {
    "atk": [5, 10, 20, 35, 50, 70, 90], "spd": [3, 6, 10, 16, 24, 34, 45],
    "crit": [3, 6, 10, 16, 24, 34, 45], "basic_dmg": [2, 3, 5, 7, 10, 14, 18],
    "unique_dmg": [2, 3, 5, 7, 10, 14, 18], "ultimate_dmg": [2, 4, 6, 9, 12, 15, 18],
    "crit_dmg": [3, 5, 8, 12, 16, 19, 22], "boss_dmg": [1, 2, 3, 5, 7, 9, 10],
    "first3_dmg": [2, 3, 5, 7, 10, 13, 15], "high_hp_dmg": [2, 3, 5, 7, 10, 13, 15],
    "low_hp_dmg": [3, 4, 6, 9, 12, 14, 16], "spd_adv_dmg": [2, 3, 5, 7, 10, 13, 15],
    "lifesteal": [1, 2, 3, 4, 5, 7, 8], "extra_hit": [0, 0, 2, 3, 5, 6, 8],
    "gold_gain": [1, 2, 3, 4, 5, 6, 7], "train_exp": [1, 2, 3, 4, 5, 6, 7],
    "happiness_gain": [1, 2, 3, 4, 5, 6, 7],
}
ARMOR_VALUES = {
    "hp": [30, 60, 100, 150, 220, 300, 400], "def": [5, 10, 20, 35, 50, 70, 90],
    "spd": [3, 6, 10, 16, 24, 34, 45], "dmg_red": [1, 2, 3, 4, 6, 7, 8],
    "boss_dmg_red": [1, 2, 3, 5, 7, 9, 10], "low_hp_dmg_red": [2, 3, 5, 7, 10, 13, 15],
    "first3_dmg_red": [2, 3, 5, 7, 10, 13, 15], "heal_bonus": [2, 3, 5, 7, 10, 13, 15],
    "turn_regen": [0.2, 0.3, 0.5, 0.7, 1, 1.3, 1.5], "shield_bonus": [2, 3, 5, 7, 10, 13, 15],
    "crit_dmg_red": [2, 3, 5, 7, 10, 13, 15], "half_dmg_chance": [0, 0, 2, 3, 4, 5, 6],
    "hunger_slow": [1, 2, 3, 4, 5, 6, 7], "clean_slow": [1, 2, 3, 4, 5, 6, 7],
    "energy_save": [1, 2, 3, 4, 5, 6, 7],
}
GEM_TYPES = ("hp", "atk", "def", "spd", "crit")
GEM_VALUES = {
    "hp": [20, 40, 70, 110, 160, 220, 290, 370, 460, 560],
    "atk": [5, 10, 18, 28, 40, 54, 70, 88, 108, 130],
    "def": [5, 10, 18, 28, 40, 54, 70, 88, 108, 130],
    "spd": [3, 6, 10, 15, 21, 28, 36, 45, 55, 66],
    "crit": [3, 6, 10, 15, 21, 28, 36, 45, 55, 66],
}


def default_gems():
    return {key: {str(level): 0 for level in range(1, 11)} for key in GEM_TYPES}


def normalize_inventory(inv, data=None):
    data = data or {}
    for kind in ("relic", "armor"):
        rows = list(data.get(f"{kind}_engravings", getattr(inv, f"{kind}_engravings", [])) or [])[:3]
        locks = list(data.get(f"{kind}_engraving_locks", getattr(inv, f"{kind}_engraving_locks", [])) or [])[:3]
        setattr(inv, f"{kind}_engravings", rows + [None] * (3 - len(rows)))
        setattr(inv, f"{kind}_engraving_locks", locks + [False] * (3 - len(locks)))
    raw = data.get("gems", getattr(inv, "gems", {})) or {}
    inv.gems = default_gems()
    for gem_type in GEM_TYPES:
        for level in range(1, 11):
            inv.gems[gem_type][str(level)] = max(0, int(raw.get(gem_type, {}).get(str(level), 0)))
    equipped = data.get("equipped_gems", getattr(inv, "equipped_gems", {})) or {}
    inv.equipped_gems = {key: max(0, min(10, int(equipped.get(key, 0)))) for key in GEM_TYPES}


def stone_item_id(kind, tier):
    return f"{TIER_NAMES[tier]}_{kind}_engraving_stone"


def roll_engraving(kind, tier, excluded=()):
    values = RELIC_VALUES if kind == "relic" else ARMOR_VALUES
    available = [key for key in values if key not in set(excluded)]
    if not available:
        raise ValueError("No unique engraving option remains")
    grades, weights = GRADE_WEIGHTS[tier]
    grade = random.choices(grades, weights=weights, k=1)[0]
    option = random.choice(available)
    return {"option": option, "grade": grade, "value": values[option][GRADES.index(grade)]}


def reroll_engraving(inv, kind, slot, tier):
    if kind not in ("relic", "armor") or slot not in range(3) or tier not in TIER_NAMES:
        return False, "invalid engraving request"
    rows = getattr(inv, f"{kind}_engravings")
    locks = getattr(inv, f"{kind}_engraving_locks")
    if locks[slot]:
        return False, "locked slot"
    cost = (1, 4, 9)[sum(1 for idx, locked in enumerate(locks) if idx != slot and locked)]
    item_id = stone_item_id(kind, tier)
    if inv.items.get(item_id, 0) < cost:
        return False, f"not enough stones ({cost})"
    excluded = [row["option"] for idx, row in enumerate(rows) if idx != slot and row]
    rolled = roll_engraving(kind, tier, excluded)
    inv.remove_item(item_id, cost)
    rows[slot] = rolled
    return True, rolled


def toggle_lock(inv, kind, slot):
    if kind not in ("relic", "armor") or slot not in range(3):
        return False
    rows = getattr(inv, f"{kind}_engravings")
    locks = getattr(inv, f"{kind}_engraving_locks")
    if rows[slot] is None:
        return False
    locks[slot] = not locks[slot]
    return True


def add_gem(inv, gem_type, level, count=1):
    if gem_type not in GEM_TYPES or level not in range(1, 7) or count < 1:
        raise ValueError("direct gem drops must be level 1-6")
    inv.gems[gem_type][str(level)] += count


def synthesize_gem(inv, gem_type, level):
    if gem_type not in GEM_TYPES or level not in range(1, 10):
        return False
    if inv.gems[gem_type].get(str(level), 0) < 2:
        return False
    inv.gems[gem_type][str(level)] -= 2
    inv.gems[gem_type][str(level + 1)] += 1
    return True


def equip_gem(inv, gem_type, level):
    if gem_type not in GEM_TYPES or level not in range(1, 11):
        return False
    if inv.gems[gem_type].get(str(level), 0) < 1:
        return False
    inv.equipped_gems[gem_type] = level
    return True


def stat_bonus(inv):
    result = {key: 0 for key in GEM_TYPES}
    for rows in (inv.relic_engravings, inv.armor_engravings):
        for row in rows:
            if row and row["option"] in result:
                result[row["option"]] += row["value"]
    for gem_type, level in inv.equipped_gems.items():
        if level:
            result[gem_type] += GEM_VALUES[gem_type][level - 1]
    return result


def highest_unlocked_tier(pet):
    clears = getattr(pet, "raid_clears", {}) or {}
    highest = 1
    for tier in range(2, 5):
        previous = clears.get(str(tier - 1), clears.get(tier - 1, []))
        if len(set(previous)) >= 4:
            highest = tier
    return highest


def drop_decay(current_tier, played_tier):
    return (1.0, 0.5, 0.2, 0.05)[min(3, max(0, current_tier - played_tier))]


def roll_stone_drop(inv, pet, kind, tier):
    tier = max(1, min(4, tier))
    if random.random() > drop_decay(highest_unlocked_tier(pet), tier):
        return None
    item_id = stone_item_id(kind, tier)
    inv.add_item(item_id, 1)
    return item_id


def roll_gem_drop(inv, tier):
    tier = max(1, min(5, tier))
    table = {
        1: ([1, 2], [90, 10]), 2: ([2, 3], [85, 15]),
        3: ([3, 4], [65, 35]), 4: ([4, 5], [70, 30]),
        5: ([5, 6], [75, 25]),
    }
    levels, weights = table[tier]
    level = random.choices(levels, weights=weights, k=1)[0]
    gem_type = random.choice(GEM_TYPES)
    add_gem(inv, gem_type, level)
    return gem_type, level


def stage_skill_profile(stage, role=""):
    stage = max(1, min(4, int(stage)))
    profile = {
        1: {"damage_mult": 1.00, "effect_mult": 1.00},
        2: {"damage_mult": 1.12, "effect_mult": 1.12},
        3: {"damage_mult": 1.25, "effect_mult": 1.25},
        4: {"damage_mult": 1.40, "effect_mult": 1.40},
    }[stage]
    if any(tag in role for tag in ("방어", "수호", "체력")):
        profile = {**profile, "damage_mult": 1.0 + (profile["damage_mult"] - 1.0) * 0.65}
    elif "스피드" in role:
        profile = {**profile, "damage_mult": 1.0 + (profile["damage_mult"] - 1.0) * 0.85}
    return profile
