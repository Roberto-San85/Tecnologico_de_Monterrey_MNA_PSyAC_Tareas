#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
compute_statistics.py

Reads one or more files containing numbers (one per line),
computes descriptive statistics using only basic algorithms,
prints per-file results to the screen, and writes them to StatisticsResults.txt.

Statistics computed per file:
- Mean
- Median
- Mode
- Standard Deviation
- Variance

Invalid lines are skipped but reported in the console.
Missing files are reported and the program continues.
Execution time (overall) is measured and reported at the end.
"""

import sys
import time
from typing import List, Tuple, Union


def compute_mean(data: List[float]) -> float:
    """Return the arithmetic mean of a non-empty list of numbers."""
    return sum(data) / len(data)


def compute_median(data: List[float]) -> float:
    """Return the median value of a non-empty list of numbers."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2

    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    return sorted_data[mid]


def compute_mode(data: List[float]) -> Union[float, List[float]]:
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


def compute_variance(data: List[float], mean: float) -> float:
    """Return the population variance given data and its mean."""
    total = 0.0
    for num in data:
        total += (num - mean) ** 2
    return total / len(data)


def compute_std_dev(variance: float) -> float:
    """Return the standard deviation (square root of variance)."""
    return variance ** 0.5


def read_file(filename: str) -> Tuple[List[float], int]:
    """
    Read numeric values from a text file (one per line).
    Lines that cannot be parsed as float are reported and ignored.
    Returns a tuple: (list_of_numbers, invalid_count).
    """
    numbers: List[float] = []
    invalid = 0

    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                numbers.append(float(text))
            except ValueError:
                invalid += 1
                print(
                    f"[ERROR] Invalid data at line {line_number} in '{filename}': "
                    f"'{text}' (ignored)"
                )
    return numbers, invalid


def format_stats_block(
    title: str,
    data: List[float],
    invalid_count: int,
) -> str:
    """
    Build a formatted text block with statistics for a single file.
    Assumes 'data' is not empty.
    """
    mean = compute_mean(data)
    median = compute_median(data)
    mode = compute_mode(data)
    variance = compute_variance(data, mean)
    std_dev = compute_std_dev(variance)

    block = (
        f"===== {title} =====\n"
        f"Total numbers processed: {len(data)}\n"
        f"Invalid lines ignored: {invalid_count}\n"
        f"Mean: {mean}\n"
        f"Median: {median}\n"
        f"Mode: {mode}\n"
        f"Variance: {variance}\n"
        f"Standard Deviation: {std_dev}\n"
        "==============================\n"
    )
    return block


def write_results(text: str) -> None:
    """Write the provided text to 'StatisticsResults.txt' using UTF-8 encoding."""
    with open("StatisticsResults.txt", "w", encoding="utf-8") as file:
        file.write(text)


def main() -> None:
    """
    Entry point: parse args, accept one or more files, compute stats per file,
    print and persist results, and report total execution time.
    """
    if len(sys.argv) < 2:
        print("Usage: python compute_statistics.py <file1> [file2 file3 ...]")
        sys.exit(1)

    start_time = time.time()

    filenames = sys.argv[1:]
    any_success = False
    output_blocks: List[str] = []

    for fname in filenames:
        try:
            data, invalid_count = read_file(fname)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {fname} (skipped)")
            continue
        except PermissionError:
            print(f"[ERROR] Permission denied: {fname} (skipped)")
            continue
        except OSError as exc:
            print(f"[ERROR] Could not read '{fname}': {exc} (skipped)")
            continue

        if not data:
            print(f"[WARN] No valid numeric data found in '{fname}'.")
            # Still create a minimal block to reflect the attempt
            block = (
                f"===== File: {fname} =====\n"
                f"Total numbers processed: 0\n"
                f"Invalid lines ignored: {invalid_count}\n"
                "No statistics computed (empty dataset)\n"
                "==============================\n"
            )
            print(block, end="")
            output_blocks.append(block)
            # do not set any_success to True here (no stats)
            continue

        # We have valid data; compute stats and print/store
        block = format_stats_block(f"File: {fname}", data, invalid_count)
        print(block, end="")
        output_blocks.append(block)
        any_success = True

    elapsed = time.time() - start_time
    footer = f"\nOverall Execution Time: {elapsed:.6f} seconds\n"
    print(footer)
    output_blocks.append(footer)

    # Persist results if we processed at least one file (even if empty)
    write_results("".join(output_blocks))

    if not any_success:
        # No file produced statistics (all missing or empty)
        # We still wrote a results file with warnings/footers.
        sys.exit(1)


if __name__ == "__main__":
    main()
