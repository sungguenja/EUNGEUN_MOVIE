from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    path('all/', views.movie_all, name='movie_all'),  # 영화 리스트
    path('search/', views.search, name='search'), # 검색 기능
    path('community/', views.article_list, name='article_list'),  # 게시판 (모든 글 리스트)
    path('<int:movie_pk>/', views.movie_detail, name='movie_detail'),  # 영화 디테일이자 해당 영화와 관련된 글 리스트
    path('<int:movie_pk>/like/', views.movie_like, name='movie_like'), # 영화 좋아요 버튼
    path('<int:movie_pk>/create/', views.article_create, name='article_create'),  # 글 작성
    path('articles/<int:article_pk>/', views.article_detail, name='article_detail'),  # 글 디테일이자 댓글 리스트
    path('articles/<int:article_pk>/delete/', views.article_delete, name='article_delete'),  # 글 삭제
    path('articles/<int:article_pk>/update/', views.article_update, name='article_update'),  # 글 수정
    path('articles/<int:article_pk>/create/', views.comment_create, name='comment_create'),  # 댓글 작성
    path('<int:article_pk>/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),  # 댓글 삭제
    path('genres/',views.genre_all,name='genre_all'), # 모든 장르
    path('genres/<int:genre_pk>/',views.genre_detail, name='genre_detail'), # 특정 장르
    path('recommend/',views.recommend,name='recommend'), # 추천
    path('recommend/random/',views.recommend_random,name='recommend_random'), # 랜덤 추천
    path('recommend/<int:genre_pk>/', views.recommend_genre, name='recommend_genre'), # 결과로 나온 장르에서 영화 고르기
    path('worldcup/',views.worldcup,name='worldcup'), # 월드컵
    path('worldcup/<int:genre_pk>/<int:round_num>/', views.start_worldcup, name='start_worldcup'), # 월드컵 데이터 가져오기
    path('victory/<int:movie_pk>/',views.victory,name='victory'), # 월드컵 우승 올리기
    path('now/',views.movie_now,name='movie_now'), # 지금 상영작
    path('upcoming/',views.movie_upcoming,name='movie_upcoming'), # 상영 예정작
]