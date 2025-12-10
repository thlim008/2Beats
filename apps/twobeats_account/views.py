from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db import IntegrityError

from .forms import (
    MusicPlaylistCreateForm,
    PlaylistMusicAddForm,
    PlaylistVideoAddForm,
    ProfileForm,
    SignupForm,
    VideoPlaylistCreateForm,
)
from .models import (
    MusicHistory,
    VideoHistory,
    MusicPlaylist,
    VideoPlaylist,
    PlaylistTrack,
    PlaylistClip,
)

# 통계 데이터를 위한 import
from apps.twobeats_upload.models import Music, Video

User = get_user_model()


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {'form': form})


@login_required(login_url='/account/login/')
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '정보가 저장되었습니다.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'account/profile.html', {'form': form})


def landing(request):
    if request.user.is_authenticated:
        return redirect('home')

    # 실제 데이터베이스 기반 통계
    stats = {
        'total_tracks': Music.objects.count(),
        'total_videos': Video.objects.count(),
        'total_users': User.objects.count(),
        'total_playlists': MusicPlaylist.objects.count() + VideoPlaylist.objects.count(),
    }

    return render(request, 'account/landing.html', {'stats': stats})


@login_required(login_url='/account/login/')
def home(request):
    return render(request, 'account/home.html')


@login_required(login_url='/account/login/')
def logout_view(request):
    auth_logout(request)
    return redirect('landing')


@login_required(login_url='/account/login/')
def mylist(request):
    tab = request.GET.get('tab', 'music')
    if tab not in ('music', 'video'):
        tab = 'music'

    if tab == 'music':
        playlists = request.user.music_playlists.order_by('-created_at')
        form_class = MusicPlaylistCreateForm
    else:
        playlists = request.user.video_playlists.order_by('-created_at')
        form_class = VideoPlaylistCreateForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect(f"{request.path}?tab={tab}")
    else:
        form = form_class()

    return render(
        request,
        'account/mylist.html',
        {
            'tab': tab,
            'playlists': playlists,
            'form': form,
        },
    )


@login_required(login_url='/account/login/')
def history(request):
    music_history = (
        MusicHistory.objects.filter(user=request.user)
        .select_related('music')
        .order_by('-played_at')
    )
    video_history = (
        VideoHistory.objects.filter(user=request.user)
        .select_related('video')
        .order_by('-played_at')
    )
    return render(
        request,
        'account/history.html',
        {
            'music_history': music_history,
            'video_history': video_history,
        },
    )


@login_required(login_url='/account/login/')
def playlist_detail(request, playlist_id):
    """
    [수정] 플레이리스트 상세 - 음악 추가 기능 제거 (순서 변경만 유지)
    """
    kind = request.GET.get('kind', 'music') # 기본값 music

    if kind == 'music':
        playlist = get_object_or_404(MusicPlaylist, id=playlist_id, user=request.user)
        items = playlist.tracks.select_related('music').order_by('order')
        is_music = True
        is_plivideo = False
    else:
        playlist = get_object_or_404(VideoPlaylist, id=playlist_id, user=request.user)
        items = playlist.clips.select_related('video').order_by('order')
        is_music = False
        is_plivideo = True

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 'add' 액션 로직 삭제됨 (음악 상세페이지에서 추가하도록 유도)
        
        if action == 'reorder':
            # 순서 변경 로직 유지
            updated = False
            items_list = list(items)
            for item in items_list:
                key = f"order_{item.id}"
                if key in request.POST:
                    try:
                        new_order = int(request.POST.get(key, item.order))
                    except (TypeError, ValueError):
                        new_order = item.order
                    if new_order != item.order:
                        item.order = new_order
                        updated = True
            if updated:
                if is_music:
                    playlist.tracks.model.objects.bulk_update(items_list, ['order'])
                else:
                    playlist.clips.model.objects.bulk_update(items_list, ['order'])
                messages.success(request, '순서를 업데이트했습니다.')
            return redirect(f"{request.path}?kind={kind}")

    return render(
        request,
        'account/playlist_detail.html',
        {
            'playlist': playlist,
            'items': items,
            'is_music': is_music,
            'is_plivideo': is_plivideo,
            'kind': kind,
            # 'form': form, # 폼 제거
        },
    )


@require_POST
@login_required(login_url='/account/login/')
def add_music_to_playlist(request):
    """
    [수정] 음악 상세 페이지에서 특정 플레이리스트에 곡 추가
    """
    music_id = request.POST.get('music_id')
    playlist_id = request.POST.get('playlist_id') # 플레이리스트 ID 받기

    if not music_id or not playlist_id:
        return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)

    # 내 플레이리스트인지 확인
    playlist = get_object_or_404(MusicPlaylist, id=playlist_id, user=request.user)
    music = get_object_or_404(Music, pk=music_id)

    # 중복 체크
    if PlaylistTrack.objects.filter(playlist=playlist, music=music).exists():
        return JsonResponse({'success': False, 'error': '이미 이 플레이리스트에 담긴 곡입니다.'})

    try:
        # 마지막 순서 구하기
        last_order = PlaylistTrack.objects.filter(playlist=playlist).count()

        PlaylistTrack.objects.create(
            playlist=playlist,
            music=music,
            order=last_order + 1,
        )
        return JsonResponse({
            'success': True,
            'message': f"'{playlist.folder_name}'에 추가되었습니다."
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def add_video_to_playlist(request):
    """
    영상 상세 페이지에서 특정 플레이리스트에 영상 추가
    """
    import json
    data = json.loads(request.body)
    video_id = data.get('video_id')
    playlist_id = data.get('playlist_id')

    if not video_id or not playlist_id:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    # 내 플레이리스트인지 확인
    playlist = get_object_or_404(VideoPlaylist, id=playlist_id, user=request.user)
    video = get_object_or_404(Video, pk=video_id)

    # 중복 체크
    if PlaylistClip.objects.filter(playlist=playlist, video=video).exists():
        return JsonResponse({'success': False, 'message': '이미 이 플레이리스트에 담긴 영상입니다.'})

    try:
        # 마지막 순서 구하기
        last_order = PlaylistClip.objects.filter(playlist=playlist).count()

        PlaylistClip.objects.create(
            playlist=playlist,
            video=video,
            order=last_order + 1,
        )
        return JsonResponse({
            'success': True,
            'message': f"'{playlist.folder_name}'에 추가되었습니다."
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def get_playlists(request):
    """
    사용자의 플레이리스트 목록 반환 (AJAX용)
    """
    playlist_type = request.GET.get('type', 'music')  # 'music' or 'video'

    if playlist_type == 'music':
        playlists = MusicPlaylist.objects.filter(user=request.user).order_by('-created_at')
        playlist_data = [{'id': pl.id, 'folder_name': pl.folder_name} for pl in playlists]
    else:
        playlists = VideoPlaylist.objects.filter(user=request.user).order_by('-created_at')
        playlist_data = [{'id': pl.id, 'folder_name': pl.folder_name} for pl in playlists]

    return JsonResponse({'playlists': playlist_data})
