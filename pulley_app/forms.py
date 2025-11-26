from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from .models import CustomUser,profile
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = profile
        fields = ['user', 'profile_photo', 'mobile_number', 'address']

CHART_TEMPERATURES = [10, 15, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50]
CHART_HTL_VALUES = [200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725, 750, 775, 800]

TEMP_CHOICES = [(str(t), f"{t} °C") for t in CHART_TEMPERATURES]
HTL_CHOICES = [(str(v), f"{v} m") for v in CHART_HTL_VALUES]


class ImageUploadForm(forms.Form):
    image = forms.ImageField(label="Upload Image")
    temperature = forms.ChoiceField(
        label="Ambient Temp (°C)",
        choices=TEMP_CHOICES,
        initial=str(35),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a temperature value from the adjustment chart."
    )
    htl = forms.ChoiceField(
        label="HTL (L/2) Value",
        choices=HTL_CHOICES,
        initial=str(400),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the HTL (L/2) value (200–800) from the chart."
    )
    
    




    
from django import forms
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from .models import CustomUser
from django import forms


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'employee_id', 'password', 'confirm_password']

        # ✅ Widgets must be defined inside Meta
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
            }),
            'employee_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID',
            }),
        }

    # ✅ Password validation logic
    # 
    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if CustomUser.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("This employee ID is already in use.")
        return employee_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Password and Confirm Password do not match.")
        
# class LoginForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email',
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        }),
        label="Password"
    )


class passwordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter old password',
        }),
        label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
        }),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
        }),
        label="Confirm New Password"
    )