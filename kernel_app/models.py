from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from gridfs_storage.storage import GridFSStorage
from django.contrib.auth.models import User

# Create your models here.
class Card(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    photo = models.FileField(max_length=500, verbose_name='Фото', storage=GridFSStorage())
    artist = models.CharField(max_length=200, verbose_name='Исполнитель')
    title = models.CharField(max_length=200, verbose_name='Название трека')
    genre = models.CharField(max_length=100, verbose_name='Жанр')
    release_year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')
    votes = models.IntegerField(default=0, verbose_name='Голоса')

    class Meta:
        db_table = 'tracks'
        ordering = ['-rating']

class Vote(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    user_id = models.IntegerField()
    card_id = models.CharField(max_length=50)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'