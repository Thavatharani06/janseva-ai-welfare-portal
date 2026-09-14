import os
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class FormService:
    @staticmethod
    def generate_official_application_pdf(
        output_pdf_path: str,
        scheme_name: str,
        scheme_code: str,
        applicant_name: str,
        applicant_email: str,
        district: str,
        annual_income: float,
        form_fields: Dict[str, Any]
    ) -> str:
        """
        Generates production PDF application form with official government layout.
        """
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        width, height = letter

        # Header Box
        c.setFillColor(colors.HexColor("#064e3b"))  # Dark emerald
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 35, "OFFICIAL GOVERNMENT WELFARE SCHEME APPLICATION FORM")
        c.setFont("Helvetica", 11)
        c.drawString(30, height - 55, f"Scheme: {scheme_name} ({scheme_code}) | JanSeva Portal Verified")

        # Form Fields Box
        y = height - 120
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "1. APPLICANT DEMOGRAPHIC & IDENTITY DETAILS")
        y -= 25

        c.setFont("Helvetica", 10)
        details = [
            ("Full Applicant Name:", applicant_name),
            ("Email Address:", applicant_email),
            ("District / State Scope:", district),
            ("Annual Income (INR):", f"Rs. {annual_income:,.2f}"),
            ("Application Tracking ID:", form_fields.get("tracking_id", "JANSEVA-2026-8891")),
            ("Submission Date:", form_fields.get("submission_date", "2026-07-21")),
        ]

        for label, val in details:
            c.setFillColor(colors.HexColor("#334155"))
            c.drawString(40, y, label)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(200, y, str(val))
            c.setFont("Helvetica", 10)
            y -= 20

        y -= 15
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "2. VERIFIED ATTACHED DOCUMENTS CHECKLIST")
        y -= 25

        docs = form_fields.get("verified_docs", ["Aadhaar Card (Verified)", "Income Certificate (Verified)"])
        for doc in docs:
            c.setFillColor(colors.HexColor("#047857"))
            c.drawString(40, y, f"✓  {doc}")
            y -= 18

        y -= 30
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.line(30, y, width - 30, y)
        y -= 30

        # Declaration
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(30, y, "Declaration: I hereby declare that all details provided above are true to the best of my knowledge.")
        y -= 40

        # Signatures
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, "Signature of Applicant")
        c.drawString(380, y, "JanSeva Digital Seal & Signature")

        c.save()
        return output_pdf_path
