# VPD Log Grab

## Description
Downloads the Vallejo Police Department public log for a specified date, converts it to plain text, parses the layout, and writes a CSV of incidents.

## Usage
```bash
vpd-log-grab YYYY-MM-DD [output_dir]
```

- `YYYY-MM-DD` – the date of the log to fetch.
- `output_dir` – optional directory to store the PDF, text, and CSV. Defaults to `/home/claw/output` if not provided; otherwise writes to the current working directory.

The script is located at `scripts/vpd_log_grab.py`.
