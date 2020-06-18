from django.db import models
from django.conf import settings
# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100)

class Movie(models.Model):
    poster_path = models.TextField()
    adult = models.BooleanField()
    overview = models.TextField()
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre,related_name='movies')
    original_title = models.CharField(max_length=300)
    original_language = models.CharField(max_length=20)
    title = models.CharField(max_length=500)
    backdrop_path = models.TextField()
    popularity = models.FloatField()
    vote_count = models.IntegerField()
    video = models.BooleanField()
    vote_average = models.FloatField()
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies')
    world_cup = models.IntegerField(default=0)

class Article(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.IntegerField(default=10)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)