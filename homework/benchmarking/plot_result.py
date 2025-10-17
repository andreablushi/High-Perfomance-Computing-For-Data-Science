#!/usr/bin/env python
"""
plot_result_from_jobs.py - No external dependencies version
Outputs data in a format that can be plotted manually or with basic tools
"""

import os
import glob

# Define paths
base_dir = "./High-Perfomance-Computing-For-Data-Science/benchmarking"
output_file = os.path.join(base_dir, "benchmark_results.txt")
plot_script_file = os.path.join(base_dir, "create_plot.gnuplot")

# Find all job output files
job_files = glob.glob(os.path.join(base_dir, "comm.job.o*"))
if not job_files:
    print("No job output files found in {}".format(base_dir))
    exit(1)

# Initialize empty lists
n_values = []
rates = []
times = []

# Process each job file
for file in job_files:
    print("Processing file: {}".format(file))
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip header lines and empty lines
            if not line or line.startswith('#') or 'n,' in line or 'time(sec),' in line:
                continue
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    n_val = int(parts[0].strip())
                    time_val = float(parts[1].strip())
                    rate_val = float(parts[2].strip())
                    n_values.append(n_val)
                    times.append(time_val)
                    rates.append(rate_val)
                    print("  n={}, time={}, rate={}".format(n_val, time_val, rate_val))
                except ValueError as e:
                    print("  Warning: Could not parse line: {} - {}".format(line, e))
                    continue

if not n_values:
    print("No valid data found in job files.")
    exit(1)

# Combine and sort data
data = list(zip(n_values, rates, times))
data.sort(key=lambda x: x[0])  # Sort by n

# Write results to file
with open(output_file, 'w') as f:
    f.write("# n(bytes)\tRate(MB/s)\tTime(sec)\n")
    for n, rate, time in data:
        f.write("{}\t{:.3f}\t{:.6f}\n".format(n, rate, time))

print("Data written to {}".format(output_file))

# Create gnuplot script
gnuplot_script = """
set terminal png size 800,600
set output 'pingpong_plot.png'
set xlabel 'Message size (bytes)'
set ylabel 'Rate (MB/s)'
set logscale x 2
set grid
set title 'MPI Ping-Pong Benchmark'
plot 'benchmark_results.txt' using 1:2 with linespoints title 'Rate (MB/s)'
"""

with open(plot_script_file, 'w') as f:
    f.write(gnuplot_script)

print("Gnuplot script created at {}".format(plot_script_file))

# Print summary and instructions
print("\n" + "="*50)
print("BENCHMARK SUMMARY")
print("="*50)

# Find statistics
max_rate = max(rates)
min_rate = min(rates)
max_rate_n = n_values[rates.index(max_rate)]
min_rate_n = n_values[rates.index(min_rate)]

print("Total data points: {}".format(len(data)))
print("Message size range: {} - {} bytes".format(min(n_values), max(n_values)))
print("Max rate: {:.2f} MB/s at {} bytes".format(max_rate, max_rate_n))
print("Min rate: {:.2f} MB/s at {} bytes".format(min_rate, min_rate_n))
print("\nData file: {}".format(output_file))
print("To create plot, run: gnuplot {}".format(plot_script_file))
print("\nRaw data:")
print("n(bytes)\tRate(MB/s)\tTime(sec)")
print("-" * 40)
for n, rate, time in data:
    print("{:8d}\t{:10.2f}\t{:10.6f}".format(n, rate, time))