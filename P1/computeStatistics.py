#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
compute_statistics.py

Reads a file containing numbers (one per line),
computes descriptive statistics using only basic algorithms,
prints results to the screen, and writes them to StatisticsResults.txt.

Statistics computed:
- Mean
- Median
- Mode
- Standard Deviation
- Variance

Invalid lines are skipped but reported in the console.
Execution time is measured and reported.
"""

import sys
import time


def compute_mean(data):
    """Return the arithmetic mean of a non-empty list of numbers."""
    return sum(data) / len(data)


def compute_median(data):
    """Return the median value of a non-empty list of numbers."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2

    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    return sorted_data[mid]


def compute_mode(data):
    """
    Return the mode of the list.
    If multiple modes exist, return a list of the modal values.
    """
    freq = {}
    for num in data:
        freq[num] = freq.get(num, 0) + 1

    max_count = max(freq.values())
    modes = [k for k, v in freq.items() if v == max_count]

    if len(modes) == 1:
        return modes[0]
    return modes


def compute_variance(data, mean):
    """Return the population variance given data and its mean."""
    total = 0.0
    for num in data:
        total += (num - mean) ** 2
    return total / len(data)


def compute_std_dev(variance):
    """Return the standard deviation (square root of variance)."""
    return variance ** 0.5


def read_file(filename):
    """
    Read numeric values from a text file (one per line).
    Lines that cannot be parsed as float are reported and ignored.
    Returns a list of floats.
    """
    numbers = []
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                numbers.append(float(text))
            except ValueError:
                print(
                    f"[ERROR] Invalid data at line {line_number}: '{text}' (ignored)"
                )
    return numbers


def write_results(text):
    """Write the provided text to 'StatisticsResults.txt' using UTF-8 encoding."""
    with open("StatisticsResults.txt", "w", encoding="utf-8") as file:
        file.write(text)


def main():
    """Entry point: parse args, compute statistics, print and persist results."""
    if len(sys.argv) != 2:
        print("Usage: python compute_statistics.py fileWithData.txt")
        sys.exit(1)

    filename = sys.argv[1]
    start_time = time.time()

    try:
        data = read_file(filename)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        sys.exit(1)

    if not data:
        print("No valid numeric data found.")
        sys.exit(1)

    # Compute statistics
    mean = compute_mean(data)
    median = compute_median(data)
    mode = compute_mode(data)
    variance = compute_variance(data, mean)
    std_dev = compute_std_dev(variance)

    elapsed = time.time() - start_time

    # Build results text
    result_text = (
        "===== Statistics Results =====\n"
        f"Total numbers processed: {len(data)}\n"
        f"Mean: {mean}\n"
        f"Median: {median}\n"
        f"Mode: {mode}\n"
        f"Variance: {variance}\n"
        f"Standard Deviation: {std_dev}\n"
        f"Execution Time: {elapsed:.6f} seconds\n"
        "==============================\n"
    )

    # Print to screen
    print(result_text)

    # Write to file
    write_results(result_text)


if __name__ == "__main__":
    main()
