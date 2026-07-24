
"""
Generates a handful of realistic-looking pharmaceutical complaint documents
(PDF + plain-text "email") for demoing the AI extraction workflow, per the
assignment note: "You may create your own realistic pharmaceutical complaint
PDFs, emails, or images for demonstration."

Run with:  python -m app.sample_data.generate_samples
Outputs into backend/app/sample_data/samples/
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT_DIR = os.path.join(os.path.dirname(__file__), "samples")
os.makedirs(OUT_DIR, exist_ok=True)


def write_pdf(filename: str, lines: list[str]):
    path = os.path.join(OUT_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < 72:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 72
        c.drawString(72, y, line)
        y -= 16
    c.save()
    print(f"Wrote {path}")


def write_text(filename: str, content: str):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"Wrote {path}")


SAMPLES = {
    "sample_complaint_1_discoloration.pdf": [
        "Subject: Customer Complaint - Discoloration in Tablets",
        "",
        "Customer: Meridian Pharma Distributors, Chicago IL",
        "Contact: Sarah Chen, Quality Manager",
        "",
        "Product: Amoxicillin 500mg Tablets",
        "Batch/Lot Number: AMX-2026-0417",
        "Manufacturing Date: 2026-02-10",
        "Expiry Date: 2028-02-09",
        "Quantity Affected: 3,200 tablets (32 bottles of 100)",
        "",
        "Complaint received via email on 2026-07-15.",
        "",
        "Description:",
        "During routine incoming inspection, our QA team observed yellowish",
        "discoloration on approximately 15% of tablets in 6 of the 32 bottles",
        "received from batch AMX-2026-0417. Tablets otherwise appear intact,",
        "no odor noted. No adverse events reported by end patients so far.",
        "Requesting investigation and root cause analysis.",
    ],
    "sample_complaint_2_adverse_event.pdf": [
        "PATIENT SAFETY COMPLAINT - URGENT",
        "",
        "Reported by: Dr. Ramesh Iyer, City Care Hospital",
        "Source: Phone Call, escalated by Regulatory Affairs",
        "Date of report: 2026-07-20",
        "",
        "Product: Metformin XR 1000mg Tablets",
        "Batch Number: MET-XR-2026-1122",
        "Manufacturing Date: 2025-11-02",
        "Expiry Date: 2027-11-01",
        "Quantity Affected: Unknown, single strip reported",
        "",
        "Description:",
        "Patient reported severe gastrointestinal distress and dizziness within",
        "30 minutes of ingestion. Tablet appeared to have an unusual chemical",
        "odor. Physician suspects possible contamination or degradation product.",
        "This has been reported as a suspected adverse drug reaction (ADR) and",
        "requires urgent triage.",
    ],
}

SAMPLE_EMAILS = {
    "sample_complaint_3_packaging.txt": """From: procurement@wellspringretail.com
Subject: Damaged blister packaging - Batch IBU-8850

Hi Team,

We received a shipment of Ibuprofen 400mg Tablets, batch IBU-8850,
manufacturing date 2026-04-01, expiry 2028-03-31, and noticed that
around 40 out of 500 blister strips have torn foil backing exposing
the tablets to air. Quantity affected roughly 400 tablets across 40
strips. No patient exposure yet, caught during our warehouse QC check
on 2026-07-18.

Please advise on replacement and let us know if this needs to be
logged as a formal complaint.

Thanks,
Wellspring Retail Purchasing Team
""",
    "sample_complaint_4_labeling.txt": """From: qa@brightlifepharmacy.com
Subject: Labeling discrepancy - wrong strength printed

Team,

Flagging a labeling error found on Paracetamol tablets, batch number
PCM-2026-0299, mfg date 2026-01-15, expiry 2028-01-14. The carton
states "650mg" but the blister foil is printed "500mg". Quantity
affected: 1 carton (100 tablets) so far, checking for more in the
same batch. Reported today, 2026-07-21, via our internal QA line.

This is a documentation/labeling discrepancy, not yet linked to any
patient harm, but needs prompt correction given potential dosing
confusion.

Regards,
Brightlife Pharmacy QA
""",
}


def main():
    for filename, lines in SAMPLES.items():
        write_pdf(filename, lines)
    for filename, content in SAMPLE_EMAILS.items():
        write_text(filename, content)


if __name__ == "__main__":
    main()
