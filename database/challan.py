from reportlab.pdfgen import canvas
from datetime import datetime


def generate_challan(vehicle_number, violation, fine, output_path):
    c = canvas.Canvas(output_path)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, "TRAFFIC E-CHALLAN")

    c.setFont("Helvetica", 12)

    c.drawString(100, 740, f"Vehicle Number: {vehicle_number}")
    c.drawString(100, 710, f"Violation: {violation}")
    c.drawString(100, 680, f"Fine Amount: Rs {fine}")
    c.drawString(100, 650, f"Date: {datetime.now()}")

    c.save()