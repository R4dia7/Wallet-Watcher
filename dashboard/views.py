from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Case, When, F, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime, time
from budgets.models import Budget
from transactions.models import Category, Transaction
from .models import Dashboard

@login_required
def dashboard(request):
    # Get or create dashboard settings
    dashboard_settings, created = Dashboard.objects.get_or_create(user=request.user)
    
    # Handle time period change and navigation
    if request.method == 'POST':
        time_period = request.POST.get('time_period')
        action = request.POST.get('action')
        
        if time_period in dict(Dashboard.TIME_PERIOD_CHOICES):
            dashboard_settings.time_period = time_period
            dashboard_settings.save()
        
        # Handle navigation actions
        if action == 'reset':
            request.session['period_offset'] = 0
        elif action == 'prev':
            period_offset = request.session.get('period_offset', 0)
            period_offset -= 1
            request.session['period_offset'] = period_offset
        elif action == 'next':
            period_offset = request.session.get('period_offset', 0)
            period_offset += 1
            request.session['period_offset'] = period_offset
    
    # Calculate date range based on time period
    today = timezone.now().date()
    
    # Get the current period offset from the session or default to 0
    period_offset = request.session.get('period_offset', 0)
    
    # Calculate the target date based on the offset
    if dashboard_settings.time_period == 'daily':
        target_date = today + timedelta(days=period_offset)
        start_date = target_date
        end_date = target_date
    elif dashboard_settings.time_period == 'weekly':
        target_date = today + timedelta(weeks=period_offset)
        start_date = target_date - timedelta(days=target_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif dashboard_settings.time_period == 'monthly':
        # Calculate target month and year
        target_month = today.month + period_offset
        target_year = today.year
        
        # Adjust year if month goes out of range
        while target_month > 12:
            target_month -= 12
            target_year += 1
        while target_month < 1:
            target_month -= 12
            target_year -= 1
            
        start_date = today.replace(year=target_year, month=target_month, day=1)
        if target_month == 12:
            end_date = start_date.replace(day=31)
        else:
            end_date = start_date.replace(month=target_month + 1, day=1) - timedelta(days=1)
    else:  # yearly
        target_year = today.year + period_offset
        start_date = today.replace(year=target_year, month=1, day=1)
        end_date = start_date.replace(month=12, day=31)
    
    # Get budgets for the user that match the current time period
    budgets = Budget.objects.filter(
        user=request.user,
        budget_type=dashboard_settings.time_period
    )
    
    # Calculate budget statuses
    budget_statuses = []
    total_budget = 0
    total_spent = 0
    total_income = 0
    
    for budget in budgets:
        # Calculate spent amount for the period
        spent_amount = Transaction.objects.filter(
            user=request.user,
            budget=budget,
            date__range=[start_date, end_date],
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate income for the period
        income = Transaction.objects.filter(
        user=request.user, 
            budget=budget,
            date__range=[start_date, end_date],
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
        # Calculate percentage spent
        percentage_spent = (spent_amount / budget.amount * 100) if budget.amount > 0 else 0
        
        # Determine status
        is_exceeded = spent_amount > budget.amount
        status_class = 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' if is_exceeded else 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
        
        budget_statuses.append({
            'budget': budget,
            'spent_amount': spent_amount,
            'income': income,
            'percentage_spent': percentage_spent,
            'is_exceeded': is_exceeded,
            'status_class': status_class
        })
        
        total_budget += budget.amount
        total_spent += spent_amount
        total_income += income
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')[:5]
    
    # Get top categories
    top_categories = Category.objects.filter(
        user=request.user, 
        category_transactions__date__range=[start_date, end_date],
        category_transactions__type='expense'
    ).annotate(
        total_spent=Sum('category_transactions__amount')
    ).order_by('-total_spent')[:5]
    
    # Calculate overall totals (across all time)
    overall_totals = Transaction.objects.filter(user=request.user).aggregate(
        total_income=Sum(
            Case(
                When(type='income', then=F('amount')),
                default=0,
                output_field=DecimalField(),
            )
        ),
        total_expenses=Sum(
            Case(
                When(type='expense', then=F('amount')),
                default=0,
                output_field=DecimalField(),
            )
        )
    )
    
    total_income = overall_totals['total_income'] or 0
    total_expenses = overall_totals['total_expenses'] or 0
    net_balance = total_income - total_expenses
    
    # Calculate balance history for the graph
    balance_history = calculate_balance_history(request.user, start_date, end_date, dashboard_settings.time_period)
    
    context = {
        'dashboard_settings': dashboard_settings,
        'time_periods': Dashboard.TIME_PERIOD_CHOICES,
        'start_date': start_date,
        'end_date': end_date,
        'budget_statuses': budget_statuses,
        'total_budget': total_budget,
        'total_spent': total_expenses,  # Updated to use overall total
        'total_income': total_income,   # Updated to use overall total
        'net_balance': net_balance,     # Added net balance
        'recent_transactions': recent_transactions,
        'top_categories': top_categories,
        'period_offset': period_offset,
        'balance_history': balance_history,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def calculate_balance_history(user, start_date, end_date, time_period):
    """Calculate balance history for the graph based on the time period."""
    # Get all transactions in the date range
    transactions = Transaction.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Initialize balance history
    balance_history = {
        'dates': [],
        'balances': [],
        'time_period': time_period
    }
    
    # Calculate initial balance (sum of all transactions before start_date)
    initial_balance = Transaction.objects.filter(
        user=user,
        date__lt=start_date
    ).aggregate(
        balance=Sum(
            Case(
                When(type='income', then=F('amount')),
                When(type='expense', then=-F('amount')),
                default=0,
                output_field=DecimalField(),
            )
        )
    )['balance'] or 0
    
    current_balance = initial_balance
    
    # Group transactions by day/week/month based on time period
    if time_period == 'daily':
        # For daily view, show hourly balances
        current_date = start_date
        for hour in range(24):
            try:
                hour_start = datetime.combine(current_date, time(hour=hour))
                hour_end = datetime.combine(current_date, time(hour=hour + 1))
                
                # continue if hour is invalid
                
                if not hour_start or not hour_end:
                    continue
                
                # Get transactions for this hour
                hour_transactions = transactions.filter(
                    date__gte=hour_start,
                    date__lt=hour_end
                )
                
                # Calculate balance for this hour
                hour_balance = hour_transactions.aggregate(
                    balance=Sum(
                        Case(
                            When(type='income', then=F('amount')),
                            When(type='expense', then=-F('amount')),
                            default=0,
                            output_field=DecimalField(),
                        )
                    )
                )['balance'] or 0
                
                current_balance += hour_balance
                
                balance_history['dates'].append(hour_start.strftime('%H:00'))
                balance_history['balances'].append(float(current_balance))
            except Exception as e:
                print(f"Error processing hour {hour}: {str(e)}")
                continue
                
    elif time_period == 'weekly':
        # For weekly view, show daily balances
        current_date = start_date
        while current_date <= end_date:
            # Get transactions for this day
            day_transactions = transactions.filter(
                date__date=current_date
            )
            
            # Calculate balance for this day
            day_balance = day_transactions.aggregate(
                balance=Sum(
                    Case(
                        When(type='income', then=F('amount')),
                        When(type='expense', then=-F('amount')),
                        default=0,
                        output_field=DecimalField(),
                    )
                )
            )['balance'] or 0
            
            current_balance += day_balance
            
            balance_history['dates'].append(current_date.strftime('%Y-%m-%d'))
            balance_history['balances'].append(float(current_balance))
            
            current_date += timedelta(days=1)
            
    elif time_period == 'monthly':
        # For monthly view, show daily balances
        current_date = start_date
        while current_date <= end_date:
            # Get transactions for this day
            day_transactions = transactions.filter(
                date__date=current_date
            )
            
            # Calculate balance for this day
            day_balance = day_transactions.aggregate(
                balance=Sum(
                    Case(
                        When(type='income', then=F('amount')),
                        When(type='expense', then=-F('amount')),
                        default=0,
                        output_field=DecimalField(),
                    )
                )
            )['balance'] or 0
            
            current_balance += day_balance
            
            balance_history['dates'].append(current_date.strftime('%Y-%m-%d'))
            balance_history['balances'].append(float(current_balance))
            
            current_date += timedelta(days=1)
            
    else:  # yearly
        # For yearly view, show monthly balances
        current_date = start_date
        while current_date <= end_date:
            # Get transactions for this month
            month_transactions = transactions.filter(
                date__year=current_date.year,
                date__month=current_date.month
            )
            
            # Calculate balance for this month
            month_balance = month_transactions.aggregate(
                balance=Sum(
                    Case(
                        When(type='income', then=F('amount')),
                        When(type='expense', then=-F('amount')),
                        default=0,
                        output_field=DecimalField(),
                    )
                )
            )['balance'] or 0
            
            current_balance += month_balance
            
            balance_history['dates'].append(current_date.strftime('%Y-%m'))
            balance_history['balances'].append(float(current_balance))
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    return balance_history