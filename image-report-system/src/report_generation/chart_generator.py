"""Matplotlib-based chart generation for Word report embedding."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from ..pipeline import DetectedDefect

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def defect_type_pie_chart(defects: list[DetectedDefect], output_path: str | Path) -> str:
    """Generate a pie chart of defect type distribution."""
    output_path = Path(output_path)
    if not defects:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "无缺陷检出", ha="center", va="center", fontsize=14, color="#666")
        ax.set_axis_off()
        fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return str(output_path)

    from collections import Counter
    counts = Counter(d.defect_type.value for d in defects)
    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = ["#fdcb6e", "#e17055", "#0984e3", "#00b894", "#b2bec3"]

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%", colors=colors[:len(labels)],
        startangle=90, textprops={"fontsize": 10},
    )
    ax.set_title("缺陷类型分布", fontsize=13, fontweight="bold", pad=12)
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(output_path)


def defect_area_histogram(defects: list[DetectedDefect], output_path: str | Path) -> str:
    """Generate a histogram of defect areas."""
    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(5, 3.5))

    if not defects:
        ax.text(0.5, 0.5, "无缺陷检出", ha="center", va="center", fontsize=14, color="#666")
        ax.set_axis_off()
    else:
        areas = [d.area_px for d in defects]
        ax.hist(areas, bins=min(20, max(5, len(areas))), color="#0984e3", edgecolor="white", alpha=0.85)
        ax.set_xlabel("缺陷面积（像素）", fontsize=10)
        ax.set_ylabel("数量", fontsize=10)
        ax.set_title("缺陷面积分布", fontsize=13, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(output_path)


def severity_bar_chart(defects: list[DetectedDefect], output_path: str | Path) -> str:
    """Generate a bar chart of severity distribution."""
    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(4, 3))

    if not defects:
        ax.text(0.5, 0.5, "无缺陷检出", ha="center", va="center", fontsize=14, color="#666")
        ax.set_axis_off()
    else:
        from collections import Counter
        counts = Counter(d.severity.value for d in defects)
        categories = ["轻微", "中等", "严重"]
        values = [counts.get(c, 0) for c in categories]
        colors = ["#00b894", "#fdcb6e", "#e17055"]
        bars = ax.bar(categories, values, color=colors, edgecolor="white")
        ax.set_ylabel("数量", fontsize=10)
        ax.set_title("缺陷严重度分布", fontsize=13, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                        str(val), ha="center", fontsize=10, fontweight="bold")

    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(output_path)
