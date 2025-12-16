"""
PDF Service for generating loan sanction letters
Uses ReportLab for professional PDF generation
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.schemas import UnderwritingResult


class PDFService:
    """Service for generating PDF documents"""
    
    def __init__(self):
        self.output_dir = "generated"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Company details
        self.company_info = {
            "name": "QuickLoan Financial Services Pvt. Ltd.",
            "address": "123 Financial District, Bangalore, Karnataka 560001",
            "phone": "+91-80-1234-5678",
            "email": "loans@quickloan.in",
            "cin": "U65100KA2020PTC123456",
            "license": "NBFC-ND-SI Certificate No: 14.03.167"
        }
    
    async def generate_sanction_letter(
        self,
        customer_data: Dict[str, Any],
        loan_details: UnderwritingResult,
        session_id: str
    ) -> str:
        """Generate loan sanction letter PDF"""
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sanction_letter_{session_id[:8]}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build PDF content
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Company header
        story.append(Paragraph(self.company_info["name"], title_style))
        story.append(Paragraph(self.company_info["address"], styles['Normal']))
        story.append(Paragraph(f"Phone: {self.company_info['phone']} | Email: {self.company_info['email']}", styles['Normal']))
        story.append(Paragraph(f"CIN: {self.company_info['cin']}", styles['Normal']))
        story.append(Paragraph(f"{self.company_info['license']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Letter title
        story.append(Paragraph("LOAN SANCTION LETTER", title_style))
        story.append(Spacer(1, 20))
        
        # Letter reference and date
        letter_ref = f"QL/{datetime.now().year}/SL/{session_id[:8].upper()}"
        letter_date = datetime.now().strftime("%d %B, %Y")
        
        ref_table_data = [
            [f"Letter Ref: {letter_ref}", f"Date: {letter_date}"]
        ]
        ref_table = Table(ref_table_data, colWidths=[3*inch, 2*inch])
        ref_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        story.append(ref_table)
        story.append(Spacer(1, 15))
        
        # Customer details
        story.append(Paragraph("Customer Details:", header_style))
        
        customer_details = f"""
        <b>Name:</b> {customer_data.get('name', 'N/A')}<br/>
        <b>Address:</b> {customer_data.get('address', 'N/A')}<br/>
        <b>PAN:</b> {customer_data.get('pan', 'N/A')}<br/>
        <b>Mobile:</b> +91-XXXX-XXX-XXX (for privacy)
        """
        story.append(Paragraph(customer_details, normal_style))
        story.append(Spacer(1, 15))
        
        # Loan details
        story.append(Paragraph("Loan Sanction Details:", header_style))
        
        # Calculate processing fee and other charges
        processing_fee = min(loan_details.loan_amount * 0.01, 5000)  # 1% or max 5000
        documentation_charges = 1000
        total_charges = processing_fee + documentation_charges
        
        # Calculate disbursement amount
        disbursement_amount = loan_details.loan_amount - total_charges
        
        # Loan details table
        loan_table_data = [
            ["Loan Amount Sanctioned", f"Rs.{loan_details.loan_amount:,.0f}"],
            ["Interest Rate", f"{loan_details.interest_rate}% per annum"],
            ["Loan Tenure", f"{loan_details.tenure} months"],
            ["EMI Amount", f"Rs.{loan_details.emi:,.0f}"],
            ["Processing Fee", f"Rs.{processing_fee:,.0f}"],
            ["Documentation Charges", f"Rs.{documentation_charges:,.0f}"],
            ["Amount to be Disbursed", f"Rs.{disbursement_amount:,.0f}"],
            ["First EMI Due Date", (datetime.now() + timedelta(days=30)).strftime("%d %B, %Y")],
        ]
        
        loan_table = Table(loan_table_data, colWidths=[2.5*inch, 2*inch])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(loan_table)
        story.append(Spacer(1, 15))
        
        # Terms and conditions
        story.append(Paragraph("Terms and Conditions:", header_style))
        
        terms = """
        1. This sanction is valid for 30 days from the date of this letter.<br/>
        2. The loan is subject to completion of documentation and verification.<br/>
        3. Interest will be charged from the date of disbursement.<br/>
        4. EMI will be auto-debited from your registered bank account.<br/>
        5. Prepayment is allowed after 6 months with charges as applicable.<br/>
        6. Default in payment will attract penalty charges.<br/>
        7. The loan is governed by the terms and conditions of QuickLoan NBFC.<br/>
        8. Any disputes will be subject to Bangalore jurisdiction.<br/>
        """
        story.append(Paragraph(terms, normal_style))
        story.append(Spacer(1, 15))
        
        # Required documents
        story.append(Paragraph("\n\nDocuments Required for Disbursement:", header_style))
        
        documents = """
        • Signed loan agreement<br/>
        • Bank account statements (last 3 months)<br/>
        • Salary certificate from employer<br/>
        • Post-dated cheques for EMI<br/>
        • Identity and address proof<br/>
        • NACH mandate form
        """
        story.append(Paragraph(documents, normal_style))
        story.append(Spacer(1, 20))
        
        # Contact information
        contact_info = f"""
        For any queries, please contact us:<br/>
        <b>Loan Officer:</b> Rajesh Kumar<br/>
        <b>Phone:</b> {self.company_info['phone']}<br/>
        <b>Email:</b> {self.company_info['email']}
        """
        story.append(Paragraph(contact_info, normal_style))
        story.append(Spacer(1, 30))
        
        # Signature section
        signature_data = [
            ["", ""],
            ["Customer Signature", "Authorized Signatory"],
            ["", "QuickLoan Financial Services"]
        ]
        signature_table = Table(signature_data, colWidths=[2.5*inch, 2.5*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('LINEBELOW', (0,0), (0,0), 1, colors.black),
            ('LINEBELOW', (1,0), (1,0), 1, colors.black),
        ]))
        story.append(signature_table)
        
        # Footer
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph("This is a computer-generated document and does not require a physical signature.", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath