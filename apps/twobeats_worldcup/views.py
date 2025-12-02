import math
import random
from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.twobeats_upload.models import Music
from apps.twobeats_music_explore.models import MusicLike
from apps.twobeats_account.models import Playlist, PlaylistMusic
from .models import WorldCupGame, WorldCupResult, CustomWorldCup
from .serializers import CandidateSerializer, WorldCupSaveSerializer

User = get_user_model()

@api_view(['GET'])
def get_candidates(request):
    """
    월드컵 후보곡 선정 API
    
    [모드 설명]
    1. sort=random: 그냥 무작위 (기존)
    2. sort=rank & genre=특정: 해당 장르 내 랭킹순
    3. sort=rank & genre=all: 모든 장르의 '장르별 1등'들을 모아서 선정 (쿼터제)
    """
    # 1. 파라미터 받기
    genre = request.query_params.get('genre', 'all')
    count = int(request.query_params.get('count', 16))
    sort_mode = request.query_params.get('sort', 'random')
    custom_code = request.query_params.get('custom_code')

    # 기본 쿼리셋
    if custom_code:
        # 커스텀 월드컵인 경우 해당 곡들만 후보로 설정
        custom_wc = get_object_or_404(CustomWorldCup, access_code=custom_code)
        base_musics = custom_wc.musics.all()
    else:
        # 일반 모드
        base_musics = Music.objects.all()

    # ---------------------------------------------------------
    # CASE A: 랭킹 모드 (인기곡 대결)
    # ---------------------------------------------------------
    if sort_mode == 'rank':
        
        # A-1. 전체 장르 통합 랭킹 (장르별 쿼터제 적용)
        if genre == 'all':
            candidates_list = []
            
            # 1. 모든 장르 목록 가져오기 ['ballad', 'dance', ...]
            all_genres = [choice[0] for choice in Music.GENRE_CHOICES]
            
            # 2. 장르별 할당량 계산 (예: 16강 / 11개 장르 = 장르당 약 2곡)
            quota_per_genre = math.ceil(count / len(all_genres))
            
            # 3. 각 장르별로 1등곡들을 수집
            for g in all_genres:
                top_songs = base_musics.filter(music_type=g).annotate(
                    total_score=Coalesce(Sum('worldcupresult__wc_score'), 0)
                ).order_by('-total_score')[:quota_per_genre]
                
                candidates_list.extend(top_songs)
            
            # 4. 중복 제거 및 셔플 (장르 순서 섞기)
            # (쿼터제로 뽑다보면 count보다 많이 뽑힐 수 있으므로 셔플 후 자름)
            candidates_list = list(set(candidates_list)) # 중복제거
            random.shuffle(candidates_list)
            candidates = candidates_list[:count]
            
            # 5. 부족분 채우기 (만약 장르별 곡이 없어서 16개가 안 되면 랜덤으로 채움)
            if len(candidates) < count:
                needed = count - len(candidates)
                existing_ids = [m.id for m in candidates]
                
                extras = list(base_musics.exclude(id__in=existing_ids).order_by('?')[:needed])
                candidates.extend(extras)

        # A-2. 특정 장르 내 랭킹 (기존 로직 유지)
        else:
            top_candidates = base_musics.filter(music_type=genre).annotate(
                total_score=Coalesce(Sum('worldcupresult__wc_score'), 0)
            ).order_by('-total_score')[:count]
            candidates = list(top_candidates)
            random.shuffle(candidates)

    # ---------------------------------------------------------
    # CASE B: 랜덤 모드 (기존 로직)
    # ---------------------------------------------------------
    else:
        if genre and genre != 'all':
            base_musics = base_musics.filter(music_type=genre)
        candidates = base_musics.order_by('?')[:count]

    # ---------------------------------------------------------
    # 공통: 최종 검증 및 반환
    # ---------------------------------------------------------
    # QuerySet이 아닌 List일 수도 있어서 len()으로 체크
    if len(candidates) < count:
        return Response(
            {'error': f'노래가 부족합니다. (현재 {len(candidates)}곡, 필요 {count}곡)'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CandidateSerializer(candidates, many=True)
    return Response({'candidates': serializer.data})


@api_view(['POST'])
@authentication_classes([]) # 인증 무시
@permission_classes([AllowAny]) # 권한 무시
def save_game_result(request):
    """
    월드컵 결과 저장 API (트랜잭션 처리)
    """
    # 1. 데이터 검증 (Serializer가 알아서 해줌)
    serializer = WorldCupSaveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # 트랜잭션 시작 (중간에 에러나면 자동 롤백)
        with transaction.atomic():
            # 유저 찾기
            user = None
            if data.get('user_uid'):
                user = User.objects.filter(pk=data['user_uid']).first()
            # 1. 커스텀 월드컵인지 확인 (custom_code 받기)
            # (request.data에서 직접 가져옵니다)
            custom_code = request.data.get('custom_code')
            custom_wc = None
            if custom_code:
                # access_code로 해당 커스텀 월드컵 찾기
                custom_wc = CustomWorldCup.objects.filter(access_code=custom_code).first()

            # 2. 게임 헤더 저장 (custom_worldcup 필드 추가)
            game = WorldCupGame.objects.create(
                wc_user=user,
                wc_total_rounds=data['total_rounds'],
                custom_worldcup=custom_wc  # ✅ 새로 추가된 부분
            ) 

            # 상세 결과 저장
            score_map = {1: 50, 2: 30, 4: 10, 8: 5, 16: 0}
            results_to_create = []

            for item in data['results']:
                results_to_create.append(WorldCupResult(
                    wc_game=game,
                    wc_music_id=item['music_id'], # ID로 바로 연결
                    wc_final_rank=item['rank'],
                    wc_score=score_map.get(item['rank'], 0)
                ))
            
            # 한 번에 저장 (Bulk Insert) - 속도 빠름
            WorldCupResult.objects.bulk_create(results_to_create)

            return Response(
                {'message': '저장 완료', 'game_id': game.pk}, 
                status=status.HTTP_201_CREATED
            )

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_custom_worldcup(request):
    """나만의 월드컵 생성"""
    title = request.data.get('title')
    music_ids = request.data.get('music_ids', []) # 선택한 노래 ID 리스트 [1, 5, 10...]

    if not title or len(music_ids) < 4:
        return Response({'error': '제목과 최소 4곡 이상의 노래가 필요합니다.'}, status=400)

    # 1. 커스텀 월드컵 객체 생성
    custom_wc = CustomWorldCup.objects.create(
        title=title,
        creator=request.user
    )
    
    # 2. 노래 연결
    musics = Music.objects.filter(id__in=music_ids)
    custom_wc.musics.set(musics)
    
    # 3. 공유 URL 반환
    share_url = f"/worldcup/custom/{custom_wc.access_code}/"
    return Response({'message': '생성 완료!', 'share_url': share_url})

def custom_worldcup_page(request):
    """나만의 월드컵 생성 화면 렌더링"""
    # 사용자가 선택할 수 있게 모든 노래 목록을 함께 보냄
    musics = Music.objects.all().order_by('music_title')
    return render(request, 'twobeats_worldcup/create.html', {'musics': musics})
    
def game_page(request):
    """월드컵 게임 화면 렌더링"""
    return render(request, 'twobeats_worldcup/game.html')

def custom_game_page(request, access_code):
    """커스텀 월드컵 플레이 페이지"""
    custom_wc = get_object_or_404(CustomWorldCup, access_code=access_code)
    context = {
        'is_custom': True,
        'custom_wc': custom_wc, # 템플릿에서 제목 등을 보여주기 위함
    }
    return render(request, 'twobeats_worldcup/game.html', context)
    
def ranking_page(request):
    """
    명예의 전당 (랭킹 페이지) - 장르 필터 추가
    URL: /worldcup/ranking/?genre=ballad
    """
    # 1. 파라미터 받기
    selected_genre = request.GET.get('genre', 'all')
    
    # 2. 기본 쿼리셋 (점수 계산)
    rankings = Music.objects.annotate(
        total_score=Coalesce(Sum('worldcupresult__wc_score'), 0),
        win_count=Count('worldcupresult', filter=Q(worldcupresult__wc_final_rank=1))
    ).filter(
        total_score__gt=0 # 0점 제외
    )

    # 3. 장르 필터링 적용
    if selected_genre != 'all':
        rankings = rankings.filter(music_type=selected_genre)

    # 4. 정렬 (점수 > 우승횟수 > 최신순)
    rankings = rankings.order_by('-total_score', '-win_count', '-music_created_at')[:100]

    # 5. 템플릿에 보낼 데이터
    context = {
        'rankings': rankings,
        'selected_genre': selected_genre,
        'genres': Music.GENRE_CHOICES, # 장르 목록 (버튼 생성용)
    }
    return render(request, 'twobeats_worldcup/ranking.html', context)


def wc_popular(request):
    """인기 차트 (월드컵점수기준)"""
    wc_musics = Music.objects.annotate(
        total_score=Coalesce(Sum('worldcupresult__wc_score'), 0)
    ).exclude(
        total_score=0 #0점은 순위 제외
    ).order_by(
        '-total_score',
        '-music_created_at'
    )[:50]
    
    context = {
        'musics': wc_musics,
        'chart_type': 'wc_popular',
        'chart_title': 'worldcup 상위 차트',
    }
    return render(request, 'twobeats_worldcup/wc_chart.html', context)

            # top_candidates = base_musics.filter(music_type=genre).annotate(
            #     total_score=Coalesce(Sum('worldcupresult__wc_score'), 0)
            # ).order_by('-total_score')[:count]
            # candidates = list(top_candidates)
            # random.shuffle(candidates)


def result_page(request, game_id):
    """월드컵 결과 페이지 렌더링"""
    game = get_object_or_404(WorldCupGame, pk=game_id)
    results = WorldCupResult.objects.filter(wc_game=game).select_related('wc_music').order_by('wc_final_rank')
    
    winner = results.first()
    others = results[1:]
    
    # 현재 로그인한 유저라면 ID를 넘겨서 본인을 제외시킴
    current_user_id = game.wc_user.pk if game.wc_user else None
    
    # 협업 필터링 추천
    recommendations = get_collaborative_recommendations(winner.wc_music.id, current_user_id)
    
    # 만약 협업 필터링 결과가 없으면(데이터 부족), 장르 기반 추천으로 대체 (Fail-over)
    if not recommendations.exists():
        recommendations = Music.objects.filter(
            music_type=winner.wc_music.music_type
        ).exclude(id=winner.wc_music.id).order_by('?')[:5]

    context = {
        'game': game,
        'winner': winner,
        'others': others,
        'recommendations': recommendations, # 템플릿으로 전달
    }
    return render(request, 'twobeats_worldcup/result.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 로그인한 유저만 가능
def save_result_to_playlist(request, game_id):
    """
    월드컵 결과(4강 이상)를 새 플레이리스트로 저장
    """
    try:
        game = get_object_or_404(WorldCupGame, pk=game_id)
        
        # 1. 저장할 대상 곡 가져오기 (예: 4강 이상인 rank 1, 2, 4)
        # 16강 전체를 저장하고 싶다면 rank 필터링을 제거하면 됩니다.
        top_results = WorldCupResult.objects.filter(
            wc_game=game, 
            wc_final_rank__lte=4  # 4위(4강) 이내만 저장
        ).order_by('wc_final_rank')
        
        if not top_results.exists():
            return Response({'error': '저장할 곡이 없습니다.'}, status=400)

        # 2. 새 플레이리스트 생성
        # 이름 예시: "월드컵 우승곡 모음 (2025-11-27)"
        playlist_title = f"월드컵 결과 ({timezone.now().strftime('%Y-%m-%d')})"
        new_playlist = Playlist.objects.create(
            user=request.user,
            folder_name=playlist_title
        )

        # 3. 곡들을 플레이리스트에 추가 (Bulk Create로 한 번에 저장)
        playlist_musics = []
        for index, result in enumerate(top_results):
            playlist_musics.append(PlaylistMusic(
                playlist=new_playlist,
                music=result.wc_music,
                order=index # 순서대로 저장
            ))
        
        PlaylistMusic.objects.bulk_create(playlist_musics)

        return Response({
            'message': f'"{playlist_title}"에 {len(playlist_musics)}곡이 저장되었습니다!',
            'playlist_id': new_playlist.id
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


def recommend_by_tags(request, game_id):
    '''월드컵 우승곡 기반 추천'''
    # 이번 게임의 우승곡 가져오기
    game = get_object_or_404(WorldCupGame, pk=game_id)
    winner_result = game.results.filter(wc_final_rank=1).first()
    winner_music = winner_result.wc_music

    # 우승곡의 태그들
    winner_tags = winner_music.tags.all()

    # 같은 장르이면서 태그가 겹치는 곡 찾기 (우승곡 제외)
    recommendations = Music.objects.filter(music_type=winner_music.music_type) \
        .exclude(id=winner_music.id) \
        .filter(tags__in=winner_tags) \
        .annotate(common_tags=Count('tags')) \
        .order_by('-common_tags', '-music_like_count')[:5]

    return render(request, 'twobeats_worldcup/recommend.html', {'musics': recommendations})


def get_collaborative_recommendations(winner_music_id, user_id=None):
    """
    협업 필터링 추천 알고리즘
    :param winner_music_id: 현재 월드컵 우승곡 ID
    :param user_id: 현재 플레이한 유저 ID (본인 제외용, 없으면 None)
    :return: 추천된 Music QuerySet (최대 5개)
    """
    
    # 1. [동질 집단 찾기] 
    # 이 노래(winner_music_id)를 '우승(rank=1)'시킨 다른 게임의 유저 ID들을 찾음
    # (익명 유저(None)는 추적이 불가능하므로 제외)
    similar_users = WorldCupResult.objects.filter(
        wc_music_id=winner_music_id,
        wc_final_rank=1,
        wc_game__wc_user__isnull=False  # 로그인 유저만
    ).exclude(
        wc_game__wc_user_id=user_id     # 나 자신은 제외
    ).values_list('wc_game__wc_user', flat=True).distinct()

    # 데이터가 너무 적으면 빈 결과 반환 (혹은 랜덤/장르 추천으로 대체)
    if not similar_users:
        return Music.objects.none()

    # 2. [선호 곡 수집 & 랭킹]
    # 나와 취향이 비슷한 유저들(similar_users)이 좋아하는 다른 곡 찾기
    
    # 방식 A: 그들이 '좋아요(MusicLike)'를 누른 곡들
    # 방식 B: 그들이 '다른 월드컵에서 우승(WorldCupResult)'시킨 곡들
    # -> 여기서는 두 가지를 합쳐서 카운트해 봅니다.
    
    # A. 좋아요 누른 곡 ID
    liked_music_ids = MusicLike.objects.filter(
        user__in=similar_users
    ).values_list('music_id', flat=True)
    
    # B. 다른 월드컵 우승 곡 ID
    won_music_ids = WorldCupResult.objects.filter(
        wc_game__wc_user__in=similar_users,
        wc_final_rank=1
    ).values_list('wc_music_id', flat=True)

    # 3. [집계 및 정렬]
    # 위 ID들을 모아서 가장 많이 언급된 곡 찾기
    # (현재 우승곡 자체는 추천에서 제외)
    all_related_music_ids = list(liked_music_ids) + list(won_music_ids)
    
    # Music 모델에서 해당 ID들을 필터링하고, 등장 횟수(frequency)로 정렬
    # 꼼수: id__in으로 필터링 후 annotate로 점수 매기기가 복잡하므로,
    # 파이썬 레벨에서 Counter를 쓰거나, DB 쿼리를 최적화할 수 있습니다.
    
    # DB 쿼리 최적화 방식:
    recommendations = Music.objects.filter(
        id__in=all_related_music_ids
    ).exclude(
        id=winner_music_id  # 방금 우승한 곡은 추천 제외
    ).annotate(
        # 좋아요나 우승 기록에 이 곡이 몇 번 등장했는지 카운트
        popularity=Count('musiclike', filter=Q(musiclike__user__in=similar_users)) + 
                   Count('worldcupresult', filter=Q(worldcupresult__wc_game__wc_user__in=similar_users, worldcupresult__wc_final_rank=1))
    ).order_by('-popularity')[:5]  # 상위 5개

    return recommendations