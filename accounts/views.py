from django.shortcuts import render, redirect
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import (
    CustomUserCreationForm, ProfileUpdateForm, PasswordChangeForm,
    CustomAuthenticationForm, PasswordResetForm, SetPasswordForm
)
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. Please check your email to verify your account.')
        return response

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.first_name}!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    return render(request, 'accounts/delete_account.html')

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    from_email = settings.DEFAULT_FROM_EMAIL
    domain_override = settings.SITE_DOMAIN
    protocol = 'http' if settings.DEBUG else 'https'
    extra_email_context = {
        'domain': settings.SITE_DOMAIN,
        'protocol': 'http' if settings.DEBUG else 'https'
    }

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

class DeleteAccountView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/delete_account.html')

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('accounts:profile')
        
        # Delete all user data
        user = request.user
        
        # Delete all budgets and related transactions
        budgets = user.budgets.all()
        for budget in budgets:
            budget.transactions.all().delete()
        budgets.delete()
        
        # Delete all categories
        user.categories.all().delete()
        
        # Delete the user
        user.delete()
        
        # Logout the user
        logout(request)
        
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('home')
