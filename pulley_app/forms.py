from django import forms
from .models import Image_database
class ImageUploadForm(forms.ModelForm):
    class Mata:
        model = Image_database
        fields = ['image']
    