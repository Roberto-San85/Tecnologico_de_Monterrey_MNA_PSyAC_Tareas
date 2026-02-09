#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
wordCount.py

Reads one or more text files and counts the frequency of each distinct word,
using basic algorithms only (manual tokenization and counting). Results for
each file are printed to the console and also written to WordCountResults.txt.

Rules:
- Words are case-insensitive (converted to lowercase).
- Allowed characters in words: ASCII letters and digits (a–z, A–Z, 0–9).
- All other characters are treated as separators and removed.
- Empty tokens after cleaning are ignored and reported as invalid when present.

Invalid tokens are reported (with line numbers) but do not stop execution.
Missing or unreadable files are reported and skipped.
Overall execution time is displayed and stored.

Complies with PEP8/pylint (snake_case, docstrings, explicit encodings).
"""

from __future__ import annotations

import sys
import time
from typing import Dict, List, Tuple


def is_alnum_ascii(char: str) -> bool:
    """
    Return True if the character is an ASCII letter or digit.
    Only 'a'-'z', 'A'-'Z', and '0'-'9' are considered valid.
    """
    return (
        ("a" <= char <= "z")
        or ("A" <= char <= "Z")
        or ("0" <= char <= "9")
    )


def clean_word(token: str) -> str:
    """
    Clean a raw token by keeping only ASCII letters and digits.
    Returns the lowercase word or an empty string if nothing remains.
    """
    cleaned_chars: List[str] = []
    for ch in token:
        if is_alnum_ascii(ch):
            cleaned_chars.append(ch.lower())
    return "".join(cleaned_chars)


def manual_split_by_spaces(line: str) -> List[str]:
    """
    Manually split a line by space characters into tokens without using str.split().
    Consecutive spaces are collapsed; leading/trailing spaces are ignored.
    """
    tokens: List[str] = []
    current = ""

    for ch in line:
        if ch == " ":
            if current != "":
                tokens.append(current)
                current = ""
        else:
            current += ch

    if current != "":
        tokens.append(current)

    return tokens


def read_words_from_file(filename: str) -> Tuple[List[str], int]:
    """
    Read words from a file, manually splitting each line into space-separated tokens
    and cleaning each token to keep only letters/digits. Returns (words, invalid_count).

    invalid_count includes tokens that result in an empty cleaned string (e.g., punctuation).
    """
    words: List[str] = []
    invalid_count = 0

    with open(filename, "r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                # Skip empty lines silently.
                continue

            raw_tokens = manual_split_by_spaces(line)

            # If line had no space-separated tokens (e.g., just spaces), continue.
            if not raw_tokens:
                continue

            for token in raw_tokens:
                cleaned = clean_word(token)
                if cleaned == "":
                    invalid_count += 1
                    print(
                        f"[ERROR] Invalid token at line {line_number} in '{filename}': "
                        f"'{token}' (ignored)"
                    )
                else:
                    words.append(cleaned)

    return words, invalid_count


def count_frequencies(words: List[str]) -> Dict[str, int]:
    """
    Manually count word frequencies using a basic dictionary algorithm.
    Returns a mapping word -> count.
    """
    freq: Dict[str, int] = {}
    for w in words:
        if w in freq:
            freq[w] += 1
        else:
            freq[w] = 1
    return freq


def format_wordcount_block(
    filename: str, words: List[str], invalid: int
) -> str:
    """
    Build a formatted text block that lists word frequencies for a single file.
    Words are presented in arbitrary dictionary iteration order.
    """
    header = (
        f"===== File: {filename} =====\n"
        f"Total words (after cleaning): {len(words)} | "
        f"Invalid tokens ignored: {invalid}\n"
    )

    if not words:
        # No valid words -> no frequency listing.
        return header + "No valid words found.\n==============================\n\n"

    frequencies = count_frequencies(words)

    lines: List[str] = [header]
    for word, count in frequencies.items():
        lines.append(f"{word}: {count}")

    lines.append("==============================\n")
    return "\n".join(lines)


def write_results_to_file(content: str) -> None:
    """Write the aggregated results to 'WordCountResults.txt' (UTF-8)."""
    with open("WordCountResults.txt", "w", encoding="utf-8") as handle:
        handle.write(content)


def main() -> None:
    """
    Entry point: accept one or more files, compute per-file word counts,
    print blocks to console, persist to WordCountResults.txt, and show total time.
    """
    if len(sys.argv) < 2:
        print("Usage: python word_count.py <file1> [file2 file3 ...]")
        sys.exit(1)

    start = time.time()
    output_blocks: List[str] = []
    any_processed = False

    for fname in sys.argv[1:]:
        try:
            words, invalid = read_words_from_file(fname)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {fname} (skipped)")
            continue
        except PermissionError:
            print(f"[ERROR] Permission denied: {fname} (skipped)")
            continue
        except OSError as exc:
            print(f"[ERROR] Could not read '{fname}': {exc} (skipped)")
            continue

        block = format_wordcount_block(fname, words, invalid)
        print(block, end="")
        output_blocks.append(block)
        any_processed = True

    elapsed = time.time() - start
    footer = f"\nOverall Execution Time: {elapsed:.6f} seconds\n"
    print(footer)
    output_blocks.append(footer)

    # Always create the results file for traceability.
    write_results_to_file("".join(output_blocks))

    # Exit non-zero if no file could be processed at all.
    if not any_processed:
        sys.exit(1)


if __name__ == "__main__":
    main()
