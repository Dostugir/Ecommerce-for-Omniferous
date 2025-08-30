from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import LoginForm

User = get_user_model()

class CustomLoginForm(LoginForm):
    def clean(self):
        # Call the parent class's clean method first to let allauth handle basic validation
        super_cleaned_data = super().clean()
        
        login_value = self.cleaned_data.get('login')
        
        if login_value:
            # Check if a user with this email/username exists
            # Since ACCOUNT_LOGIN_METHOD is 'email', we primarily check for email existence.
            user_exists = User.objects.filter(email__iexact=login_value).exists()

            if not user_exists:
                raise forms.ValidationError(
                    "No account found with this email address. Please check your email or sign up."
                )
            else:
                # If user exists, check if they are active
                user = User.objects.get(email__iexact=login_value)
                if not user.is_active:
                    raise forms.ValidationError(
                        "Your account is not active. Please check your email for a verification link or contact support."
                    )
        
        # Call the parent class's clean method to continue allauth's validation
        # This is called here after our custom validation to ensure allauth's
        # own checks (like password validation) are performed.
        return super().clean()
