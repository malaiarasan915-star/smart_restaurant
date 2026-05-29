from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering a new user with custom fields.
    """
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('phone',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """
    Form for editing a CustomUser.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'role', 'table_number')
