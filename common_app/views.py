from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, PetForm
from .models import Pet
from board_app.models import Post
from weight_tracker_app.models import Weight
from django.contrib.auth import logout

# Create your views here.

@login_required
def index(request):
    context = {}
    if request.user.is_authenticated:
        pets = Pet.objects.filter(owner=request.user)
        recent_posts = Post.objects.filter(image__isnull=False, pet__owner=request.user).order_by('-created_at')[:12]
        context.update({
            'pets': pets,
            'recent_posts': recent_posts,
            'pet_form': PetForm(),
        })
    return render(request, 'common_app/index.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            # 여러 마리 고양이 정보 저장
            pet_idx = 0
            while True:
                name = request.POST.get(f'pet_name_{pet_idx}')
                breed = request.POST.get(f'pet_breed_{pet_idx}')
                birth_date = request.POST.get(f'pet_birth_date_{pet_idx}')
                gender = request.POST.get(f'pet_gender_{pet_idx}')
                neutered = request.POST.get(f'pet_neutered_{pet_idx}')
                weight = request.POST.get(f'pet_weight_{pet_idx}')
                notes = request.POST.get(f'pet_notes_{pet_idx}')
                image = request.FILES.get(f'pet_image_{pet_idx}')
                if not name:
                    break
                Pet.objects.create(
                    owner=user,
                    name=name,
                    pet_type='cat',
                    breed=breed,
                    birth_date=birth_date,
                    weight=weight or None,
                    image=image,
                )
                pet_idx += 1
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
    # pet_form 추가
    pet_form = PetForm()
    return render(request, 'common_app/register.html', {
        'user_form': user_form,
        'pet_form': pet_form,
        'pet_breeds': Pet.CAT_BREEDS,
    })

@login_required
def pet_edit(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    latest_weight = Weight.objects.filter(pet=pet).order_by('-date').first()
    initial = {}
    if latest_weight:
        initial['weight'] = latest_weight.weight
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, '반려동물 정보가 수정되었습니다.')
            return redirect('index')
    else:
        form = PetForm(instance=pet, initial=initial)
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
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        neutered = request.POST.get('neutered')
        weight = request.POST.get('weight')
        notes = request.POST.get('notes')
        image = request.FILES.get('image')
        Pet.objects.create(
            owner=request.user,
            name=name,
            pet_type='cat',
            breed=breed,
            birth_date=birth_date,
            weight=weight or None,
            image=image,
        )
        messages.success(request, '반려동물이 등록되었습니다.')
        return redirect('index')
    else:
        form = PetForm()
    return render(request, 'common_app/pet_register.html', {'form': form})

@login_required
def pet_delete(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        pet.delete()
        return redirect('index')
    return render(request, 'common_app/pet_confirm_delete.html', {'pet': pet})

# 로그아웃 후 로그인 페이지로 리다이렉트하는 커스텀 뷰
def custom_logout_view(request):
    logout(request)
    return redirect('login')
