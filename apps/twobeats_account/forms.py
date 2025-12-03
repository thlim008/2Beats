from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from apps.twobeats_upload.models import Music, Video
from .models import MusicPlaylist, VideoPlaylist

username_validator = RegexValidator(
    regex=r'^[a-z0-9](?:[a-z0-9_-]{3,18}[a-z0-9])$',
    message='아이디는 5~20자의 영문 소문자, 숫자, 특수기호(_ , -)만 사용하며, 시작/끝에는 특수기호를 사용할 수 없습니다.',
)


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label='아이디',
        min_length=5,
        max_length=20,
        validators=[username_validator],
        help_text='5~20자의 영문 소문자, 숫자, 특수기호(_ , -)만 가능하며 시작/끝에는 특수기호를 쓸 수 없습니다.',
    )
    password1 = forms.CharField(
        label='비밀번호',
        strip=False,
        widget=forms.PasswordInput,
        min_length=8,
        help_text='8자 이상이면 됩니다. 대소문자/특수기호 제한 없음.',
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        strip=False,
        widget=forms.PasswordInput,
        help_text='비밀번호를 한 번 더 입력하세요.',
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label='이름',
        required=False,
        help_text='이름을 입력하세요.',
    )
    last_name = forms.CharField(
        label='성',
        required=False,
        help_text='성을 입력하세요.',
    )
    email = forms.EmailField(
        label='이메일',
        required=False,
    )
    phone_number = forms.CharField(
        label='전화번호',
        required=False,
        help_text='예: 010-1234-5678',
    )
    profile_image = forms.ImageField(
        label='프로필 이미지',
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_image')


class MusicPlaylistCreateForm(forms.ModelForm):
    folder_name = forms.CharField(label='플레이리스트 이름', max_length=100)

    class Meta:
        model = MusicPlaylist
        fields = ('folder_name',)


class VideoPlaylistCreateForm(forms.ModelForm):
    folder_name = forms.CharField(label='플레이리스트 이름', max_length=100)

    class Meta:
        model = VideoPlaylist
        fields = ('folder_name',)


class PlaylistMusicAddForm(forms.Form):
    music = forms.ModelChoiceField(
        label='음악',
        queryset=Music.objects.all(),
    )
    order = forms.IntegerField(
        label='순서',
        required=False,
        min_value=0,
        help_text='비우면 자동으로 마지막에 추가됩니다.',
    )


class PlaylistVideoAddForm(forms.Form):
    video = forms.ModelChoiceField(
        label='영상',
        queryset=Video.objects.all(),
    )
    order = forms.IntegerField(
        label='순서',
        required=False,
        min_value=0,
        help_text='비우면 자동으로 마지막에 추가됩니다.',
    )
