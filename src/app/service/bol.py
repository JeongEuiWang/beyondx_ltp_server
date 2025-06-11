from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepInFrame, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

async def create_structured_bill_of_lading(data, filename="structured_bill_of_lading.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Normal_LEFT', parent=styles['Normal'], alignment=0))
    styles.add(ParagraphStyle(name='Normal_CENTER', parent=styles['Normal'], alignment=1))
    styles.add(ParagraphStyle(name='Normal_RIGHT', parent=styles['Normal'], alignment=2))
    styles.add(ParagraphStyle(name='Bold_LEFT', parent=styles['Normal_LEFT'], fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Small_Normal_LEFT', parent=styles['Normal_LEFT'], fontSize=6))
    styles.add(ParagraphStyle(name='Small_Bold_LEFT', parent=styles['Small_Normal_LEFT'], fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Section_Title', parent=styles['Bold_LEFT'], fontSize=10, spaceBefore=0.1*inch, spaceAfter=0.05*inch))

    story = []

    header_content = [
        [Paragraph("<b>DATE</b>", styles['Small_Bold_LEFT']), Paragraph(datetime.now().strftime("%Y-%m-%d"), styles['Small_Normal_LEFT']),
         Paragraph("<b>BILL OF LADING NUMBER</b>", styles['Small_Bold_LEFT']), Paragraph(data.get('id', 'N/A'), styles['Small_Normal_LEFT'])],
    ]
    header_table = Table(header_content, colWidths=[0.7*inch, 2.8*inch, 1.7*inch, 2.3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.1*inch))



    from_location = data.get('from_location', {})
    to_location = data.get('to_location', {})

    party_info_data = [
        [Paragraph("<b>SHIP FROM</b>", styles['Small_Bold_LEFT']),
         Paragraph("<b>SHIP TO</b>", styles['Small_Bold_LEFT'])],
        [Paragraph(from_location.get('location_type', 'N/A') + " (Shipper)", styles['Small_Normal_LEFT']),
         Paragraph(to_location.get('location_type', 'N/A') + " (Consignee)", styles['Small_Normal_LEFT'])],
        [Paragraph(f"{from_location.get('address', '')}", styles['Small_Normal_LEFT']),
         Paragraph(f"{to_location.get('address', '')}", styles['Small_Normal_LEFT'])],
        [Paragraph(f"{from_location.get('city', '')}, {from_location.get('state', '')} {from_location.get('zip_code', '')}", styles['Small_Normal_LEFT']),
         Paragraph(f"{to_location.get('city', '')}, {to_location.get('state', '')} {to_location.get('zip_code', '')}", styles['Small_Normal_LEFT'])],
        [Paragraph(f"County: {from_location.get('county', '')}", styles['Small_Normal_LEFT']),
         Paragraph(f"County: {to_location.get('county', '')}", styles['Small_Normal_LEFT'])],
        [Paragraph(f"Req. Date: {from_location.get('request_datetime', '')}", styles['Small_Normal_LEFT']),
         Paragraph(f"Req. Date: {to_location.get('request_datetime', '')}", styles['Small_Normal_LEFT'])],
    ]

    party_table = Table(party_info_data, colWidths=[3.75*inch, 3.75*inch])
    party_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,-1), 0.5, colors.black),
        ('BOX', (1,0), (1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    story.append(party_table)
    story.append(Spacer(1, 0.1*inch))

    from_accessorials = ", ".join([acc['name'] for acc in from_location.get('accessorials', [])])
    to_accessorials = ", ".join([acc['name'] for acc in to_location.get('accessorials', [])])

    accessorials_data = [
        [Paragraph("<b>Shipper Accessorials:</b>", styles['Small_Bold_LEFT']), Paragraph(from_accessorials if from_accessorials else "None", styles['Small_Normal_LEFT'])],
        [Paragraph("<b>Consignee Accessorials:</b>", styles['Small_Bold_LEFT']), Paragraph(to_accessorials if to_accessorials else "None", styles['Small_Normal_LEFT'])],
    ]
    accessorials_table = Table(accessorials_data, colWidths=[1.5*inch, 6*inch])
    accessorials_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(accessorials_table)
    story.append(Spacer(1, 0.2*inch))


    story.append(Paragraph("CUSTOMER ORDER INFORMATION", styles['Section_Title']))
    customer_order_header = [
        Paragraph("<b>Quantity</b>", styles['Small_Bold_LEFT']),
        Paragraph("<b>Weight (LBS)</b>", styles['Small_Bold_LEFT']),
        Paragraph("<b>Package Description</b>", styles['Small_Bold_LEFT']),
        Paragraph("<b>Stackable</b>", styles['Small_Bold_LEFT'])
    ]

    customer_order_data = [customer_order_header]
    cargo_items = data.get('cargo', [])
    
    num_data_rows = 8
    min_row_height = 0.2 * inch

    row_heights = [None]

    for i in range(num_data_rows):
        if i < len(cargo_items):
            item = cargo_items[i]
            has_content = bool(str(item.get('quantity', '')).strip() or \
                               str(item.get('weight', '')).strip() or \
                               item.get('package_description', '').strip() or \
                               (item.get('cargo_stackable') is not None))
            
            if has_content:
                row_heights.append(None)
                stackable_text = ''
                if item.get('cargo_stackable') is True:
                    stackable_text = 'Yes'
                elif item.get('cargo_stackable') is False:
                    stackable_text = 'No'
                
                row_cells = [
                    Paragraph(str(item.get('quantity', '')), styles['Small_Normal_LEFT']),
                    Paragraph(str(item.get('weight', '')), styles['Small_Normal_LEFT']),
                    Paragraph(item.get('package_description', ''), styles['Small_Normal_LEFT']),
                    Paragraph(stackable_text, styles['Small_Normal_LEFT'])
                ]
            else:
                row_heights.append(min_row_height)
                row_cells = [Paragraph('', styles['Small_Normal_LEFT']) for _ in range(len(customer_order_header))]
        else:
            row_heights.append(min_row_height)
            row_cells = [Paragraph('', styles['Small_Normal_LEFT']) for _ in range(len(customer_order_header))]
        customer_order_data.append(row_cells)

    
    customer_order_table = Table(customer_order_data, colWidths=[0.8*inch, 1*inch, 4.7*inch, 1*inch], rowHeights=row_heights)
    customer_order_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(customer_order_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Spacer(1, 1*inch))

    pricing_line_content = [
        Paragraph("<b>Base Price:</b> $ {:.2f}".format(data.get('base_price', 0.0)), styles['Small_Bold_LEFT']),
        Paragraph("<b>Extra Price:</b> $ {:.2f}".format(data.get('extra_price', 0.0)), styles['Small_Bold_LEFT']),
        Paragraph("<b>TOTAL PRICE:</b> $ {:.2f}".format(data.get('total_price', 0.0)), styles['Bold_LEFT']),
    ]

    page_width = letter[0]
    available_width = page_width - (doc.leftMargin + doc.rightMargin)
    
    price_col_widths = [available_width * 0.3, available_width * 0.3, available_width * 0.4]

    pricing_table_horizontal = Table([pricing_line_content], colWidths=price_col_widths)
    pricing_table_horizontal.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    story.append(pricing_table_horizontal)




    doc.build(story)
    print(f"PDF '{filename}' created successfully.")

json_data = {
    "id": "A26774E97D3C4152A71800703FB7D42E",
    "user_id": 1,
    "cargo_transportation_id": 1,
    "is_priority": True,
    "total_weight": 1500.0,
    "base_price": 141.75,
    "extra_price": 560.0,
    "total_price": 701.75,
    "order_status": "ESTIMATE",
    "order_primary": None,
    "order_additional_request": None,
    "from_location": {
        "state": "TX",
        "county": "Dallas-Texas County",
        "city": "Dallas",
        "zip_code": "75030",
        "address": "61, Cheongmyeong-ro, Yeongtong-gu",
        "location_type": "COMMERCIAL",
        "request_datetime": "2025-05-05T18:40:00",
        "accessorials": [
            {"cargo_accessorial_id": 1, "name": "Inside Delivery"},
            {"cargo_accessorial_id": 2, "name": "Two Person"}
        ],
        "id": 1
    },
    "to_location": {
        "state": "TX",
        "county": "Dallas-Texas County",
        "city": "Dallas",
        "zip_code": "75028",
        "address": "123, Hansoup-ro, Yeongtong-gu",
        "location_type": "AIRPORT",
        "request_datetime": "2025-05-10T19:40:00",
        "accessorials": [
            {"cargo_accessorial_id": 2, "name": "Two Person"},
            {"cargo_accessorial_id": 3, "name": "Lift Gate"}
        ],
        "id": 2
    },
    "cargo": [
        {
            "width": 40,
            "length": 48,
            "height": 80,
            "weight": 1500,
            "quantity": 1,
            "package_description": "Description of package",
            "cargo_stackable": True,
            "cargo_temperature": "At least 30 D.C",
            "is_hazardous": False,
            "hazardous_detail": "detail of hazardous",
            "id": 1
        },
        {
            "width": 40,
            "length": 48,
            "height": 80,
            "weight": 1000,
            "quantity": 2,
            "package_description": "Description of package Description of packageDescription of packageDescription of packageDescription of packageDescription of packageDescription of packageDescription of packageDescription of packageDescription of package",
            "cargo_stackable": True,
            "cargo_temperature": "At least 30 D.C",
            "is_hazardous": False,
            "hazardous_detail": "detail of hazardous",
            "id": 1
        }
    ]
}