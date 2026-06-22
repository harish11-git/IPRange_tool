#!/usr/bin/env python3
"""Convert CIDR IP ranges to XML address-pattern regex entries.

Usage:
    python cidr_to_regex.py -t <TICKET> <CIDR> [CIDR ...]
    python cidr_to_regex.py -t <TICKET> -f <file>
    python cidr_to_regex.py                              (interactive mode)

Examples:
    python cidr_to_regex.py -t MC-4093 37.186.33.0/24 37.186.34.0/24
    python cidr_to_regex.py -t MC-4093 -f cidrs.txt
"""

import sys
import ipaddress


def _char_range(lo, hi):
    """Regex fragment for a single-digit range."""
    if lo == hi:
        return str(lo)
    if lo == 0 and hi == 9:
        return r"\d"
    return f"[{lo}-{hi}]"


def _two_digit(lo, hi):
    """Regex alternatives for two-digit numbers [lo..hi] (10-99)."""
    lo_t, lo_u = divmod(lo, 10)
    hi_t, hi_u = divmod(hi, 10)

    if lo_t == hi_t:
        return [str(lo_t) + _char_range(lo_u, hi_u)]

    parts = []
    if lo_u > 0:
        parts.append(str(lo_t) + _char_range(lo_u, 9))
        lo_t += 1

    top = []
    if hi_u < 9:
        top.append(str(hi_t) + _char_range(0, hi_u))
        hi_t -= 1

    if lo_t <= hi_t:
        parts.append(_char_range(lo_t, hi_t) + r"\d")

    parts.extend(top)
    return parts


def _two_digit_padded(lo, hi):
    """Regex alternatives for 00-99 (last two digits inside a three-digit number)."""
    if lo == 0 and hi == 99:
        return [r"\d\d"]

    lo_t, lo_u = divmod(lo, 10)
    hi_t, hi_u = divmod(hi, 10)

    if lo_t == hi_t:
        return [str(lo_t) + _char_range(lo_u, hi_u)]

    parts = []
    if lo_u > 0:
        parts.append(str(lo_t) + _char_range(lo_u, 9))
        lo_t += 1

    top = []
    if hi_u < 9:
        top.append(str(hi_t) + _char_range(0, hi_u))
        hi_t -= 1

    if lo_t <= hi_t:
        parts.append(_char_range(lo_t, hi_t) + r"\d")

    parts.extend(top)
    return parts


def _three_digit(lo, hi):
    """Regex alternatives for three-digit numbers [lo..hi] (100-255)."""
    lo_h, lo_r = divmod(lo, 100)
    hi_h, hi_r = divmod(hi, 100)

    if lo_h == hi_h:
        return [str(lo_h) + p for p in _two_digit_padded(lo_r, hi_r)]

    parts = []
    if lo_r > 0:
        parts.extend(str(lo_h) + p for p in _two_digit_padded(lo_r, 99))
        lo_h += 1

    top = []
    if hi_r < 99:
        top.extend(str(hi_h) + p for p in _two_digit_padded(0, hi_r))
        hi_h -= 1

    if lo_h <= hi_h:
        if lo_h == hi_h:
            parts.append(str(lo_h) + r"\d\d")
        else:
            parts.append(f"[{lo_h}-{hi_h}]" + r"\d\d")

    parts.extend(top)
    return parts


def octet_regex(lo, hi):
    """Build a regex matching all integers in [lo..hi] (0 <= lo <= hi <= 255)."""
    if lo == hi:
        return str(lo)

    if lo == 0 and hi == 255:
        return r"([1-9]?\d|[12]\d\d)"

    parts = []

    if lo <= 9:
        parts.append(_char_range(lo, min(hi, 9)))

    if lo <= 99 and hi >= 10:
        parts.extend(_two_digit(max(lo, 10), min(hi, 99)))

    if hi >= 100:
        parts.extend(_three_digit(max(lo, 100), min(hi, 255)))

    if len(parts) == 1:
        return parts[0]
    return "(" + "|".join(parts) + ")"


def cidr_to_xml(cidr_str, ticket):
    """Convert a CIDR string to XML comment + address-pattern line."""
    network = ipaddress.ip_network(cidr_str.strip(), strict=False)
    first = str(network.network_address)
    last = str(network.broadcast_address)

    start = list(network.network_address.packed)
    end = list(network.broadcast_address.packed)

    octets = [octet_regex(start[i], end[i]) for i in range(4)]
    pattern = r"\.".join(octets)

    cidr_clean = cidr_str.strip()
    comment = f"<!--  Added via {ticket} Ip range: {cidr_clean}  IP Range First usable : {first} Last usable {last}  -->"
    address = f'<address pattern = "{pattern}$"/>'
    return f"{comment}\n{address}"


def main():
    ticket = "MC-4093"
    cidrs = []
    args = sys.argv[1:]

    i = 0
    file_path = None
    positional = []
    while i < len(args):
        if args[i] == "-t" and i + 1 < len(args):
            ticket = args[i + 1]
            i += 2
        elif args[i] == "-f" and i + 1 < len(args):
            file_path = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if file_path:
        with open(file_path) as f:
            cidrs = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    elif positional:
        cidrs = positional

    if cidrs:
        lines = []
        for cidr in cidrs:
            try:
                lines.append(cidr_to_xml(cidr, ticket))
            except ValueError as e:
                print(f"ERROR: {cidr} - {e}", file=sys.stderr)
        print("\n\n".join(lines))
    else:
        print("CIDR to Regex XML Converter")
        print("---")
        ticket = input("Ticket number [MC-4093]: ").strip() or "MC-4093"
        print(f"\nUsing ticket: {ticket}")
        print("Enter CIDR ranges (e.g. 37.186.39.0/24), one per line.")
        print("Type 'done' when finished, or 'quit' to exit.\n")
        collected = []
        while True:
            try:
                cidr = input("CIDR> ").strip()
                if not cidr or cidr.lower() in ("quit", "exit", "q"):
                    break
                if cidr.lower() == "done":
                    break
                collected.append(cidr)
            except (KeyboardInterrupt, EOFError):
                print()
                break

        if collected:
            print("\n--- OUTPUT ---\n")
            lines = []
            for cidr in collected:
                try:
                    lines.append(cidr_to_xml(cidr, ticket))
                except ValueError as e:
                    print(f"ERROR: {cidr} - {e}", file=sys.stderr)
            print("\n\n".join(lines))


if __name__ == "__main__":
    main()
