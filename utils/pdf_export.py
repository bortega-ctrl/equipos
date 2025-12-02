
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_to_pdf(dataframe, filename="reporte.pdf", logo_path=None):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(30, 750, "Reporte de Equipos")
    y = 700
    if logo_path:
        c.drawImage(logo_path, 400, 730, width=100, height=50)
    for _, row in dataframe.iterrows():
        text = f"ID:{row['id']} | {row['tipo']} | {row['ubicacion']} | Estado:{row['estado']} | Motivo:{row['motivo']}"
        c.drawString(30, y, text)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
