"""
検出可能効果量(Minimum Detectable Effect)の評価。

`DATA_EXPANSION_PHASE.md`の完了条件⑨「Effect Sizeが検出可能な水準かを評価可能にする」の
実装。**改善策を探すためのスクリプトではなく、「そもそも改善を検出できるのか」を測る道具**。

【背景】
これまで測定できた最良の効果量は買い期待値Rで+0.02〜+0.06。一方、無改造EAの全体PFは
期間だけで0.76 / 1.16 / 1.17と動く。探している効果より物差しの震えが大きい状態では、
Foldを増やしても判定できない可能性がある。それをデータ収集の前に評価する。

【ノイズを2層に分けて扱う】
1. Fold内サンプリング誤差: 1 Fold の取引数 n に対する平均Rの標準誤差
2. Fold間（レジーム）分散: 真の効果量そのものが期間で変動する分

A/B は同一期間で実行するため(1)の期間差は相殺される。残るのは
「除外群と残存群の差」の推定誤差と、(2)の効果量自体のばらつき。

【フィルター型仮説の効果量の分解（H006型）】
A = B ∪ S （B=残存, S=除外）とすると、代数的に

    mean_R(B) - mean_R(A) = (|S| / |A|) x (mean_R(B) - mean_R(S))

すなわち **効果量 = 除外率 x 群間差**。効果を大きくするには除外率を上げるか
群間差を広げるしかなく、両者はトレードオフになる（除外率を上げると|S|の推定が
安定する代わりに取引機会が減る）。この構造を明示的に計算する。

【この道具が答えないこと】
- どの仮説を採用すべきか（判定はしない）
- 効果量を大きくする方法（それは探索であり、本フェーズでは凍結中）
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_mt4_trades import parse_trades_html  # noqa: E402

PIP_SIZE = 0.01
CONTRACT = 100000


def realized_r(t: dict) -> float | None:
    if not t.get("sl") or not t.get("open_price") or not t.get("lots"):
        return None
    stop_dist = abs(t["open_price"] - t["sl"]) / PIP_SIZE
    if stop_dist <= 0:
        return None
    pip_val = (PIP_SIZE * CONTRACT) / t["open_price"]
    risk = stop_dist * pip_val * t["lots"]
    return t["profit"] / risk if risk else None


def load_rs(path: str, direction: str = "buy") -> list[float]:
    out = []
    for t in parse_trades_html(path):
        if t.get("type") != direction or not t.get("close_time"):
            continue
        r = realized_r(t)
        if r is not None:
            out.append(r)
    return out


def mean(v):
    return sum(v) / len(v)


def sd(v):
    if len(v) < 2:
        return float("nan")
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def mde_single_fold(sigma: float, n: int, alpha=0.05, power=0.80) -> float:
    """1 Foldの平均Rについて、両側alpha・検出力powerで検出できる最小効果量。"""
    z_a = 1.959963985  # alpha=0.05 両側
    z_b = 0.841621234  # power=0.80
    return (z_a + z_b) * sigma / math.sqrt(n)


def mde_filter_design(sigma: float, n_total: int, removal_frac: float,
                      alpha=0.05, power=0.80) -> float:
    """フィルター型(A=B∪S)の設計で検出できる最小の【効果量】(mean_R(B)-mean_R(A))。

    群間差 d の標準誤差は sigma*sqrt(1/nB + 1/nS)。効果量 = removal_frac * d なので、
    検出可能な効果量 = removal_frac * (z_a+z_b) * sigma * sqrt(1/nB + 1/nS)。
    """
    z_a, z_b = 1.959963985, 0.841621234
    n_s = n_total * removal_frac
    n_b = n_total - n_s
    if n_s < 1 or n_b < 1:
        return float("nan")
    se_d = sigma * math.sqrt(1.0 / n_b + 1.0 / n_s)
    return removal_frac * (z_a + z_b) * se_d


def folds_needed(effect_mean: float, effect_sd: float, alpha=0.05, power=0.80) -> int:
    """Fold間で効果量がばらつく場合に、平均効果を0と区別するのに必要なFold数。"""
    if effect_mean == 0 or effect_sd <= 0:
        return -1
    z_a, z_b = 1.959963985, 0.841621234
    n = ((z_a + z_b) * effect_sd / abs(effect_mean)) ** 2
    return max(2, math.ceil(n))


def main():
    import argparse
    ap = argparse.ArgumentParser(description="検出可能効果量の評価(Data Expansion Phase 完了条件9)")
    ap.add_argument("--pair", action="append", default=[],
                    help="fold名:年数:A_report.htm:B_report.htm を複数指定")
    ap.add_argument("--direction", default="buy")
    args = ap.parse_args()

    print("=" * 78)
    print("1. Fold内のRのばらつき（1トレードあたり）")
    print("=" * 78)
    print(f"{'fold':<10}{'arm':<4}{'n':>6}{'mean_R':>10}{'sd_R':>9}{'SE(mean)':>10}")

    folds = []
    for spec in args.pair:
        name, years, a_path, b_path = spec.split(":", 3)
        ra, rb = load_rs(a_path, args.direction), load_rs(b_path, args.direction)
        for arm, r in (("A", ra), ("B", rb)):
            print(f"{name:<10}{arm:<4}{len(r):>6}{mean(r):>10.4f}{sd(r):>9.4f}"
                  f"{sd(r)/math.sqrt(len(r)):>10.4f}")
        folds.append({"name": name, "A": ra, "B": rb, "years": float(years)})

    print()
    print("=" * 78)
    print("2. 効果量の分解:  効果量 = 除外率 x 群間差")
    print("=" * 78)
    print(f"{'fold':<10}{'nA':>5}{'nB':>5}{'除外率':>9}{'群間差':>10}{'効果量':>10}{'SE(効果)':>10}{'z':>7}")

    effects, effect_rows = [], []
    for f in folds:
        nA, nB = len(f["A"]), len(f["B"])
        nS = nA - nB
        if nS <= 0:
            continue
        frac = nS / nA
        eff = mean(f["B"]) - mean(f["A"])
        gap = eff / frac if frac else float("nan")
        sigma = sd(f["A"])
        se = frac * sigma * math.sqrt(1.0 / nB + 1.0 / nS)
        effects.append(eff)
        effect_rows.append({"name": f["name"], "eff": eff, "se": se,
                            "rate_per_year": nA / f["years"] if f.get("years") else None})
        print(f"{f['name']:<10}{nA:>5}{nB:>5}{frac*100:>8.1f}%{gap:>10.4f}"
              f"{eff:>10.4f}{se:>10.4f}{eff/se:>7.2f}")

    print()
    print("=" * 78)
    print("3. Foldをまたいだ効果量の合成（逆分散加重）")
    print("=" * 78)
    print("注意: 各Foldの効果量は SE=0.09〜0.26 と大きい。それらの観測値の散らばり(sd)を")
    print("      そのまま『Fold間分散』として使うと、Fold内誤差を無視した過大評価になる。")
    print("      ここでは各推定値をSEで重み付けして合成する。\n")
    if effect_rows:
        w = [1.0 / (e["se"] ** 2) for e in effect_rows]
        wm = sum(x["eff"] * wi for x, wi in zip(effect_rows, w)) / sum(w)
        wse = 1.0 / math.sqrt(sum(w))
        z = wm / wse
        p = math.erfc(abs(z) / math.sqrt(2))
        print(f"観測された効果量: {[round(e['eff'],4) for e in effect_rows]}")
        print(f"各FoldのSE       : {[round(e['se'],4) for e in effect_rows]}")
        print(f"\n逆分散加重平均 = {wm:.4f}   SE = {wse:.4f}   z = {z:.2f}   p = {p:.3f}")
        if p >= 0.05:
            print(f"→ **3Fold合計でも、効果は0と区別できない**（p={p:.3f}）")
        naive_sd = sd(effects)
        print(f"\n（参考）観測値のsd = {naive_sd:.4f} は、最小のFold内SE {min(e['se'] for e in effect_rows):.4f}")
        print("        よりも小さい。独立な推定値であればこれは起こりにくく、3点の一致は")
        print("        再現性の証拠ではなく偶然と解釈するのが妥当。")

    print()
    print("=" * 78)
    print("4. 検出可能効果量（MDE）: 買い取引数 x 除外率")
    print("=" * 78)
    sigma_ref = sd(folds[0]["A"]) if folds else 1.0
    print(f"（σ_R = {sigma_ref:.4f}、α=0.05、検出力0.80。単位は期待値R）\n")
    print(f"{'買い取引数':>10}" + "".join(f"{f'除外{int(p*100)}%':>11}" for p in (0.2, 0.35, 0.5, 0.7)))
    for n in (50, 100, 200, 400, 800, 1600, 3200, 6400):
        row = f"{n:>10}"
        for p in (0.2, 0.35, 0.5, 0.7):
            row += f"{mde_filter_design(sigma_ref, n, p):>11.4f}"
        print(row)

    print()
    print("=" * 78)
    print("5. 逆算: 観測された効果量を検出するのに必要なデータ量")
    print("=" * 78)
    if effect_rows:
        rates = [e["rate_per_year"] for e in effect_rows if e.get("rate_per_year")]
        rate = mean(rates) if rates else float("nan")
        print(f"実測の買い取引発生率: {[round(r) for r in rates]} 件/年 → 平均 {rate:.0f} 件/年\n")
        print(f"{'目標効果量':>10}{'除外率':>9}{'必要買い取引数':>15}{'必要年数':>10}")
        for target in (0.0461, 0.05, 0.08, 0.10, 0.15):
            for frac in (0.369,):
                k = frac * (1.959963985 + 0.841621234) * sigma_ref * \
                    math.sqrt(1.0 / (1 - frac) + 1.0 / frac)
                n_need = (k / target) ** 2
                print(f"{target:>10.4f}{frac*100:>8.1f}%{n_need:>15.0f}{n_need/rate:>10.1f}")
        print()
        n10 = rate * 10
        k = 0.369 * (1.959963985 + 0.841621234) * sigma_ref * \
            math.sqrt(1.0 / (1 - 0.369) + 1.0 / 0.369)
        print(f"逆に、10年分（買い約{n10:.0f}件）で検出できる最小効果量 = "
              f"**+{k/math.sqrt(n10):.4f} R**")


if __name__ == "__main__":
    main()
