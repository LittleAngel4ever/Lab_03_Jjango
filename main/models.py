from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import base64


class ChartTrack(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    release_year = models.IntegerField()
    cover_image_id = models.CharField(max_length=50, blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True)
    lyrics = models.TextField(blank=True)
    artist_info = models.TextField(blank=True, verbose_name="Информация об исполнителе")
    rating = models.FloatField(default=0.0)
    votes_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'chart_tracks'

    def __str__(self):
        return f"{self.artist} - {self.title}"
    
    def cover_base64(self):
        if not self.cover_image_id:
            return ''
        try:
            from .gridfs_utils import get_image
            img_data = get_image(ObjectId(self.cover_image_id))
            if img_data:
                return base64.b64encode(img_data).decode('utf-8')
        except Exception:
            pass
        return ''

    @property
    def cover_url(self):
        if self.cover_image_id:
            return f'/track/{self.pk}/cover/'
        return self.cover_image_url or ''

@receiver(pre_delete, sender=ChartTrack)
def delete_track_cover(sender, instance, **kwargs):
    if instance.cover_image_id:
        from .gridfs_utils import delete_image
        try:
            delete_image(ObjectId(instance.cover_image_id))
        except:
            pass

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=50)
    score = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track_id')
        indexes = [
            models.Index(fields=['user', 'track_id']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.track_id}: {self.score}"
