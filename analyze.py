import csv
import os
from collections import Counter, defaultdict
from pathlib import Path

OUTPUT_DIR = "analysis"

def _to_bool(v):
    s = (v or "").strip().lower()
    return s in {"true", "1", "yes", "y", "t"}


def _safe_float(v, default = 0.0):
    try:
        return float(v)
    except Exception:
        return default

def analyze_results(results_file):
    with open(results_file, "r") as f:
        reader = csv.DictReader(f)
        results = list(reader)

    # write plots + summary for the presentation.
    if results:
        generate_charts(results, results_file=results_file, output_dir=OUTPUT_DIR)

    return results

def _overall_preserved_rate(rows):
    vals = [_to_bool(r.get("meaning_preserved", "")) for r in rows]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)

def _rate_by_condition(rows):
    grouped = defaultdict(list)
    for r in rows:
        cond = (r.get("condition") or "").strip() or "unknown"
        grouped[cond].append(r)
    out = []
    for cond, rs in grouped.items():
        out.append((cond, _overall_preserved_rate(rs), len(rs)))
    out.sort(key=lambda x: x[0])
    return out

def generate_charts(
    rows,
    *,
    results_file: str,
    output_dir: str = OUTPUT_DIR,
):
    out_root = Path(output_dir)
    charts_dir = out_root / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # matplotlib tries to write caches under $HOME by default; keep it inside the repo
    mpl_config = out_root / ".matplotlib"
    mpl_config.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

    # local import keeps runtime light if you only want CSV reading
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402

    total = len(rows)
    preserved_rate = _overall_preserved_rate(rows)

    # 1) overall meaning preserved (bar chart)
    plt.figure(figsize=(5, 4))
    plt.bar(["meaning_preserved"], [preserved_rate])
    plt.ylim(0, 1)
    plt.ylabel("Rate")
    plt.title("Meaning Preserved Rate (Overall)")
    plt.tight_layout()
    plt.savefig(charts_dir / "meaning_preserved_overall.png", dpi=200)
    plt.close()

    # 2) effect of context on meaning preservation (bar chart)
    by_cond = _rate_by_condition(rows)
    if len(by_cond) >= 2 or (len(by_cond) == 1 and by_cond[0][0] != "unknown"):
        labels = [c for (c, _, _) in by_cond]
        rates = [r for (_, r, _) in by_cond]
        plt.figure(figsize=(6, 4))
        plt.bar(labels, rates)
        plt.ylim(0, 1)
        plt.ylabel("Preservation rate")
        plt.title("Effect of context on meaning preservation")
        plt.tight_layout()
        plt.savefig(charts_dir / "effect_of_context_on_meaning_preservation.png", dpi=200)
        plt.close()

    # 3) failure type distribution (excluding 'none' where preserved) (bar chart)
    failure_types = []
    for r in rows:
        ft = (r.get("failure_type") or "").strip() or "unknown"
        mp = _to_bool(r.get("meaning_preserved", ""))
        if mp and ft == "none":
            continue
        failure_types.append(ft)
    ft_counts = Counter(failure_types)
    if ft_counts:
        items = sorted(ft_counts.items(), key=lambda x: (-x[1], x[0]))
        labels = [k for (k, _) in items]
        counts = [v for (_, v) in items]
        plt.figure(figsize=(7, max(3.5, 0.35 * len(labels))))
        plt.barh(labels, counts)
        plt.xlabel("Count")
        plt.title("Failure Type Distribution")
        plt.tight_layout()
        plt.savefig(charts_dir / "failure_type_distribution.png", dpi=200)
        plt.close()

    # summary text file
    lines = []
    lines.append(f"Results file: {results_file}")
    lines.append(f"Total rows: {total}")
    lines.append(f"Meaning preserved rate (overall): {preserved_rate:.3f}")

    # condition stats (if present)
    if by_cond:
        lines.append("")
        lines.append("Effect of context on meaning preservation:")
        for cond, rate, n in by_cond:
            lines.append(f"- {cond}: {rate:.3f} (n={n})")

    # failure types
    if ft_counts:
        lines.append("")
        lines.append("Failure types (excluding preserved/none):")
        for k, v in sorted(ft_counts.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- {k}: {v}")

    (out_root / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    analyze_results("data/results.csv")