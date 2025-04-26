from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pet
from weight_tracker_app.models import Weight

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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 폼에서 빈 값/0이 들어오면 최근 체중 기록에서 자동 입력
        weight_val = self.cleaned_data.get('weight')
        if weight_val in [None, '', 0]:
            latest_weight = Weight.objects.filter(pet=instance).order_by('-date').first()
            if latest_weight:
                instance.weight = latest_weight.weight
            else:
                instance.weight = None
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'breed', 'birth_date', 'weight', 'image']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        } 