from django import forms
from django.forms import inlineformset_factory
from .models import Post, Photo


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'categories', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


PhotoFormSet = inlineformset_factory(
    Post,
    Photo,
    fields=[
        'image',
        'title',
        'short_description',
        'license_type',
        'price_note',
        'camera_model',
        'file_format',
        'resolution',
    ],
    extra=3,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control'}),
        'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'license_type': forms.Select(attrs={'class': 'form-select'}),
        'price_note': forms.TextInput(attrs={'class': 'form-control'}),
        'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
        'file_format': forms.TextInput(attrs={'class': 'form-control'}),
        'resolution': forms.TextInput(attrs={'class': 'form-control'}),
        'categories': forms.CheckboxSelectMultiple(),
    }
)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ваше сообщение...'
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )