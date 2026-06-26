from bson import ObjectId
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.template.loader import render_to_string
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .models import ChartTrack, Vote


def index(request):
    tracks = list(ChartTrack.objects.all().order_by('-rating', '-votes_count')[:20])
    for track in tracks:
        track.cover_b64 = track.cover_base64()
        track.filled_stars = int(track.rating)
    return render(request, 'main/index.html', {
        'tracks': tracks,
        'score_range': range(1, 11),
    })

def load_more_tracks(request):
    page = int(request.GET.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    tracks = list(ChartTrack.objects.all().order_by('-rating', '-votes_count')[offset:offset + per_page])
    for track in tracks:
        track.cover_b64 = track.cover_base64()
        track.filled_stars = int(track.rating)
    html = render_to_string('main/includes/track_card.html', {
        'tracks': tracks,
        'score_range': range(1, 11),
    }, request=request)
    has_next = ChartTrack.objects.count() > offset + per_page
    return JsonResponse({'html': html, 'has_next': has_next})

def track_detail(request, track_id):
    try:
        obj_id = ObjectId(track_id)
    except Exception:
        raise Http404("Некорректный идентификатор трека")
    track = get_object_or_404(ChartTrack, pk=obj_id)
    track.cover_b64 = track.cover_base64()
    track.filled_stars = int(track.rating)
    return render(request, 'main/track_detail.html', {
        'track': track,
        'score_range': range(1, 11),
    })

@user_passes_test(lambda u: u.is_staff)
def add_track(request):
    if request.method == 'POST':
        cover_url = request.POST.get('cover_image_url', '').strip()
        track = ChartTrack.objects.create(
            title=request.POST.get('title'),
            artist=request.POST.get('artist'),
            genre=request.POST.get('genre'),
            release_year=int(request.POST.get('release_year', 0)),
            lyrics=request.POST.get('lyrics', ''),
            artist_info=request.POST.get('artist_info', ''),
            cover_image_url=cover_url,
        )
        if cover_url:
            try:
                import requests as req
                response = req.get(cover_url, timeout=10,
                                   headers={'User-Agent': 'DjangoChart/1.0'})
                if response.status_code == 200:
                    from .gridfs_utils import save_image
                    file_id = save_image(response.content, f"uploaded_{track.pk}.jpg")
                    track.cover_image_id = str(file_id)
                    track.cover_image_url = ''
                    track.save()
            except Exception:
                pass
        return redirect('index')
    return render(request, 'main/add_track.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна. Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
@require_POST
def vote_track(request, track_id):
    try:
        obj_id = ObjectId(track_id)
    except Exception:
        return JsonResponse({'error': 'Неверный идентификатор трека'}, status=400)

    track = get_object_or_404(ChartTrack, pk=obj_id)

    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body)
        score = int(data.get('score', 0))
    else:
        score = int(request.POST.get('score', 0))

    if score < 1 or score > 10:
        return JsonResponse({'error': 'Неверная оценка'}, status=400)

    if Vote.objects.filter(user=request.user, track_id=str(track.pk)).exists():
        return JsonResponse({'error': 'Вы уже голосовали'}, status=403)

    try:
        Vote.objects.create(user=request.user, track_id=str(track.pk), score=score)
    except IntegrityError:
        return JsonResponse({'error': 'Вы уже голосовали'}, status=403)

    votes = Vote.objects.filter(track_id=str(track.pk))
    count = votes.count()
    avg = sum(v.score for v in votes) / count
    track.rating = round(avg, 2)
    track.votes_count = count
    track.save()

    return JsonResponse({
        'success': True,
        'new_rating': track.rating,
        'new_votes_count': track.votes_count
    })

def track_cover(request, track_id):
    track = get_object_or_404(ChartTrack, pk=ObjectId(track_id))
    if not track.cover_image_id:
        raise Http404("Обложка отсутствует")
    from .gridfs_utils import get_image as get_gridfs_image
    img_data = get_gridfs_image(ObjectId(track.cover_image_id))
    if not img_data:
        raise Http404("Файл обложки не найден")
    return HttpResponse(img_data, content_type='image/jpeg')
