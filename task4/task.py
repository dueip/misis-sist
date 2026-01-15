import json
from typing import List, Dict, Tuple
import numpy as np

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def membership(x: float, points: List[Tuple[float, float]]) -> float:
    points = sorted(points, key=lambda p: p[0])

    if len(points) < 2:
        return 0.0

    if x <= points[0][0]:
        return points[0][1]

    if x >= points[-1][0]:
        return points[-1][1]

    for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
        if x1 <= x <= x2:
            if x1 == x2:
                return max(y1, y2)
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

    return 0.0


def fuzzify(value: float, terms: List[dict]) -> Dict[str, float]:
    fuzzy = {}
    for term in terms:
        fuzzy[term["id"]] = membership(value, term["points"])
    return fuzzy


def aggregate_output(
    fuzzy_input: Dict[str, float],
    rules: List[List[str]],
    output_terms: List[dict],
    x_values: np.ndarray
) -> np.ndarray:

    term_by_id = {t["id"]: t for t in output_terms}
    mu_agg = np.zeros_like(x_values, dtype=float)

    for input_id, output_id in rules:
        activation = fuzzy_input.get(input_id, 0.0)
        if activation <= 0:
            continue

        term = term_by_id.get(output_id)
        if not term:
            continue

        mu_term = np.array(
            [membership(x, term["points"]) for x in x_values]
        )

        mu_agg = np.maximum(mu_agg, np.minimum(mu_term, activation))

    return mu_agg


def defuzzify_mean_of_max(
    x_values: np.ndarray,
    mu: np.ndarray
) -> float:

    if mu.size == 0:
        return 0.0

    max_mu = np.max(mu)
    if max_mu == 0:
        return 0.0

    idx = np.where(np.isclose(mu, max_mu))[0]
    return float((x_values[idx[0]] + x_values[idx[-1]]) / 2)



def load_rules(path: str) -> List[List[str]]:
    data = load_json(path)
    rules: List[List[str]] = []
    for r in data:
            rules.append(r)
    return rules


def main(
    lvinput_path: str = "lvinput.json",
    lvoutput_path: str = "lvoutput.json",
    rules_path: str = "rules.json",
    temperature: float = 19.0
) -> float:
  

    lvinput = load_json(lvinput_path)
    lvoutput = load_json(lvoutput_path)
    rules = load_rules(rules_path)

    temp_terms = lvinput["температура"]
    heat_terms = lvoutput["нагрев"]

    fuzzy_temp = fuzzify(temperature, temp_terms)

    all_x = [x for term in heat_terms for x, _ in term["points"]]
    x_min, x_max = min(all_x), max(all_x)
    x_values = np.linspace(x_min, x_max, 2000)

    mu_out = aggregate_output(
        fuzzy_temp,
        rules,
        heat_terms,
        x_values
    )

    return defuzzify_mean_of_max(x_values, mu_out)


if __name__ == "__main__":
    for T in [15, 19, 22, 25, 30]:
        u = main(temperature=T)
        print(f"Температура {T:>5.1f}°C → управление {u:.2f}")
