import time
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Report(models.Model):
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('yearly', 'Yearly Report'),
        ('custom', 'Custom Report'),
    ]
    
    SORT_OPTIONS = [
        ('date_asc', 'Date (Oldest First)'),
        ('date_desc', 'Date (Newest First)'),
        ('amount_asc', 'Amount (Lowest First)'),
        ('amount_desc', 'Amount (Highest First)'),
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=100)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    transaction_types = models.JSONField(default=list)  # List of transaction types to include
    categories = models.JSONField(default=list)  # List of category IDs to include
    sort_by = models.CharField(max_length=20, choices=SORT_OPTIONS, default='date_desc')
    file = models.FileField(upload_to='reports/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'report_type']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

    def _generate_balance_history_data(self, data, transactions):
        """Generate balance history data for the chart based on report type"""
        from decimal import Decimal

        balance_data = {
            'labels': [],
            'datasets': [{
                'label': 'Balance',
                'data': [],
                'borderColor': 'rgb(59, 130, 246)',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'fill': True,
                'tension': 0.4
            }]
        }

        # Determine appropriate date format based on report type
        if self.report_type == 'daily':
            date_format = '%H:00'  # Hourly for daily view
            group_format = '%Y-%m-%d %H'
        elif self.report_type == 'weekly':
            date_format = '%a, %d'  # Day of week for weekly view
            group_format = '%Y-%m-%d'
        elif self.report_type == 'monthly':
            date_format = '%d'  # Day of month for monthly view
            group_format = '%Y-%m-%d'
        elif self.report_type == 'yearly':
            date_format = '%b'  # Month for yearly view
            group_format = '%Y-%m'
        else:  # custom
            # For custom reports, choose appropriate grouping based on date range
            days_diff = (self.end_date.date() - self.start_date.date()).days
            if days_diff <= 7:
                date_format = '%a, %d'
                group_format = '%Y-%m-%d'
            elif days_diff <= 31:
                date_format = '%d %b'
                group_format = '%Y-%m-%d'
            elif days_diff <= 365:
                date_format = '%b'
                group_format = '%Y-%m'
            else:
                date_format = '%Y'
                group_format = '%Y'

        # Get all transactions and process them in Python rather than using DB functions
        all_transactions = transactions.values('date', 'type', 'amount').order_by('date')

        # Group transactions by date period
        grouped_data = {}

        for tx in all_transactions:
            tx_date = tx['date']
            period_key = tx_date.strftime(group_format)

            if period_key not in grouped_data:
                grouped_data[period_key] = {
                    'balance': Decimal('0.00'),
                    'date': tx_date
                }

            # Update balance based on transaction type
            if tx['type'] == 'income':
                grouped_data[period_key]['balance'] += tx['amount']
            else:  # expense
                grouped_data[period_key]['balance'] -= tx['amount']

        # Sort periods chronologically
        sorted_periods = sorted(grouped_data.items(), key=lambda x: x[0])

        # Calculate cumulative balance
        cumulative_balance = Decimal('0.00')

        for period_key, period_data in sorted_periods:
            cumulative_balance += period_data['balance']

            # Format date for display
            label = period_data['date'].strftime(date_format)

            balance_data['labels'].append(label)
            balance_data['datasets'][0]['data'].append(float(cumulative_balance))

        data['chart_data']['balance_history'] = balance_data

    def _generate_category_breakdown_data(self, data, income_transactions, expense_transactions):
        """Generate category breakdown data for pie charts"""
        from collections import defaultdict

        # Define colors for the charts
        colors = [
            'rgba(54, 162, 235, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(22, 160, 133, 0.8)',
            'rgba(192, 57, 43, 0.8)',
            'rgba(243, 156, 18, 0.8)',
            'rgba(142, 68, 173, 0.8)',
            'rgba(39, 174, 96, 0.8)'
        ]

        # Process income transactions
        income_by_category = defaultdict(Decimal)
        for transaction in income_transactions:
            category_name = transaction.category.name if transaction.category else 'Uncategorized'
            income_by_category[category_name] += transaction.amount

        # Sort by amount (highest first)
        income_sorted = sorted(income_by_category.items(), key=lambda x: x[1], reverse=True)

        income_chart_data = {
            'labels': [],
            'data': [],
            'backgroundColor': []
        }

        for i, (category_name, amount) in enumerate(income_sorted):
            income_chart_data['labels'].append(category_name)
            income_chart_data['data'].append(float(amount))
            income_chart_data['backgroundColor'].append(colors[i % len(colors)])

        data['chart_data']['income_by_category'] = income_chart_data

        # Process expense transactions
        expense_by_category = defaultdict(Decimal)
        for transaction in expense_transactions:
            category_name = transaction.category.name if transaction.category else 'Uncategorized'
            expense_by_category[category_name] += transaction.amount

        # Sort by amount (highest first)
        expense_sorted = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)

        expense_chart_data = {
            'labels': [],
            'data': [],
            'backgroundColor': []
        }

        for i, (category_name, amount) in enumerate(expense_sorted):
            expense_chart_data['labels'].append(category_name)
            expense_chart_data['data'].append(float(amount))
            expense_chart_data['backgroundColor'].append(colors[i % len(colors)])

        data['chart_data']['expense_by_category'] = expense_chart_data

    def generate_report_data(self):
        """Generate the data for the report"""
        from transactions.models import Transaction
        from budgets.models import Budget
        from django.db.models import Q

        # Apply sorting
        if self.sort_by == 'date_asc':
            sort_field = 'date'
        elif self.sort_by == 'date_desc':
            sort_field = '-date'
        elif self.sort_by == 'amount_asc':
            sort_field = 'amount'
        elif self.sort_by == 'amount_desc':
            sort_field = '-amount'
        elif self.sort_by == 'name_asc':
            sort_field = 'name'
        elif self.sort_by == 'name_desc':
            sort_field = '-name'
        else:
            sort_field = '-date'

        data = {
            'report_info': {
                'title': self.title,
                'type': self.get_report_type_display(),
                'period': f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}",
                # 'generated_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            },
            'transactions': [],
            'budgets': [],
            'categories': [],
            'chart_data': {
                'balance_history': {
                    'labels': [],
                    'datasets': []
                },
                'income_by_category': {
                    'labels': [],
                    'data': [],
                    'backgroundColor': []
                },
                'expense_by_category': {
                    'labels': [],
                    'data': [],
                    'backgroundColor': []
                    }
                }
            }

            # Build transaction filter
        transaction_filter = Q(user=self.user) & Q(date__range=(self.start_date, self.end_date))

        if self.transaction_types:
            transaction_filter &= Q(type__in=self.transaction_types)

        if self.categories:
            category_ids = [int(id) for id in self.categories if id.isdigit()]
            if category_ids:
                transaction_filter &= Q(category__id__in=category_ids)

        # Get transactions for the period
        transactions = Transaction.objects.filter(transaction_filter).select_related('category', 'budget').order_by(sort_field)

        # Calculate summary data
        income_transactions = [t for t in transactions if t.type == 'income']
        expense_transactions = [t for t in transactions if t.type == 'expense']

        total_income = sum(t.amount for t in income_transactions) if income_transactions else Decimal('0.00')
        total_expense = sum(t.amount for t in expense_transactions) if expense_transactions else Decimal('0.00')

        data['summary'] = {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'transaction_count': len(transactions),
        }

        # Generate balance history data for chart
        self._generate_balance_history_data(data, transactions)

        # Generate category breakdown data
        self._generate_category_breakdown_data(data, income_transactions, expense_transactions)

        # Format transaction data
        for transaction in transactions:
            data['transactions'].append({
                'id': transaction.id,
                'name': transaction.name,
                'description': transaction.description,
                'amount': transaction.amount,
                'type': transaction.get_type_display(),
                'date': transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
                'category': transaction.category.name if transaction.category else 'Uncategorized',
                'budget': transaction.budget.get_budget_type_display() if transaction.budget else 'No Budget',
            })

        # Get budgets for the period
        budgets = Budget.objects.filter(
            user=self.user
        ).order_by('budget_type')

        for budget in budgets:
            data['budgets'].append({
                'id': budget.id,
                'type': budget.get_budget_type_display(),
                'amount': budget.amount,
                'spent': budget.get_spent_amount(),
                'remaining': budget.get_remaining_amount(),
                'is_exceeded': budget.is_exceeded(),
            })
            
        return data

    def generate_pdf(self):
        """Generate a PDF report"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import io

        data = self.generate_report_data()
        buffer = io.BytesIO()

        # Create the PDF object
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(data['report_info']['title'], title_style))

        # Add report info
        info_style = ParagraphStyle(
            'CustomInfo',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Report Type: {data['report_info']['type']}", info_style))
        elements.append(Paragraph(f"Period: {data['report_info']['period']}", info_style))
        elements.append(Paragraph(f"Generated At: {time.strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        elements.append(Spacer(1, 20))

        # Add summary
        summary_style = ParagraphStyle(
            'CustomSummary',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20
        )
        elements.append(Paragraph("Summary", summary_style))

        summary_data = [
            ['Total Income', f"${data['summary']['total_income']}"],
            ['Total Expense', f"${data['summary']['total_expense']}"],
            ['Balance', f"${data['summary']['balance']}"],
            ['Number of Transactions', str(data['summary']['transaction_count'])],
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Add transactions
        if data['transactions']:
            elements.append(Paragraph("Transactions", summary_style))
            transaction_data = [['Date', 'Name', 'Type', 'Amount', 'Category', 'Budget']]
            for transaction in data['transactions']:
                transaction_data.append([
                    transaction['date'],
                    transaction['name'],
                    transaction['type'],
                    f"${transaction['amount']}",
                    transaction['category'],
                    transaction['budget'],
                ])

            transaction_table = Table(transaction_data, colWidths=[1*inch, 1.5*inch, 0.75*inch, 0.75*inch, 1*inch, 1*inch])
            transaction_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(transaction_table)
            elements.append(Spacer(1, 20))

        # Add budgets
        if data['budgets']:
            elements.append(Paragraph("Budgets", summary_style))
            budget_data = [['Type', 'Amount', 'Spent', 'Remaining', 'Status']]
            for budget in data['budgets']:
                budget_data.append([
                    budget['type'],
                    f"${budget['amount']}",
                    f"${budget['spent']}",
                    f"${budget['remaining']}",
                    'Exceeded' if budget['is_exceeded'] else 'Normal',
                ])

            budget_table = Table(budget_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            budget_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(budget_table)

        # Generate PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
