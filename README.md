# CIDR to Regex XML Converter

Converts CIDR IP ranges into XML address-pattern entries with regex, ready to paste into configuration files.

## Example

**Input:**
```
37.186.39.0/24
103.225.75.96/27
```

**Output:**
```xml
<!--  Added via MC-4703 Ip range: 37.186.39.0/24  IP Range First usable : 37.186.39.0 Last usable 37.186.39.255  -->
<address pattern = "37\.186\.39\.([1-9]?\d|[12]\d\d)$"/>

<!--  Added via MC-4703 Ip range: 103.225.75.96/27  IP Range First usable : 103.225.75.96 Last usable 103.225.75.127  -->
<address pattern = "103\.225\.75\.(9[6-9]|1[0-1]\d|12[0-7])$"/>
```

## Prerequisites

- **Python 3.6+** (uses the built-in `ipaddress` module, no extra packages needed)

## Usage

### Option 1: Batch Script (Windows CMD)

1. Add your CIDR ranges to `IP_RANGE.txt` (one per line)
2. Run from CMD:

```cmd
cidr_to_regex.bat
```

To specify a ticket number:

```cmd
cidr_to_regex.bat MC-5001
```

Output is printed on screen and saved to `IP_RANGE_OUTPUT.xml`.

### Option 2: Python Script Directly

**Command-line arguments:**
```bash
python cidr_to_regex.py -t MC-4703 37.186.39.0/24 10.0.0.0/22
```

**From a file:**
```bash
python cidr_to_regex.py -t MC-4703 -f IP_RANGE.txt
```

**Interactive mode:**
```bash
python cidr_to_regex.py
```

## Supported CIDR Prefixes

Works with any prefix length from `/0` to `/32`:

| Prefix | Example | Last Octet Regex |
|--------|---------|-----------------|
| `/24` | `37.186.39.0/24` | `([1-9]?\d\|[12]\d\d)` |
| `/25` | `192.168.1.0/25` | `(\d\|[1-9]\d\|1[0-1]\d\|12[0-7])` |
| `/28` | `81.12.224.192/28` | `(19[2-9]\|20[0-7])` |
| `/29` | `213.233.64.48/29` | `(4[8-9]\|5[0-5])` |
| `/32` | `213.233.93.1/32` | `1` (exact match) |
| `/22` | `46.97.48.0/22` | Third octet varies too |

## Files

| File | Purpose |
|------|---------|
| `cidr_to_regex.py` | Core Python script (the engine) |
| `cidr_to_regex.bat` | Windows CMD launcher |
| `IP_RANGE.txt` | Input file — add your CIDRs here |
| `IP_RANGE_OUTPUT.xml` | Generated output (auto-created) |
