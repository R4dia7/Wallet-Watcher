from django.contrib import messages
from .models import Budget
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BudgetForm

@login_required
def budget_list(request):
    BUDGET_TYPES = ['daily', 'weekly', 'monthly', 'yearly']
    budgets = {budget.budget_type: budget for budget in Budget.objects.filter(user=request.user)}
    
    return render(request, 'budgets/list.html', {
        'budget_types': BUDGET_TYPES,
        'budgets': budgets,
    })

@login_required
def budget_create(request):
    budget_type = request.GET.get('type')
    if not budget_type or budget_type not in ['daily', 'weekly', 'monthly', 'yearly']:
        messages.error(request, 'Invalid budget type.')
        return redirect('budgets:budget_list')
    
    if Budget.objects.filter(user=request.user, budget_type=budget_type).exists():
        messages.error(request, f'{budget_type.title()} budget already exists.')
        return redirect('budgets:budget_list')
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.budget_type = budget_type
            budget.save()
            messages.success(request, f'{budget_type.title()} budget created successfully.')
            return redirect('budgets:budget_list')
    else:
        form = BudgetForm()
    
    return render(request, 'form.html', {
        'form': form,
        'title': f'Set {budget_type.title()} Budget',
        'back_url': 'budgets:budget_list',
    })

@login_required
def budget_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, f'{budget.get_budget_type_display()} budget updated successfully.')
            return redirect('budgets:budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'form.html', {
        'form': form,
        'title': f'Update {budget.get_budget_type_display()} Budget',
        'back_url': 'budgets:budget_list',
    })

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    name = f'{budget.get_budget_type_display()} Budget'
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully.')
        return redirect('budgets:budget_list')
    
    return render(request, 'confirm_delete.html', {
        'model_name': name,
        'title': f'Delete {budget.get_budget_type_display()} Budget',
        'back_url': 'budgets:budget_list',
    })