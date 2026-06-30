from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.contrib import messages
from .models import Project, Service
from .forms import ContactMessageForm
from .ai_service import AIServiceError, ask_portfolio_ai

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['services'] = Service.objects.all()
        context['contact_form'] = ContactMessageForm()
        return context

class ContactSubmitView(View):
    def post(self, request, *args, **kwargs):
        form = ContactMessageForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if form.is_valid():
            contact_message = form.save()
            try:
                email = EmailMessage(
                    subject=f"Portfolio enquiry from {contact_message.name}",
                    body=(
                        f"Name: {contact_message.name}\n"
                        f"Email: {contact_message.email}\n\n"
                        f"Message:\n{contact_message.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_NOTIFICATION_EMAIL],
                    reply_to=[contact_message.email],
                )
                email.send(fail_silently=False)
            except Exception:
                logger.exception("Contact message saved but notification email failed")
                failure_msg = (
                    "Your message was saved, but the email notification could not be delivered. "
                    "Please email Mohit directly at mohitmusic2429@gmail.com."
                )
                if is_ajax:
                    return JsonResponse({'success': False, 'saved': True, 'message': failure_msg}, status=502)
                messages.warning(request, failure_msg)
                return redirect('index')

            if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
                local_msg = (
                    "Your message was saved, but local email delivery is not configured yet. "
                    "Add the Brevo SMTP values to the project .env file."
                )
                if is_ajax:
                    return JsonResponse({'success': False, 'saved': True, 'message': local_msg}, status=503)
                messages.warning(request, local_msg)
                return redirect('index')
            success_msg = "Thank you! Your message has been sent successfully."
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            
            messages.success(request, success_msg)
            return redirect('index')
        else:
            errors = form.errors.get_json_data()
            error_msg = "There was an error in your submission. Please check your fields."
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg, 'errors': errors}, status=400)
            
            messages.error(request, error_msg)
            # Re-render home page with form errors
            projects = Project.objects.all()
            services = Service.objects.all()
            return render(request, 'portfolio/index.html', {
                'projects': projects,
                'services': services,
                'contact_form': form,
            })


class ChatView(View):
    def post(self, request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        rate_key = f"portfolio-chat:{client_ip}"
        requests_made = cache.get(rate_key, 0)
        if requests_made >= 12:
            return JsonResponse(
                {'error': 'You have sent several messages. Please wait a minute and try again.'},
                status=429,
            )
        cache.set(rate_key, requests_made + 1, 60)

        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request.'}, status=400)

        question = str(payload.get('message', '')).strip()
        history = payload.get('history', [])
        if not question or len(question) > 500 or not isinstance(history, list):
            return JsonResponse({'error': 'Please enter a question under 500 characters.'}, status=400)

        try:
            answer = ask_portfolio_ai(question, history, Project.objects.all())
        except AIServiceError as exc:
            if str(exc) == 'AI_NOT_CONFIGURED':
                return JsonResponse({
                    'error': 'The AI assistant is being configured. Meanwhile, ask me about Mohit’s skills, projects, experience, or contact details.',
                    'code': 'not_configured',
                }, status=503)
            error_message = 'The assistant is taking a short break. Please try again in a moment.'
            if settings.DEBUG:
                error_message = f"Local AI error: {str(exc).removeprefix('AI_REQUEST_FAILED: ')}"
            return JsonResponse({'error': error_message}, status=502)
        return JsonResponse({'answer': answer})
