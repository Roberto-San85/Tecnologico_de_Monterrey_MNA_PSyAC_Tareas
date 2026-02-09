#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
convertNumbers.py

Reads one or more files containing non-negative integers (one per line) and
converts each value to binary and hexadecimal using manual algorithms
(no bin(), hex(), format(), or base tricks).

Invalid lines are reported and ignored. Missing files are reported and skipped.
Per-file results are printed to the console and also written to ConversionResults.txt.
Overall execution time is displayed and stored.

Complies with PEP8/pylint (snake_case, docstrings, explicit encodings).
"""

from __future__ import annotations

import sys
import time
from typing import List, Tuple


def decimal_to_binary(number: int) -> str:
    """
    Convert a non-negative integer to its binary representation
    using manual division-by-2, returning a string like '10101'.
    """
    if number == 0:
        return "0"

    bits: List[str] = []
    n = number
    while n > 0:
        remainder = n % 2
        bits.append("1" if remainder == 1 else "0")
        n //= 2

    bits.reverse()
    return "".join(bits)


def decimal_to_hexadecimal(number: int) -> str:
    """
    Convert a non-negative integer to its hexadecimal representation
    using manual division-by-16, returning uppercase hex digits.
    """
    if number == 0:
        return "0"

    hex_digits = "0123456789ABCDEF"
    digits: List[str] = []
    n = number
    while n > 0:
        remainder = n % 16
        digits.append(hex_digits[remainder])
        n //= 16

    digits.reverse()
    return "".join(digits)


def read_numbers_from_file(filename: str) -> Tuple[List[int], int]:
    """
    Read integers from a file (one per line). Only non-negative integers are valid.
    Returns (numbers, invalid_count).
    Lines that are empty, not integers, or negative are counted as invalid,
    reported to the console, and ignored.
    """
    numbers: List[int] = []
    invalid_count = 0

    with open(filename, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                # Ignore empty lines silently
                continue

            try:
                value = int(text)
                if value < 0:
                    raise ValueError("Negative value not allowed")
                numbers.append(value)
            except ValueError:
                invalid_count += 1
                print(
                    f"[ERROR] Invalid value at line {line_number} in '{filename}': "
                    f"'{text}' (ignored)"
                )

    return numbers, invalid_count


def format_conversion_block(filename: str, numbers: List[int], invalid: int) -> str:
    """
    Build and return a formatted text block for a single file that shows each
    decimal value with its binary and hexadecimal conversions.
    """
    header = (
        f"===== File: {filename} =====\n"
        f"Valid items: {len(numbers)} | Invalid lines ignored: {invalid}\n"
    )

    lines: List[str] = [header]
    for value in numbers:
        binary = decimal_to_binary(value)
        hexa = decimal_to_hexadecimal(value)
        lines.append(f"Decimal: {value} | Binary: {binary} | Hexadecimal: {hexa}")

    lines.append("==============================\n")
    return "\n".join(lines)


def write_results_to_file(content: str) -> None:
    """Write the aggregated results to 'ConversionResults.txt' (UTF-8)."""
    with open("ConversionResults.txt", "w", encoding="utf-8") as handle:
        handle.write(content)


def main() -> None:
    """
    Entry point: accept one or more input files, convert numbers for each file,
    print per-file conversions, persist all results, and show total elapsed time.
    """
    if len(sys.argv) < 2:
        print("Usage: python convert_numbers.py <file1> [file2 file3 ...]")
        sys.exit(1)

    start = time.time()
    results_blocks: List[str] = []
    any_processed = False

    for fname in sys.argv[1:]:
        try:
            numbers, invalid = read_numbers_from_file(fname)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {fname} (skipped)")
            continue
        except PermissionError:
            print(f"[ERROR] Permission denied: {fname} (skipped)")
            continue
        except OSError as exc:
            print(f"[ERROR] Could not read '{fname}': {exc} (skipped)")
            continue

        if not numbers and invalid == 0:
            # File existed but was empty or only whitespace.
            block = (
                f"===== File: {fname} =====\n"
                "No data found (empty file)\n"
                "==============================\n\n"
            )
            print(block, end="")
            results_blocks.append(block)
            # Considered processed, even if no conversions.
            any_processed = True
            continue

        block = format_conversion_block(fname, numbers, invalid)
        print(block, end="")
        results_blocks.append(block)
        any_processed = True

    elapsed = time.time() - start
    footer = f"\nOverall Execution Time: {elapsed:.6f} seconds\n"
    print(footer)
    results_blocks.append(footer)

    # Always write an output file for traceability.
    write_results_to_file("".join(results_blocks))

    # Exit non-zero if nothing could be processed at all.
    if not any_processed:
        sys.exit(1)


if __name__ == "__main__":
    main()
