from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, PetForm
from .models import Pet
from board_app.models import Post

# Create your views here.

def index(request):
    context = {}
    if request.user.is_authenticated:
        pets = Pet.objects.filter(owner=request.user)
        recent_posts = Post.objects.filter(image__isnull=False).order_by('-created_at')[:12]
        context.update({
            'pets': pets,
            'recent_posts': recent_posts
        })
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        pet_form = PetForm(request.POST, request.FILES)
        if user_form.is_valid() and pet_form.is_valid():
            user = user_form.save()
            pet = pet_form.save(commit=False)
            pet.owner = user
            pet.save()
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        pet_form = PetForm()
    return render(request, 'register.html', {'user_form': user_form, 'pet_form': pet_form})

@login_required
def pet_edit(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, '반려동물 정보가 수정되었습니다.')
            return redirect('index')
    else:
        form = PetForm(instance=pet)
    return render(request, 'common_app/pet_edit.html', {'form': form, 'pet': pet})

@login_required
def pet_update(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, '반려동물 정보가 수정되었습니다.')
            return redirect('index')
    return redirect('pets:edit', pet_id=pet_id)

@login_required
def pet_register(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, '반려동물이 등록되었습니다.')
            return redirect('index')
    else:
        form = PetForm()
    return render(request, 'common_app/pet_register.html', {'form': form})
