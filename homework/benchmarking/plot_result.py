#!/usr/bin/env python3
"""
plot_result.py

Reads MPI benchmark output files (comm.job.o*) containing lines like:
  n, time(sec), RATE(MB/SEC)

Generates:
 - a CSV file sorted by n
 - a PNG with two plots (linear and log-scaled X axis)

Usage:
  python3 plot_result.py --pattern "comm.job.o*" --out results.csv
"""

import re
import glob
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Match lines like: 1024, 0.000001669, 1170.285714
LINE_RE = re.compile(r'^\s*(\d+)\s*,\s*([0-9.eE+-]+)\s*,\s*([0-9.eE+-]+)\s*$')

def parse_files(pattern):
    """Parse all matching files and return a DataFrame."""
    rows = []
    for f in sorted(glob.glob(pattern)):
        with open(f, 'r') as fh:
            for line in fh:
                m = LINE_RE.match(line)
                if m:
                    rows.append({
                        'n': int(m.group(1)),
                        'time_sec': float(m.group(2)),
                        'rate_MB_s': float(m.group(3)),
                        'source': Path(f).name
                    })
    return pd.DataFrame(rows)

def save_csv(df, out_path):
    """Save sorted data to CSV."""
    df_sorted = df.sort_values('n').reset_index(drop=True)
    df_sorted.to_csv(out_path, index=False)
    return df_sorted

def plot_linear_and_log(df, out_png):
    """Plot Rate vs n both linear and log-scaled."""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    ax_lin, ax_log = axs

    # Linear scale
    ax_lin.plot(df['n'], df['rate_MB_s'], marker='o', linestyle='-', color='tab:blue')
    ax_lin.set_xlabel('Message size n (bytes)')
    ax_lin.set_ylabel('Rate (MB/sec)')
    ax_lin.set_title('Rate vs n (Linear scale)')
    ax_lin.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Logarithmic scale (base 2)
    ax_log.plot(df['n'], df['rate_MB_s'], marker='o', linestyle='-', color='tab:orange')
    ax_log.set_xscale('log', base=2)
    ax_log.set_xlabel('Message size n (bytes)')
    ax_log.set_ylabel('Rate (MB/sec)')
    ax_log.set_title('Rate vs n (Log2 scale)')
    ax_log.grid(True, which='both', linestyle='--', linewidth=0.5)

    fig.suptitle('Ping-Pong Bandwidth (2 MPI Processes)', fontsize=14)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_png, dpi=150)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Parse comm.job.o* and plot MPI bandwidth")
    parser.add_argument('--pattern', default='comm.job.o*', help='Glob pattern for input files')
    parser.add_argument('--out', default='results.csv', help='Output CSV filename')
    parser.add_argument('--plot', default='pingpong_plot.png', help='Output PNG filename')
    args = parser.parse_args()

    df = parse_files(args.pattern)
    if df.empty:
        print("No matching data found.")
        return

    df_sorted = save_csv(df, args.out)
    plot_linear_and_log(df_sorted, args.plot)

    print(f"\n✅ CSV saved at: {Path(args.out).resolve()}")
    print(f"✅ Plot saved at: {Path(args.plot).resolve()}\n")

if __name__ == '__main__':
    main()
