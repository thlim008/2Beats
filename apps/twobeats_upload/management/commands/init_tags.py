from django.core.management.base import BaseCommand
from apps.twobeats_upload.models import Tag


class Command(BaseCommand):
    help = '초기 태그 생성'
    
    def handle(self, *args, **kwargs):
        tags = [
            # 분위기
            '신남',
            '슬픔',
            '잔잔함',
            '활기찬',
            '로맨틱',
            '우울함',
            '힐링',
            '감성적',
            
            # 상황
            '운동',
            '드라이브',
            '출퇴근',
            '카페',
            '공부',
            '파티',
            '새벽',
            '여름',
            '겨울',
            '비오는날',
            
            # 스타일
            '어쿠스틱',
            '일렉트로닉',
            '리믹스',
        ]
        
        created_count = 0
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {created_count}개의 태그 생성 완료!')
        )