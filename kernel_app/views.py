import base64
from django.shortcuts import render
from kernel_app.forms import LoginForm, NewCard, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, get_object_or_404, redirect
from kernel_app.models import Card, Vote

# Create your views here.
def registration_page(request):
    form = RegistrationForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            newUser = form.save(commit=False)
            newUser.set_password(form.cleaned_data['password1'])
            newUser.save()
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})

def login_page(request):
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main')
    return render(request, 'login.html', {'form': form})

def main_page(request):
    cardList = Card.objects.all()
    for card in cardList:
        image_data = card.photo.file.read()
        card.imageBase = base64.b64encode(image_data).decode('utf-8')
    return render(request, 'main.html', {'cardList': cardList})

@login_required
@staff_member_required
def new_card_page(request):
    if request.method == 'POST':
        form = NewCard(request.POST, request.FILES)
        if form.is_valid():
            card = Card.objects.create(
                photo=form.cleaned_data['photo'],
                artist=form.cleaned_data['artist'],
                title=form.cleaned_data['title'],
                genre=form.cleaned_data['genre'],
                release_year=form.cleaned_data['release_year'],
                rating=0.0,
                votes=0
            )
            card.save()
    form = NewCard()
    return render(request, 'newCard.html', {'form': form})

@login_required
def card_page(request, id):
    track = get_object_or_404(Card, id=id)
    image_data = track.photo.file.read()
    track.imageBase = base64.b64encode(image_data).decode('utf-8')
    
    user_vote = Vote.objects.filter(
        user_id=request.user.id, 
        card_id=str(track.id)
    ).first()
    
    if request.method == 'POST' and not user_vote:
        score = request.POST.get('score')
        score = int(score)
        
        Vote.objects.create(
            user_id=request.user.id,
            card_id=str(track.id),
            score=score
        )
        
        total_rating = track.rating * track.votes
        track.votes += 1
        track.rating = (total_rating + score) / track.votes
        track.save()
            
        return redirect('card_page', id=id)
    
    return render(request, 'card.html', {
        'track': track,
        'user_vote': user_vote.score if user_vote else None,
        'score_range': range(1, 11)
    })

def logout_page(request):
    logout(request)
    return redirect('login')