import sqlite3
from xlsxwriter.workbook import Workbook


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import LongTable, BaseDocTemplate,Frame, PageTemplate
from reportlab.lib import colors
from reportlab.platypus import Paragraph, TableStyle


def excel():
    workbook = Workbook("Murojaatnomalar.xlsx")
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(30)
    worksheet.set_column(1,1,200.1)
    worksheet.set_column(0,0,20.1)
    worksheet.write(0, 0, "Ism-Familya")
    worksheet.write(0, 1, "Murojaatnoma")

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    with sqlite3.connect('Murojaat.sqlite3') as conn:
        c = conn.cursor()
        mysel = c.execute("select name,murojaat from murojaatlar")
    for i, row in enumerate(mysel, 1):
        worksheet.write(i, 0, row[0])
        worksheet.write(i, 1, row[1],cell_format)
    workbook.close()
    return open("Murojaatnomalar.xlsx",'rb')

def pdf():
    doc = BaseDocTemplate(
        "Murojaatnomalar.pdf",
        pagesize=A4,
        rightMargin=12,
        leftMargin=5,
        topMargin=8,
        bottomMargin=15,
        showBoundary=False)

    elements = []

    with sqlite3.connect('Murojaat.sqlite3') as conn:
        conn.row_factory = lambda cursor, row: [row[0],row[1]]
        c = conn.cursor()
        data = c.execute("select name,murojaat from murojaatlar").fetchall()
    data = [["Ism-Familya","Murojaatnoma"]]+data

    tableStyle = [
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (0, 0), (0, -1), "LEFT"),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 7), (0, 7), "RIGHT"),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]


    styles = getSampleStyleSheet()
    styleN = styles['Normal']

    styleN.wordWrap = 'CJK'

    data2 = [[Paragraph(cell, styleN) for cell in row] for row in data]

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 2 * cm, id='normal')

    colwidths = [frame._width/5.,4*frame._width/5.]

    t = LongTable(data2, colWidths=colwidths)
    t.setStyle(TableStyle(tableStyle))
    elements.append(t)

    template = PageTemplate(id='longtable', frames=frame)
    doc.addPageTemplates([template])
    doc.build(elements)
    return open("Murojaatnomalar.pdf",'rb')