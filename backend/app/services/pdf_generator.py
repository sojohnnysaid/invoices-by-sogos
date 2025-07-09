from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from app.models.invoice import Invoice, InvoiceParty, LineItem, PartyType, InvoiceStatus


class InvoicePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Party name style
        self.styles.add(ParagraphStyle(
            name='PartyName',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#111827'),
            leading=14,
            fontName='Helvetica-Bold'
        ))
        
        # Party details style
        self.styles.add(ParagraphStyle(
            name='PartyDetails',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            leading=12
        ))
        
        # Label style
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            leading=11
        ))
        
        # Value style
        self.styles.add(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#111827'),
            leading=12
        ))
        
        # Notes style
        self.styles.add(ParagraphStyle(
            name='Notes',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            leading=14
        ))
    
    def _format_currency(self, amount: Decimal, currency: str) -> str:
        """Format amount with currency symbol"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CNY': '¥',
            'INR': '₹',
            'CAD': 'C$',
            'AUD': 'A$',
        }
        symbol = currency_symbols.get(currency, currency + ' ')
        return f"{symbol}{amount:,.2f}"
    
    def _format_date(self, date: datetime) -> str:
        """Format date as MM/DD/YYYY"""
        return date.strftime('%m/%d/%Y')
    
    def _get_status_color(self, status: InvoiceStatus) -> colors.Color:
        """Get color based on invoice status"""
        status_colors = {
            InvoiceStatus.DRAFT: colors.HexColor('#6b7280'),
            InvoiceStatus.SENT: colors.HexColor('#3b82f6'),
            InvoiceStatus.PAID: colors.HexColor('#10b981'),
            InvoiceStatus.OVERDUE: colors.HexColor('#ef4444'),
        }
        return status_colors.get(status, colors.HexColor('#6b7280'))
    
    def _create_header(self, invoice: Invoice, parties: List[InvoiceParty]) -> List:
        """Create invoice header with parties information"""
        elements = []
        
        # Get parties
        from_party = next((p for p in parties if p.party_type == PartyType.FROM), None)
        to_party = next((p for p in parties if p.party_type == PartyType.TO), None)
        ship_to_party = next((p for p in parties if p.party_type == PartyType.SHIP_TO), None)
        
        # Title and Invoice Number
        header_data = [[
            Paragraph('INVOICE', self.styles['InvoiceTitle']),
            Paragraph(f'<b>Invoice #:</b> {invoice.invoice_number}', self.styles['Value'])
        ]]
        
        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice details and parties
        details_data = []
        
        # Left side - From party
        if from_party:
            from_content = []
            from_content.append(Paragraph('<b>From:</b>', self.styles['Label']))
            from_content.append(Paragraph(from_party.name, self.styles['PartyName']))
            if from_party.address:
                from_content.append(Paragraph(from_party.address, self.styles['PartyDetails']))
            if from_party.city or from_party.state or from_party.zip_code:
                location = ', '.join(filter(None, [from_party.city, from_party.state, from_party.zip_code]))
                from_content.append(Paragraph(location, self.styles['PartyDetails']))
            if from_party.country:
                from_content.append(Paragraph(from_party.country, self.styles['PartyDetails']))
            if from_party.email:
                from_content.append(Paragraph(from_party.email, self.styles['PartyDetails']))
            if from_party.phone:
                from_content.append(Paragraph(from_party.phone, self.styles['PartyDetails']))
        else:
            from_content = [Paragraph('', self.styles['Normal'])]
        
        # Middle - To party
        if to_party:
            to_content = []
            to_content.append(Paragraph('<b>Bill To:</b>', self.styles['Label']))
            to_content.append(Paragraph(to_party.name, self.styles['PartyName']))
            if to_party.address:
                to_content.append(Paragraph(to_party.address, self.styles['PartyDetails']))
            if to_party.city or to_party.state or to_party.zip_code:
                location = ', '.join(filter(None, [to_party.city, to_party.state, to_party.zip_code]))
                to_content.append(Paragraph(location, self.styles['PartyDetails']))
            if to_party.country:
                to_content.append(Paragraph(to_party.country, self.styles['PartyDetails']))
            if to_party.email:
                to_content.append(Paragraph(to_party.email, self.styles['PartyDetails']))
            if to_party.phone:
                to_content.append(Paragraph(to_party.phone, self.styles['PartyDetails']))
        else:
            to_content = [Paragraph('', self.styles['Normal'])]
        
        # Right side - Invoice details
        invoice_details = []
        invoice_details.append(Paragraph(f'<b>Status:</b> <font color="{self._get_status_color(invoice.status).hexval()}">{invoice.status.value.upper()}</font>', self.styles['Value']))
        invoice_details.append(Paragraph(f'<b>Issue Date:</b> {self._format_date(invoice.date)}', self.styles['Value']))
        invoice_details.append(Paragraph(f'<b>Due Date:</b> {self._format_date(invoice.due_date)}', self.styles['Value']))
        if invoice.payment_terms:
            invoice_details.append(Paragraph(f'<b>Payment Terms:</b> {invoice.payment_terms}', self.styles['Value']))
        invoice_details.append(Paragraph(f'<b>Currency:</b> {invoice.currency}', self.styles['Value']))
        
        # Create the details table
        details_data = [[from_content, to_content, invoice_details]]
        
        details_table = Table(details_data, colWidths=[2.2*inch, 2.2*inch, 2.1*inch])
        details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(details_table)
        
        # Ship To (if exists)
        if ship_to_party:
            elements.append(Spacer(1, 0.2*inch))
            ship_to_content = []
            ship_to_content.append(Paragraph('<b>Ship To:</b>', self.styles['Label']))
            ship_to_content.append(Paragraph(ship_to_party.name, self.styles['PartyName']))
            if ship_to_party.address:
                ship_to_content.append(Paragraph(ship_to_party.address, self.styles['PartyDetails']))
            if ship_to_party.city or ship_to_party.state or ship_to_party.zip_code:
                location = ', '.join(filter(None, [ship_to_party.city, ship_to_party.state, ship_to_party.zip_code]))
                ship_to_content.append(Paragraph(location, self.styles['PartyDetails']))
            if ship_to_party.country:
                ship_to_content.append(Paragraph(ship_to_party.country, self.styles['PartyDetails']))
            
            ship_to_table = Table([[ship_to_content]], colWidths=[6.5*inch])
            ship_to_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(ship_to_table)
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_line_items_table(self, line_items: List[LineItem], currency: str) -> Table:
        """Create line items table"""
        # Table headers
        headers = ['Description', 'Quantity', 'Unit Price', 'Amount']
        data = [[Paragraph(f'<b>{h}</b>', self.styles['Value']) for h in headers]]
        
        # Sort line items by position
        sorted_items = sorted(line_items, key=lambda x: x.position)
        
        # Add line items
        for item in sorted_items:
            data.append([
                Paragraph(item.description, self.styles['Value']),
                Paragraph(f'{item.quantity:,.2f}', self.styles['Value']),
                Paragraph(self._format_currency(item.unit_price, currency), self.styles['Value']),
                Paragraph(self._format_currency(item.amount, currency), self.styles['Value']),
            ])
        
        # Create table
        table = Table(data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            
            # Borders
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e5e7eb')),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#f3f4f6')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        
        return table
    
    def _create_totals_section(self, invoice: Invoice) -> Table:
        """Create totals section"""
        data = []
        
        # Subtotal
        data.append([
            Paragraph('Subtotal:', self.styles['Value']),
            Paragraph(self._format_currency(invoice.subtotal, invoice.currency), self.styles['Value'])
        ])
        
        # Tax
        if invoice.tax_amount > 0:
            data.append([
                Paragraph(f'Tax ({invoice.tax_rate}%):', self.styles['Value']),
                Paragraph(self._format_currency(invoice.tax_amount, invoice.currency), self.styles['Value'])
            ])
        
        # Discount
        if invoice.discount_amount > 0:
            data.append([
                Paragraph('Discount:', self.styles['Value']),
                Paragraph(f'-{self._format_currency(invoice.discount_amount, invoice.currency)}', self.styles['Value'])
            ])
        
        # Shipping
        if invoice.shipping_amount > 0:
            data.append([
                Paragraph('Shipping:', self.styles['Value']),
                Paragraph(self._format_currency(invoice.shipping_amount, invoice.currency), self.styles['Value'])
            ])
        
        # Total
        data.append([
            Paragraph('<b>Total:</b>', self.styles['Value']),
            Paragraph(f'<b>{self._format_currency(invoice.total, invoice.currency)}</b>', self.styles['Value'])
        ])
        
        # Amount Paid
        if invoice.amount_paid > 0:
            data.append([
                Paragraph('Amount Paid:', self.styles['Value']),
                Paragraph(self._format_currency(invoice.amount_paid, invoice.currency), self.styles['Value'])
            ])
        
        # Balance Due
        data.append([
            Paragraph('<b>Balance Due:</b>', ParagraphStyle(
                name='BalanceDue',
                parent=self.styles['Value'],
                fontSize=12,
                textColor=colors.HexColor('#dc2626') if invoice.balance_due > 0 else colors.HexColor('#059669')
            )),
            Paragraph(f'<b>{self._format_currency(invoice.balance_due, invoice.currency)}</b>', ParagraphStyle(
                name='BalanceDueAmount',
                parent=self.styles['Value'],
                fontSize=12,
                textColor=colors.HexColor('#dc2626') if invoice.balance_due > 0 else colors.HexColor('#059669')
            ))
        ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#e5e7eb')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#374151')),
        ]))
        
        return table
    
    def _create_notes_section(self, invoice: Invoice) -> List:
        """Create notes and terms section"""
        elements = []
        
        if invoice.notes:
            elements.append(Paragraph('<b>Notes:</b>', self.styles['Label']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(invoice.notes, self.styles['Notes']))
            elements.append(Spacer(1, 0.2*inch))
        
        if invoice.terms:
            elements.append(Paragraph('<b>Terms & Conditions:</b>', self.styles['Label']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(invoice.terms, self.styles['Notes']))
        
        return elements
    
    def generate_pdf(self, invoice: Invoice, parties: List[InvoiceParty], line_items: List[LineItem]) -> bytes:
        """Generate PDF invoice and return as bytes"""
        # Create BytesIO buffer
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        # Build content
        elements = []
        
        # Header with parties
        elements.extend(self._create_header(invoice, parties))
        
        # Line items table
        if line_items:
            elements.append(self._create_line_items_table(line_items, invoice.currency))
            elements.append(Spacer(1, 0.3*inch))
        
        # Totals section
        totals_table = self._create_totals_section(invoice)
        # Align totals to the right
        totals_container = Table([[None, totals_table]], colWidths=[3.5*inch, 3*inch])
        totals_container.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(totals_container)
        
        # Notes and terms
        if invoice.notes or invoice.terms:
            elements.append(Spacer(1, 0.5*inch))
            elements.extend(self._create_notes_section(invoice))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.read()