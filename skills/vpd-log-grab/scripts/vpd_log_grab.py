#!/usr/bin/env python3
"""
VPD Log Grab – Final script
==========================

Downloads the Vallejo Police Department public log for a given date,
converts it to plain text using pdftotext, parses the layout, and writes
a CSV of incidents.
"""

import sys
import os
import re
import urllib.request
import subprocess

BASE_URL = "https://cdnsm5-hosted.civiclive.com/UserFiles/Servers/Server_16397369/File/Public%20Information/DailyLog"

def download_pdf(date_str: str, out_path: str) -> None:
    file_date = date_str.replace('-', '_')
    url = f"{BASE_URL}/{file_date}.pdf?v=1774913671405"
    print(f"Downloading {url} …")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(out_path, "wb") as out:
        out.write(resp.read())


def pdf_to_text(pdf_path: str, txt_path: str) -> None:
    subprocess.check_call(["pdftotext", "-layout", pdf_path, txt_path])


def parse_layout(txt_path: str) -> list:
    records = []
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^(incident|from|vallejo)", line.lower()):
                continue
            parts = re.split(r"\s{2,}", line)
            if len(parts) < 6:
                continue
            inc_id = parts[0].strip()
            if not re.match(r"^\d{10}$", inc_id):
                continue
            date_time = parts[1].strip()
            if ' ' not in date_time:
                continue
            date, time = date_time.split(' ', 1)
            location = parts[2].strip()
            description = parts[3].strip()
            beat = parts[4].strip()
            disposition = parts[5].strip()
            records.append((inc_id, date, time, location, description, beat, disposition))
    print(f"Parsed {len(records)} records from {txt_path}")
    return records


def write_csv(records: list, csv_path: str) -> None:
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Incident #,Date,Time,Location,Description,Beat,Disposition\n")
        for r in records:
            f.write(",".join(r) + "\n")
    print(f"Wrote {len(records)} rows to {csv_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: vpd_log_grab.py YYYY-MM-DD [output_dir]")
        sys.exit(1)
    date_str = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/home/claw/output"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{date_str}.pdf")
    txt_path = os.path.join(output_dir, f"{date_str}_layout.txt")
    csv_path = os.path.join(output_dir, f"{date_str}_incidents.csv")
    try:
        download_pdf(date_str, pdf_path)
        pdf_to_text(pdf_path, txt_path)
        records = parse_layout(txt_path)
        if records:
            write_csv(records, csv_path)
            # also copy to workspace output folder
            import shutil
            workspace_output = os.path.join(os.path.expanduser("~/.openclaw/workspace/output"), os.path.basename(csv_path))
            os.makedirs(os.path.dirname(workspace_output), exist_ok=True)
            shutil.copy(csv_path, workspace_output)
            print(f"Copied CSV to {workspace_output}")
        else:
            print("No records parsed – CSV not created.")
    except Exception as e:
        print("Error during processing:", e)
        raise


if __name__ == "__main__":
    main()
