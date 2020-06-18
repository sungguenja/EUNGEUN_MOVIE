from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib import messages
from .models import Movie, Genre, Article, Comment
from .forms import ArticleForm, CommentForm
import requests
import random

# Create your views here.
def index(request):
    api_key = settings.TMDB_KEY
    data = requests.get('https://api.themoviedb.org/3/movie/now_playing?api_key='+api_key+'&language=ko-KR&page=1&region=KR').json()
    recommend_movies = data['results'][:10]
    pop_movies = Movie.objects.exclude(id=664413).order_by('-popularity')[:6]
    vote_movies = Movie.objects.exclude(id=664413).order_by('-vote_average')[:6]
    articles = Article.objects.order_by('-pk')[:10]
    users_movies = Movie.objects.annotate(q_count=Count('like_users')).order_by('-q_count')[:6]
    random_movie = requests.get('https://api.themoviedb.org/3/movie/upcoming?api_key='+api_key+'&language=ko-KR&page=1&region=KR').json()
    random_movie = random.choice(random_movie['results'])
    api_key = settings.API_SECRET_KEY
    context = {
        'recommend_movies': recommend_movies,
        'pop_movies': pop_movies,
        'vote_movies': vote_movies,
        'articles': articles,
        'users_movies': users_movies,
        'random_movie': random_movie,
        'api_key': api_key
    }
    return render(request,'movies/index.html',context)

def search(request):
    if request.method == 'POST':
        search_value = request.POST['search_value']
        if search_value == '':
            messages.warning(request,'검색창에 검색어를 입력해주세요!')
            return redirect('movies:index')
        else:
            movies = Movie.objects.filter(title__contains=search_value).distinct()
            articles = Article.objects.filter(Q(title__contains=search_value)|Q(content__contains=search_value)).distinct()
            context = {
                'movies': movies,
                'articles': articles
            }
            return render(request,'movies/search.html',context)
    else:
        messages.warning(request,'검색창을 이용해주세요! 💻')
        return redirect('movies:index')

def movie_all(request):
    sort = request.GET.get('sort','')
    if sort == 'vote':
        movies = Movie.objects.annotate(like_count=Count('like_users')).order_by('-vote_average')
    elif sort == 'pop':
        movies = Movie.objects.annotate(like_count=Count('like_users')).order_by('-popularity')
    elif sort == 'likes':
        movies = Movie.objects.annotate(like_count=Count('like_users')).order_by('-like_count')
    else:
        movies = Movie.objects.annotate(like_count=Count('like_users')).order_by('-release_date')
    genres = Genre.objects.order_by('name')
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movies': movies,
        'genres': genres,
        'page_obj': page_obj,
    }
    return render(request,'movies/movie_all.html', context)

def article_list(request):
    articles = Article.objects.order_by('-pk')
    paginator = Paginator(articles,20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'articles': articles,
        'page_obj': page_obj
    }
    return render(request,'articles/article_all.html',context)

def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie.objects.annotate(like_count=Count('like_users')).prefetch_related('article_set'),pk=movie_pk)
    api_key = settings.API_SECRET_KEY
    tmdb_key = settings.TMDB_KEY
    score = 0
    people = 0
    for i in movie.article_set.all():
        score += i.rank
        people += 1
    if people == 0:
        avg_rank = None
    else:
        avg_rank = round(score/people,1)
    context = {
        'movie': movie,
        'api_key': api_key,
        'avg_rank': avg_rank,
        'tmdb_key': tmdb_key
    }
    return render(request, 'movies/movie_detail.html', context)

def movie_like(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie,pk=movie_pk)
        logined = True
        if movie.like_users.filter(id=request.user.pk).exists():
            like = False
            movie.like_users.remove(request.user)
            like_people = len(movie.like_users.all())
        else:
            like = True
            movie.like_users.add(request.user)
            like_people = len(movie.like_users.all())
    else:
        logined = False
        like = False
        like_people = 0
    return JsonResponse({'logined':logined,'like':like,'like_people':like_people})

def article_create(request, movie_pk):
    if request.user.is_anonymous:
        messages.warning(request,'로그인을 해주세요 🙇')
        return redirect('accounts:login')
    else:
        if request.method == 'POST':
            form = ArticleForm(request.POST)
            if form.is_valid():
                movie = get_object_or_404(Movie,pk=movie_pk)
                article = form.save(commit=False)
                article.user = request.user
                article.movie = movie
                article.save()
                return redirect('movies:article_detail', article.pk)
        else:
            form = ArticleForm()
        context = {'form':form}
        return render(request,'articles/create.html',context)

def article_detail(request, article_pk):
    article = get_object_or_404(Article.objects.prefetch_related('comment_set'),pk=article_pk)
    form = CommentForm()
    context = {
        'article': article,
        'form': form
    }
    return render(request,'articles/detail.html',context)

def article_delete(request, article_pk):
    if request.user.is_anonymous:
        messages.warning(request,'이런 로그인을 깜빡하셨군요 😋')
        return redirect('accounts:login')
    article = get_object_or_404(Article,pk=article_pk)
    if request.user != article.user:
        messages.error(request,'다른 유저의 글은 삭제 못해요! 😡')
        return redirect('movies:article_detail',article.pk)
    else:
        if request.method == 'POST':
            article.delete()
            messages.success(request,'성공적으로 삭제 되었습니다! 👍')
            return redirect('movies:index')
        else:
            messages.error(request,'지정한 방식으로 삭제를 부탁드립니다 😭')
            return redirect('movies:article_detail',article.pk)


