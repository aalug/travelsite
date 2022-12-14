"""
Forms for accounts app.
"""
from django import forms
from .models import User, UserProfile, NewsletterEmail, MessageToStaff
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    """Form foe creating / registering a new user."""
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')


class UserProfileForm(forms.ModelForm):
    """Form for getting the information from user to build user profile."""
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                      validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                  validators=[allow_only_images_validator])
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...'}))

    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at', 'modified_at', 'info_font_color']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for f in self.fields.values():
            f.required = False


class NewsletterEmailForm(forms.ModelForm):
    """Form for getting the data which later will be sent as newsletter."""

    class Meta:
        model = NewsletterEmail
        fields = '__all__'


class MessageToStaffForm(forms.ModelForm):
    """Form for sending emails to admin team / owner."""

    class Meta:
        model = MessageToStaff
        fields = '__all__'
