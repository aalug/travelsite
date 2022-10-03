"""
Views for accounts app.
"""
from django.contrib import messages, auth
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView, RedirectView, TemplateView, CreateView

from accounts.forms import UserForm, UserProfileForm, NewsletterEmailForm
from accounts.models import User, Subscriber, UserProfile
from accounts.utils import detect_user_type, send_verification_email, send_confirmation_email, send_newsletter


class RegisterUserView(SuccessMessageMixin, FormView):
    """View for registering a new user."""
    template_name = 'accounts/register_user.html'
    form_class = UserForm
    success_url = reverse_lazy('home')
    success_message = 'Congratulations! Your account has been created.' \
                      'Please check your email to activate it.'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            messages.warning(self.request, 'You are already logged in!')
            return redirect('my-account')

        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create_user(email=email, username=username, password=password)
        self.sent_email(user)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.user.is_authenticated:
            messages.warning(self.request, 'You are already logged in!')
            return redirect('my-account')

    def sent_email(self, user):
        """Sending verification email."""
        mail_subject = 'Please activate your account'
        email_template = 'accounts/emails/verification_email.html'
        send_verification_email(self.request, user, mail_subject, email_template)


class MyAccountRedirectView(LoginRequiredMixin, RedirectView):
    """view checks is the user an admin or a regular user and
       redirects to appropriate view and page."""

    def get_redirect_url(self, *args, **kwargs):
        return detect_user_type(self.request.user)


class LoginView(View):
    """View for logging in."""

    def get(self, request):
        if request.user.is_authenticated:
            messages.warning(request, 'You are already logged in.')
            return redirect('my-account')
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('my-account')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')


class LogoutView(View):
    """View for logging out."""

    def get(self, request):
        auth.logout(request)
        messages.info(request, 'You are now logged out.')
        return redirect('login')


class DashboardView(LoginRequiredMixin, View):
    """View for displaying user dashboard."""

    font_color = ''

    def get(self, request):
        profile = get_object_or_404(UserProfile, user=self.request.user)
        profile_form = UserProfileForm(instance=profile)
        context = {
            'user': request.user,
            'profile_form': profile_form
        }
        return render(request, 'accounts/dashboard.html', context)

    def post(self, request):
        profile = get_object_or_404(UserProfile, user=self.request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            font_color = request.POST.get('font-color')
            profile.info_font_color = font_color
            profile_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('dashboard')


class ActivateView(View):
    """Activate the user by setting the is_active status to True."""

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Congratulation! Your account is activated.')
            return redirect('my-account')
        else:
            messages.error(request, 'Invalid activation link')
            return redirect('my-account')


class ForgotPasswordView(View):
    """View for handling forgotten passwords."""

    def get(self, request):
        return render(request, 'accounts/forgot_password.html')

    def post(self, request):
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot-password')


class ResetPasswordValidateView(View):
    """View for validating the password reset."""

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.info(request, 'Please reset your password.')
            return redirect('reset-password')
        else:
            messages.error(request, 'This link has expired.')
            return redirect('my-account')


class ResetPasswordView(View):
    """View for resetting passwords."""

    def get(self, request):
        return render(request, 'accounts/reset_password.html')

    def post(self, request):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset-password')


class SubscribeToNewsletterView(View):
    """View for signing up to the newsletter."""

    def post(self, request):
        email = request.POST.get('email')
        Subscriber.objects.create(email=email)
        current_site = request.POST.get('current_site')
        messages.success(request, 'Congratulations! You successfully signed up to our newsletter.')

        # send email to confirm subscription
        mail_subject = f'Hello {email}! '
        email_template = 'accounts/emails/confirm_subscription_email.html'
        send_confirmation_email(email, mail_subject, email_template)
        return redirect(current_site)


class SendNewsletterView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, FormView):
    """View for sending newsletter emails to all subscribers."""

    def test_func(self):
        if self.request.user.is_staff:
            return True
        raise PermissionDenied

    form_class = NewsletterEmailForm
    template_name = 'accounts/send_newsletter.html'
    success_url = reverse_lazy('newsletter')
    success_message = 'Email sent successfully.'

    def form_valid(self, form):
        title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        email_template = 'accounts/emails/newsletter.html'
        send_newsletter(title, content, email_template)
        form.save()
        return super().form_valid(form)
