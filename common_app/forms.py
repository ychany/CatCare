from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pet

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PetForm(forms.ModelForm):
    breed = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pet_type = self.data.get('pet_type') if self.data else (self.instance.pet_type if self.instance else None)
        
        if pet_type == 'cat':
            self.fields['breed'].choices = Pet.CAT_BREEDS
        elif pet_type == 'dog':
            self.fields['breed'].choices = Pet.DOG_BREEDS
        else:
            self.fields['breed'].choices = [('', '동물 종류를 먼저 선택해주세요')]

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'breed', 'birth_date', 'image']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        } 