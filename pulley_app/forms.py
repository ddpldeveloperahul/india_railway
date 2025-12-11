from django import forms
from django.core.exceptions import ValidationError
from django import forms
 
CHART_TEMPERATURES = [10, 15, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50]
CHART_HTL_VALUES = [200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725, 750, 775, 800]

TEMP_CHOICES = [(str(t), f"{t} °C") for t in CHART_TEMPERATURES]
HTL_CHOICES = [(str(v), f"{v} m") for v in CHART_HTL_VALUES]


class ImageUploadForm(forms.Form):
    image = forms.ImageField(label="Upload Image")
    pole_name = forms.CharField(
        label="Pole Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the name/identifier of the pole (optional)"
    )
    # temperature = forms.ChoiceField(
    #     label="Ambient Temp (°C)",
    #     choices=TEMP_CHOICES,
    #     initial=str(35),
    #     widget=forms.Select(attrs={'class': 'form-select'}),
    #     help_text="Select a temperature value from the adjustment chart."
    # )
    temperature = forms.ChoiceField(
        label="Ambient Temp (°C)",
        choices=TEMP_CHOICES,
        initial=str(35),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Select a temperature value from the adjustment chart."
    )
    htl = forms.ChoiceField(
        label="HTL (L/2) Value",
        choices=HTL_CHOICES,
        initial=str(400),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the HTL (L/2) value (200–800) from the chart."
    )
    
    
class Upload_htl_temp(forms.Form):
    pole_name = forms.CharField(
        label="Pole Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the name/identifier of the pole (optional)"
    )
    # temperature = forms.ChoiceField(
    #     label="Ambient Temp (°C)",
    #     choices=TEMP_CHOICES,
    #     initial=str(35),
    #     widget=forms.Select(attrs={'class': 'form-select'}),
    #     help_text="Select a temperature value from the adjustment chart."
    # )
    temperature = forms.ChoiceField(
        label="Ambient Temp (°C)",
        choices=TEMP_CHOICES,
        initial=str(35),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Select a temperature value from the adjustment chart."
    )
    htl = forms.ChoiceField(
        label="HTL (L/2) Value",
        choices=HTL_CHOICES,
        initial=str(400),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the HTL (L/2) value (200–800) from the chart."
    )
    
    
    