def article_update(request, article_pk):
    if request.user.is_anonymous:
        messages.warning(request,'이런 로그인을 깜빡하셨군요 😋')
        return redirect('accounts:login')
    article = get_object_or_404(Article,pk=article_pk)
    if article.user != request.user:
        messages.error(request,'다른 유저의 글은 수정할 수가 없습니다! 👿')
        return redirect('movies:article_detail',article.pk)
    else:
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return redirect('movies:article_detail',article.pk)
        else:
            form = ArticleForm(instance=article)
        context = {'form': form }
        return render(request,'articles/create.html',context)

def comment_create(request, article_pk):
    if request.user.is_anonymous:
        messages.error(request,'로그인을 하고 댓글을 써주시길 바랍니다. 😇')
        return redirect('accounts:login')
    else:
        if request.method == 'POST':
            article = get_object_or_404(Article,pk=article_pk)
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.article = article
                comment.save()
                return redirect('movies:article_detail', article.pk)
        else:
            messages.error(request,'댓글작성은 어떻게 들어오셨나요? 🤔')
            return redirect('movies:article_detail', article.pk)

def comment_delete(request, article_pk, comment_pk):
    if request.user.is_anonymous:
        messages.warning(request,'로그인을 하고 댓글삭제를 요청해주세요! 😵')
        return redirect('movies:article_detail',article_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.user != request.user:
        messages.error(request,'남의 댓글은 삭제하실 수가 없는데 뭘 하시는 거죠? 🤔')
        return redirect('movies:article_detail',article_pk)
    else:
        if request.method == 'POST':
            comment.delete()
            messages.success(request,'성공적으로 댓글이 삭제되었습니다!')
        else:
            messages.warning(request,'정해진 방식으로 요청을 보내주세요! 😟')
        return redirect('movies:article_detail',article_pk)

def genre_all(request):
    genres = Genre.objects.all()
    context = {
        'genres': genres
    }
    return render(request,'movies/genre_all.html',context)

def genre_detail(request,genre_pk):
    genre_on = get_object_or_404(Genre,pk=genre_pk)
    sort = request.GET.get('sort','')
    if sort == 'vote':
        movies =  genre_on.movies.annotate(like_count=Count('like_users')).order_by('-vote_average')
    elif sort == 'pop':
        movies =  genre_on.movies.annotate(like_count=Count('like_users')).order_by('-popularity')
    elif sort == 'likes':
        movies =  genre_on.movies.annotate(like_count=Count('like_users')).order_by('-like_count')
    else:
        movies =  genre_on.movies.annotate(like_count=Count('like_users')).order_by('-release_date')
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    genres = Genre.objects.order_by('name')
    context = {
        'movies': movies,
        'page_obj': page_obj,
        'genres': genres,
        'genre_on': genre_on
    }
    return render(request,'movies/movie_all.html', context)

def recommend(request):
    weather_key = settings.WEATHER_KEY
    genres = Genre.objects.all()
    context = {
        'weather_key': weather_key,
        'genres': genres
    }
    return render(request,'recommend/main.html',context)

def recommend_random(request):
    recommend_movies = Movie.objects.filter(adult=False).exclude(genres__in=[27]).exclude(poster_path=None).order_by('?')[:9]
    return JsonResponse({'random_movies':list(recommend_movies.values())})

def recommend_genre(request,genre_pk):
    genre = get_object_or_404(Genre,pk=genre_pk)
    movies = genre.movies.order_by('?')[:3]
    movies = list(movies.values())
    return JsonResponse({'movies':movies, 'genre':genre.name})

def worldcup(request):
    return render(request,'recommend/worldcup.html')

def start_worldcup(request,genre_pk,round_num):
    if genre_pk == 0:
        movies = Movie.objects.order_by('?')[:round_num]
        genre_name = '모든'
    else:
        genre = get_object_or_404(Genre,pk=genre_pk)
        genre_name = genre.name
        movies = genre.movies.order_by('?')[:round_num]
    return JsonResponse({'movies':list(movies.values()),'genre_name':genre_name})

def victory(request,movie_pk):
    movie = get_object_or_404(Movie,pk=movie_pk)
    movie.world_cup += 1
    movie.save()
    movies =  Movie.objects.order_by('-world_cup')[:10]
    return JsonResponse({'movies':list(movies.values())})

def movie_now(request):
    api_key = settings.TMDB_KEY
    data = requests.get('https://api.themoviedb.org/3/movie/now_playing?api_key='+api_key+'&language=ko-KR&page=1&region=KR').json()
    data = data['results'][:9]
    for i in data:
        if Movie.objects.filter(id=i['id']).exists():
            i['db'] = True
        else:
            i['db'] = False
    context = {
        'data': data,
        'title': '현재 상영작'
    }
    return render(request,'cinema/movie_now.html',context)

def movie_upcoming(request):
    api_key = settings.TMDB_KEY
    data = requests.get('https://api.themoviedb.org/3/movie/upcoming?api_key='+api_key+'&language=ko-KR&page=1&region=KR').json()
    data = data['results'][:9]
    for i in data:
        if Movie.objects.filter(id=i['id']).exists():
            i['db'] = True
        else:
            i['db'] = False
    context = {
        'data': data,
        'title': '개봉 예정작'
    }
    return render(request,'cinema/movie_now.html',context)