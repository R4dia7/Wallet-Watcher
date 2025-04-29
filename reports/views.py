from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import json

from .models import Report
from .forms import ReportFilterForm, ReportForm, StandardReportForm

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/list.html'
    context_object_name = 'reports'
    paginate_by = 10

    def get_queryset(self):
        queryset = Report.objects.filter(user=self.request.user)
        
        # Apply filters
        filter_form = ReportFilterForm(self.request.GET)
        if filter_form.is_valid():
            report_type = filter_form.cleaned_data.get('report_type')
            date_range = filter_form.cleaned_data.get('date_range')
            sort_by = filter_form.cleaned_data.get('sort_by')

            if report_type:
                queryset = queryset.filter(report_type=report_type)

            if date_range:
                today = timezone.now().date()
                if date_range == 'day':
                    queryset = queryset.filter(created_at__date=today)
                elif date_range == 'week':
                    start_date = today - timedelta(days=today.weekday())
                    queryset = queryset.filter(created_at__date__range=[start_date, today])
                elif date_range == 'month':
                    start_date = today.replace(day=1)
                    queryset = queryset.filter(created_at__date__range=[start_date, today])
                elif date_range == 'year':
                    start_date = today.replace(month=1, day=1)
                    queryset = queryset.filter(created_at__date__range=[start_date, today])

            if sort_by:
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-created_at')

        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ReportFilterForm(self.request.GET)
        return context


