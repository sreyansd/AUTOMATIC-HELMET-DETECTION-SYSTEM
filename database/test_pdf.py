from reportlab.pdfgen import canvas

c = canvas.Canvas("sample.pdf")

c.drawString(100, 750, "Hello ReportLab!")

c.save()

print("PDF Created Successfully")