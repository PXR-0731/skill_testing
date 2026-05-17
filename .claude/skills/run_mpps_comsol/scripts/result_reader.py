#!/usr/bin/env python3
"""
result_reader.py - 读取 COMSOL 仿真结果 (.txt) 并绘制吸声系数曲线

功能：
    1. 读取 comsol_runner.py 导出的频率-吸声系数 .txt 文件
    2. 解析数据并计算统计指标（峰值、平均吸声系数等）
    3. 绘制吸声系数频谱曲线图
    4. 将图表保存为图片文件

用法：
    python result_reader.py --result_file /path/to/absorption.txt --output_plot /path/to/plot.png
"""

import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 无头环境使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np


def parse_result_file(result_file: str) -> dict:
    """
    解析 COMSOL 导出的 .txt 结果文件。

    期望格式（制表符分隔，含表头）：
        freq[Hz]    absorption
        100         0.15
        125         0.22
        ...

    Returns:
        dict: {"frequencies": [...], "absorption": [...]}
    """
    if not os.path.exists(result_file):
        raise FileNotFoundError(f"结果文件不存在: {result_file}")

    # 尝试多种分隔符解析
    for sep in ["\t", ",", " ", ";"]:
        try:
            data = np.genfromtxt(result_file, delimiter=sep, skip_header=1, dtype=float)
            if data.ndim == 2 and data.shape[1] >= 2:
                return {
                    "frequencies": data[:, 0].tolist(),
                    "absorption": np.clip(data[:, 1], 0.0, 1.0).tolist()
                }
        except (ValueError, IndexError):
            continue

    # 若均失败，尝试手动解析
    frequencies, absorption = [], []
    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.lower().startswith("freq"):
                continue
            parts = line.replace(",", "\t").replace(" ", "\t").split("\t")
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                try:
                    frequencies.append(float(parts[0]))
                    absorption.append(float(parts[1]))
                except ValueError:
                    continue

    if not frequencies:
        raise ValueError(f"无法解析结果文件: {result_file}")

    return {
        "frequencies": frequencies,
        "absorption": [max(0.0, min(1.0, a)) for a in absorption]
    }


def compute_metrics(data: dict) -> dict:
    """计算吸声性能统计指标。"""
    freqs = np.array(data["frequencies"])
    absorp = np.array(data["absorption"])

    peak_idx = np.argmax(absorp)
    avg_100_5000 = np.mean(absorp[(freqs >= 100) & (freqs <= 5000)])

    return {
        "peak_absorption": float(absorp[peak_idx]),
        "peak_frequency": float(freqs[peak_idx]),
        "average_100_5000Hz": float(avg_100_5000),
        "frequency_range": [float(freqs[0]), float(freqs[-1])]
    }


def plot_absorption_curve(data: dict, output_path: str, metrics: dict = None):
    """
    绘制吸声系数频谱曲线并保存。

    Args:
        data: {"frequencies": [...], "absorption": [...]}
        output_path: 图片保存路径 (.png)
        metrics: 可选的统计指标字典，用于在图中标注
    """
    freqs = np.array(data["frequencies"])
    absorp = np.array(data["absorption"])

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    # 主曲线
    ax.plot(freqs, absorp, color="#2E86AB", linewidth=2.2, label="Absorption Coefficient")
    ax.fill_between(freqs, 0, absorp, alpha=0.15, color="#2E86AB")

    # 峰值标注
    if metrics:
        peak_freq = metrics["peak_frequency"]
        peak_abs = metrics["peak_absorption"]
        ax.axvline(x=peak_freq, color="#E94F37", linestyle="--", alpha=0.7, linewidth=1.2)
        ax.annotate(
            f"Peak: {peak_abs:.3f} @ {peak_freq:.0f} Hz",
            xy=(peak_freq, peak_abs),
            xytext=(peak_freq * 1.3, peak_abs - 0.08),
            fontsize=10,
            color="#E94F37",
            arrowprops=dict(arrowstyle="->", color="#E94F37", lw=1.2)
        )

    # 0.8 参考线
    ax.axhline(y=0.8, color="#888888", linestyle=":", alpha=0.6, linewidth=1)
    ax.text(freqs[-1] * 1.02, 0.8, "0.8", fontsize=9, color="#888888", va="center")

    # 坐标轴设置
    ax.set_xlabel("Frequency (Hz)", fontsize=12)
    ax.set_ylabel("Absorption Coefficient", fontsize=12)
    ax.set_title("Micro-Perforated Panel Absorption Spectrum", fontsize=14, pad=15)
    ax.set_xscale("log")
    ax.set_xlim([max(50, freqs[0]), freqs[-1]])
    ax.set_ylim([0, 1.05])
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(loc="lower right", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="读取 MPPS 仿真结果并绘制吸声曲线")
    parser.add_argument("--result_file", required=True, help="仿真结果 .txt 文件路径")
    parser.add_argument("--output_plot", default="absorption_curve.png", help="输出图片路径")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                        help="stdout 数据输出格式")
    args = parser.parse_args()

    try:
        # 解析数据
        data = parse_result_file(args.result_file)

        # 计算指标
        metrics = compute_metrics(data)

        # 绘图
        plot_absorption_curve(data, args.output_plot, metrics)

        # 构建输出
        result = {
            "status": "ok",
            "plot_path": os.path.abspath(args.output_plot),
            "metrics": metrics,
            "data": {
                "frequencies": data["frequencies"],
                "absorption_coefficients": data["absorption"]
            }
        }

        if args.format == "json":
            print(json.dumps(result, indent=2))
        elif args.format == "csv":
            print("frequency_hz,absorption")
            for f, a in zip(data["frequencies"], data["absorption"]):
                print(f"{f},{a}")

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
