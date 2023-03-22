from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Instagram


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'profile_picture', 'email', 'password1', 'password2']


# for admin side
class AccountCreateForm(forms.ModelForm):
    """
        A form for creating new account.
        Includes all the required fields, plus a repeated password.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        instance = super().save(commit=False)

        instance.set_password(self.cleaned_data["password1"])
        if commit:
            instance.save()
        return instance


class AddInstagramForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Instagram
        fields = ['username', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class Add2faInstagramForm(forms.ModelForm):
    twoFACode = forms.IntegerField()

    class Meta:
        model = Instagram
        fields = ('twoFACode',)
