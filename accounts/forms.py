from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
    PasswordResetForm as DjangoPasswordResetForm,
    SetPasswordForm as DjangoSetPasswordForm
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        if len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        return password2

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(email=username).exists():
            raise ValidationError(_("No account found with this email address."))
        return username

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'phone_number',
                 'profile_picture', 'theme_preference', 'email_notifications')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(
        label=_("Current password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        field_order = ['email', 'first_name', 'last_name', 'current_password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email field read-only
        self.fields['email'].widget.attrs.update({
            'readonly': 'readonly',
            'class': 'bg-gray-100 dark:bg-gray-700'
        })
        self.fields['email'].required = False

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.instance.check_password(current_password):
            raise ValidationError(_("Your current password was entered incorrectly. Please enter it again."))
        return current_password

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class PasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label=_("Current password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        if len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        return password2

class PasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_("No account found with this email address."))
        return email

class SetPasswordForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        if len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        return password2 