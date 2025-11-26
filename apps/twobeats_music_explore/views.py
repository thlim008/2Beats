# apps/twobeats_music_explore/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from apps.twobeats_upload.models import Music, Tag  # Tag 추가!
from .models import MusicLike, MusicComment


def search_music(request):
    """음악 검색"""
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    tag = request.GET.get('tag', '')
    
    musics = Music.objects.all()
    
    # 검색어 필터
    if query:
        musics = musics.filter(
            Q(music_title__icontains=query) | 
            Q(music_singer__icontains=query)
        )
    
    # 장르 필터
    if genre:
        musics = musics.filter(music_type=genre)
    
    # 태그 필터
    if tag:
        musics = musics.filter(tags__name=tag)
    
    # 모든 태그 가져오기 (동적!)
    all_tags = Tag.objects.all().order_by('name')
    
    context = {
        'musics': musics,
        'query': query,
        'genre': genre,
        'tag': tag,
        'all_tags': all_tags,  # 추가!
    }
    return render(request, 'music_explore/search.html', context)


# 나머지 함수들은 그대로...
def chart_popular(request):
    """인기 차트 (재생수순)"""
    musics = Music.objects.all().order_by('-music_count')[:50]
    
    context = {
        'musics': musics,
        'chart_type': 'popular',
        'chart_title': '인기 차트',
    }
    return render(request, 'music_explore/chart.html', context)


def chart_latest(request):
    """최신 차트 (업로드순)"""
    musics = Music.objects.all().order_by('-music_created_at')[:50]
    
    context = {
        'musics': musics,
        'chart_type': 'latest',
        'chart_title': '최신 차트',
    }
    return render(request, 'music_explore/chart.html', context)


def chart_liked(request):
    """좋아요 차트 (좋아요순)"""
    musics = Music.objects.all().order_by('-music_like_count')[:50]
    
    context = {
        'musics': musics,
        'chart_type': 'liked',
        'chart_title': '좋아요 차트',
    }
    return render(request, 'music_explore/chart.html', context)


def music_detail(request, music_id):
    """음악 상세 페이지"""
    music = get_object_or_404(Music, pk=music_id)
    
    # 재생수 증가
    music.music_count += 1
    music.save()
    
    # 댓글 가져오기
    comments = music.comments.all()
    
    # 좋아요 여부 확인
    is_liked = False
    if request.user.is_authenticated:
        is_liked = MusicLike.objects.filter(
            user=request.user, 
            music=music
        ).exists()
    
    context = {
        'music': music,
        'comments': comments,
        'is_liked': is_liked,
    }
    return render(request, 'music_explore/detail.html', context)


@login_required
def music_like(request, music_id):
    """좋아요 토글"""
    music = get_object_or_404(Music, pk=music_id)
    
    # 이미 좋아요 했는지 확인
    like = MusicLike.objects.filter(user=request.user, music=music)
    
    if like.exists():
        # 좋아요 취소
        like.delete()
        music.music_like_count -= 1
        is_liked = False
    else:
        # 좋아요 추가
        MusicLike.objects.create(user=request.user, music=music)
        music.music_like_count += 1
        is_liked = True
    
    music.save()
    
    # AJAX 요청이면 JSON 응답
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_liked': is_liked,
            'like_count': music.music_like_count,
        })
    
    # 일반 요청이면 리다이렉트
    return redirect('music_explore:detail', music_id=music_id)


@login_required
def music_comment(request, music_id):
    """댓글 작성"""
    if request.method == 'POST':
        music = get_object_or_404(Music, pk=music_id)
        content = request.POST.get('content', '')
        
        if content:
            MusicComment.objects.create(
                user=request.user,
                music=music,
                content=content
            )
    
    return redirect('music_explore:detail', music_id=music_id)