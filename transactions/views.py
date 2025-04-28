from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Transaction
from .forms import CategoryForm, TransactionForm

# Create your views here.

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')
    
    # Calculate summary for all transactions
    summary = Transaction.get_summary(request.user)
    
    return render(request, 'transactions/list.html', {
        'transactions': transactions,
        'summary': summary,
    })

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(user=request.user, data=request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction created successfully.')
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'form.html', {
        'form': form,
        'title': 'Create Transaction',
        'back_url': 'transactions:transaction_list',
    })

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(user=request.user, data=request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm(user=request.user, instance=transaction)
    return render(request, 'form.html', {
        'form': form,
        'title': 'Update Transaction',
        'back_url': 'transactions:transaction_list',
    })

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('transactions:transaction_list')
    return render(request, 'confirm_delete.html', {
        'model_name': 'Transaction',
        'name': f'{transaction.name}"',
        'back_url': 'transactions:transaction_list',
    })

@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'transactions/detail.html', {
        'object': transaction,
        'model_name': 'Transaction',
        'update_url': 'transactions:transaction_update',
        'delete_url': 'transactions:transaction_delete',
        'list_url': 'transactions:transaction_list',
    })

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'transactions/category_list.html', {
        'categories': categories,
    })

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect('transactions:category_list')
    else:
        form = CategoryForm()
    return render(request, 'form.html', {
        'form': form,
        'title': 'Create Category',
        'back_url': 'transactions:category_list',
    })

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('transactions:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'form.html', {
        'form': form,
        'title': 'Update Category',
        'back_url': 'transactions:category_list',
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        # check if category is used in any transactions
        if Transaction.objects.filter(category=category).exists():
            messages.error(request, 'Cannot delete category that is in use.')
            return redirect('transactions:category_list')
        # delete the category
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('transactions:category_list')
    return render(request, 'confirm_delete.html', {
        'model_name': 'Category',
        'name': f'{category.name}"',
        'back_url': 'transactions:category_list',
    })

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    return render(request, 'transactions/detail.html', {
        'object': category,
        'model_name': 'Category',
        'update_url': 'transactions:category_update',
        'delete_url': 'transactions:category_delete',
        'list_url': 'transactions:category_list',
    })
