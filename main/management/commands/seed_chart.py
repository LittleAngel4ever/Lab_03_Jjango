from django.core.management.base import BaseCommand
from main.models import ChartTrack
from main.soundcharts_api import get_top_tracks
from main.gridfs_utils import save_image, get_gridfs
import requests
from io import BytesIO

def download_image_from_loremflickr(seed):
    url = f"https://loremflickr.com/300/300/music?random={seed}"
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'DjangoChart/1.0'})
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Ошибка загрузки изображения для seed={seed}: {e}")
        return None

def generate_fallback_cover(track_index):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (300, 300), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    draw.text((80, 140), f"Track {track_index}", fill="white")
    buf = BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

class Command(BaseCommand):
    help = 'Загружает треки и скачивает обложки из LoremFlickr в GridFS'

    def handle(self, *args, **options):
        fs = get_gridfs()
        for file in fs.find():
            fs.delete(file._id)

        ChartTrack.objects.all().delete()

        tracks = get_top_tracks(limit=50)
        for idx, t in enumerate(tracks, start=1):
            image_data = download_image_from_loremflickr(seed=idx)
            if image_data is None:
                self.stdout.write(self.style.WARNING(
                    f"Не удалось загрузить обложку для трека {idx}, использую заглушку."
                ))
                image_data = generate_fallback_cover(idx)

            file_id = save_image(image_data, f"track_{idx}.jpg")

            ChartTrack.objects.create(
                title=t['title'],
                artist=t['artist'],
                genre=t['genre'],
                release_year=t['release_year'],
                cover_image_id=str(file_id),
                lyrics=t['lyrics'],
                artist_info=t['artist_info'],
            )

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(tracks)} треков с обложками из LoremFlickr'))
