"""
Simple script to:
 - read files matching comm.job.o* (or a provided glob pattern),
 - extract lines in the format: n, time(sec), RATE(MB/SEC)
 - save a CSV sorted by n
 - generate a single PNG containing both plots (time vs n and rate vs n)

Usage example:
  python3 plot_result.py --pattern "comm.job.o*" --out comm_results.csv

Generates: comm_results.csv and time_and_rate.png by default.
"""
import re
import glob
import argparse
import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Regular expression to match lines like: 1024, 0.000001669, 1170.285714
LINE_RE = re.compile(r'^\s*(\d+)\s*,\s*([0-9.eE+-]+)\s*,\s*([0-9.eE+-]+)\s*$')

def parse_files(pattern):
    """
    Parse all files matching the given glob pattern and collect rows.
    Returns a pandas DataFrame with columns: n, time_s, rate_mb_s, source.
    """
    rows = []
    files = sorted(glob.glob(pattern))
    for f in files:
        try:
            with open(f, 'r') as fh:
                for ln in fh:
                    m = LINE_RE.match(ln)
                    if m:
                        n = int(m.group(1))
                        time_s = float(m.group(2))
                        rate = float(m.group(3))
                        rows.append({'n': n, 'time_s': time_s, 'rate_mb_s': rate, 'source': os.path.basename(f)})
        except Exception:
            # ignore unreadable files
            continue
    return pd.DataFrame(rows)

def save_csv(df, out_path):
    """
    Save the DataFrame sorted by 'n' to CSV and return the sorted DataFrame.
    """
    df_sorted = df.sort_values('n').reset_index(drop=True)
    df_sorted.to_csv(out_path, index=False)
    return df_sorted

def plot_both(df, out_png):
    """
    Create a single PNG with two subplots (time vs n on top, rate vs n below).
    X-axis is log-scaled base 2 (n in bytes).
    """
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax_time, ax_rate = axs

    # Time plot (top)
    ax_time.plot(df['n'], df['time_s'], marker='o', linestyle='-', color='tab:blue')
    ax_time.set_xscale('log', base=2)
    ax_time.set_ylabel('Time (s)')
    ax_time.set_title('Time vs n')
    ax_time.grid(True, which='both', ls='--', lw=0.5)

    # Rate plot (bottom)
    ax_rate.plot(df['n'], df['rate_mb_s'], marker='o', linestyle='-', color='tab:green')
    ax_rate.set_xscale('log', base=2)
    ax_rate.set_xlabel('n (bytes)')
    ax_rate.set_ylabel('Rate (MB/s)')
    ax_rate.set_title('Bandwidth (RATE) vs n')
    ax_rate.grid(True, which='both', ls='--', lw=0.5)

    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)

def main():
    p = argparse.ArgumentParser(description='Parse comm.job.o* and plot results')
    p.add_argument('--pattern', default='comm.job.o*', help='glob pattern for input files')
    p.add_argument('--out', default='comm_results.csv', help='output CSV file')
    p.add_argument('--plot', default='time_and_rate.png', help='output PNG containing both plots')
    args = p.parse_args()

    df = parse_files(args.pattern)
    if df.empty:
        print('No matching lines found. Check the glob pattern or file format.')
        return

    df_sorted = save_csv(df[['n','time_s','rate_mb_s']].drop_duplicates(subset=['n','time_s','rate_mb_s']), args.out)
    plot_both(df_sorted, args.plot)

    print(f'CSV saved: {Path(args.out).absolute()}')
    print(f'Combined plot saved: {Path(args.plot).absolute()}')

if __name__ == '__main__':
    main()