@login_required
def report_dashboard(request):
    """Main reports dashboard with time period selection"""
    # Set default report type
    report_type = request.session.get('report_type', 'daily')
    period_offset = request.session.get('period_offset', 0)
    sort_by = request.session.get('sort_by', 'date_desc')
    
    # Handle form submission
    if request.method == 'POST':
        if 'report_type' in request.POST:
            report_type = request.POST.get('report_type')
            request.session['report_type'] = report_type
            request.session['period_offset'] = 0
            period_offset = 0
            
        if 'sort_by' in request.POST:
            sort_by = request.POST.get('sort_by')
            request.session['sort_by'] = sort_by
            
        # Handle navigation actions
        action = request.POST.get('action')
        if action == 'reset':
            request.session['period_offset'] = 0
            period_offset = 0
        elif action == 'prev':
            period_offset = request.session.get('period_offset', 0) - 1
            request.session['period_offset'] = period_offset
        elif action == 'next':
            period_offset = request.session.get('period_offset', 0) + 1
            request.session['period_offset'] = period_offset
    
    # Calculate date range
    form = StandardReportForm(initial={'sort_by': sort_by})
    start_date, end_date = form.get_date_range(report_type, period_offset)
    
    # Prepare period display text
    if report_type == 'daily':
        period_text = start_date.strftime('%B %d, %Y')
    elif report_type == 'weekly':
        period_text = f"Week of {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    elif report_type == 'monthly':
        period_text = start_date.strftime('%B %Y')
    else:  # yearly
        period_text = start_date.strftime('%Y')
    
    # Get report data
    report_data = generate_report_data(request.user, report_type, start_date, end_date, sort_by)
    chart_data = json.dumps(report_data['chart_data'], cls=DjangoJSONEncoder)
    report_data.pop('chart_data', None)
    
    # Get existing reports
    saved_reports = Report.objects.filter(
        user=request.user, 
        report_type=report_type
    ).order_by('-created_at')[:5]
    
    context = {
        'report_type': report_type,
        'report_types': Report.REPORT_TYPES,
        'period_offset': period_offset,
        'period_text': period_text,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'sort_options': Report.SORT_OPTIONS,
        'report_data': report_data,
        'chart_data': chart_data,  # Add the properly encoded JSON
        'saved_reports': saved_reports,
        'standard_report_form': form,
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def create_standard_report(request, report_type):
    """Create a standard report (daily, weekly, monthly, yearly)"""
    if report_type not in dict(Report.REPORT_TYPES):
        messages.error(request, "Invalid report type.")
        return redirect('reports:overview')
    
    if request.method == 'POST':
        form = StandardReportForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            period_offset = form.cleaned_data.get('period_offset', 0)
            sort_by = form.cleaned_data['sort_by']
            
            # Calculate date range
            start_date, end_date = form.get_date_range(report_type, period_offset)
            
            # Create the report
            report = Report.objects.create(
                user=request.user,
                title=title,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                sort_by=sort_by,
                transaction_types=['income', 'expense'],
            )
            
            messages.success(request, f"{report.get_report_type_display()} created successfully.")
            return redirect('reports:detail', pk=report.pk)
    else:
        # Get current period offset from session
        period_offset = request.session.get('period_offset', 0)
        
        # Generate default title
        form = StandardReportForm(initial={
            'period_offset': period_offset,
            'sort_by': request.session.get('sort_by', 'date_desc'),
        })
        start_date, end_date = form.get_date_range(report_type, period_offset)
        
        # Create a default title based on report type and period
        if report_type == 'daily':
            default_title = f"Daily Report - {start_date.strftime('%B %d, %Y')}"
        elif report_type == 'weekly':
            default_title = f"Weekly Report - {start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}"
        elif report_type == 'monthly':
            default_title = f"Monthly Report - {start_date.strftime('%B %Y')}"
        else:  # yearly
            default_title = f"Yearly Report - {start_date.strftime('%Y')}"
        
        form = StandardReportForm(initial={
            'title': default_title,
            'period_offset': period_offset,
            'sort_by': request.session.get('sort_by', 'date_desc'),
        })
    
    return render(request, 'reports/standard_report_form.html', {
        'form': form,
        'report_type': report_type,
        'report_type_display': dict(Report.REPORT_TYPES)[report_type],
    })


@login_required
def create_custom_report(request):
    """Create a custom report with specific date range and filters"""
    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # Extract the data from form
                report = form.save(commit=False)
                report.user = request.user
                report.report_type = 'custom'
                
                if not timezone.is_aware(report.start_date):
                    report.start_date = timezone.make_aware(report.start_date)
                if not timezone.is_aware(report.end_date):
                    report.end_date = timezone.make_aware(report.end_date)
                
                report.save()
                form.save_m2m()
                
                messages.success(request, "Custom report created successfully.")
                return redirect('reports:detail', pk=report.pk)
            except Exception as e:
                messages.error(request, f"Error creating report: {str(e)}")
                print(f"Error in create_custom_report: {str(e)}")
        else:
            # Print form errors to help debug
            print(f"Form errors: {form.errors}")
            messages.error(request, "There was an error with your form submission. Please check the form and try again.")
    else:
        # Default to current month for date range
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
        
        form = ReportForm(
            user=request.user,
            initial={
                'title': f"Custom Report - {start_date.strftime('%B %Y')}",
                'start_date': start_date,
                'end_date': end_date,
                'sort_by': 'date_desc',
                'transaction_types': ['income', 'expense'],  # Include all by default
            }
        )
    
    return render(request, 'reports/custom_report_form.html', {
        'form': form,
    })

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        report_data = self.object.generate_report_data()
        chart_data = json.dumps(report_data['chart_data'], cls=DjangoJSONEncoder)
        print(chart_data)
        report_data.pop('chart_data', None)
        context = super().get_context_data(**kwargs)
        context['report_data'] = report_data
        context['chart_data'] = chart_data
        return context


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('reports:list')
    
    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Report'
        context['message'] = f'Are you sure you want to delete the report "{self.object.title}"?'
        context['back_url'] = 'reports:list'
        return context


@login_required
def download_report(request, pk):
    """Download a report as PDF"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    pdf_file = report.generate_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.title.replace(" ", "_")}.pdf"'
    return response


def generate_report_data(user, report_type, start_date, end_date, sort_by='date_desc'):
    """Generate report data for the given period without saving a report"""
    # Create a temporary report to use its data generation methods
    temp_report = Report(
        user=user,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        transaction_types=['income', 'expense'],
    )
    
    return temp_report.generate_report_data()
