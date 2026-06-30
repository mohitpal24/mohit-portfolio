import json
from unittest.mock import patch

from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .models import Project, Service, ContactMessage
from .forms import ContactMessageForm

class PortfolioModelTests(TestCase):

    def test_service_tag_list_parsing(self):
        """Service tag_list splits a comma-separated string into a list of trimmed strings."""
        service = Service.objects.create(
            title="Cloud Integration",
            description="Deploying applications securely.",
            tags="Django, AWS, Docker, Kubernetes"
        )
        self.assertEqual(service.tag_list, ["Django", "AWS", "Docker", "Kubernetes"])

    def test_service_tag_list_empty(self):
        """Service tag_list returns an empty list if tags are empty or not present."""
        service = Service.objects.create(
            title="Consultation",
            description="Architecture talks.",
            tags=""
        )
        self.assertEqual(service.tag_list, [])

    def test_project_string_representation(self):
        """Project string representation returns the title."""
        project = Project.objects.create(
            title="Sample Web App",
            category="Web Dev",
            description="A sample test project."
        )
        self.assertEqual(str(project), "Sample Web App")

class PortfolioViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Seed migrations automatically populated some data, let's check
        # We can add explicit test instances here
        self.service = Service.objects.create(
            title="Cloud Infrastructure",
            description="Testing cloud scaling.",
            tags="AWS, GCP"
        )
        self.project = Project.objects.create(
            title="Microservices Setup",
            category="DevOps",
            description="Testing microservices views."
        )

    def test_index_page_status_code_and_template(self):
        """IndexView loads successfully and renders index.html."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio/index.html')
        self.assertIn('projects', response.context)
        self.assertIn('services', response.context)
        self.assertIn('contact_form', response.context)

    def test_contact_submit_post_redirect(self):
        """Standard POST submission redirects to index on success and saves message."""
        post_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello Mohit, love your portfolio!'
        }
        response = self.client.post(reverse('contact_submit'), data=post_data)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'John Doe')
        self.assertEqual(msg.email, 'john@example.com')
        self.assertEqual(msg.message, 'Hello Mohit, love your portfolio!')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_submit_ajax_success(self):
        """AJAX POST submission returns JSON response with success code."""
        post_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'message': 'Hi Mohit, let\'s collaborate!'
        }
        response = self.client.post(
            reverse('contact_submit'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'success': True,
            'message': 'Thank you! Your message has been sent successfully.'
        })
        self.assertEqual(ContactMessage.objects.filter(name='Jane Smith').count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Jane Smith', mail.outbox[0].subject)

    def test_contact_submit_ajax_validation_error(self):
        """AJAX POST submission with invalid email returns error details."""
        post_data = {
            'name': 'Invalid User',
            'email': 'not-an-email',
            'message': 'Testing bad email validation.'
        }
        response = self.client.post(
            reverse('contact_submit'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['errors'])
        self.assertEqual(ContactMessage.objects.filter(name='Invalid User').count(), 0)

    @override_settings(AI_API_KEY='test-key')
    @patch('portfolio.views.ask_portfolio_ai', return_value='A grounded AI response.')
    def test_chat_endpoint_returns_ai_answer(self, mock_ask):
        response = self.client.post(
            reverse('chat'),
            data=json.dumps({'message': 'Would Mohit fit a backend role?', 'history': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['answer'], 'A grounded AI response.')
        mock_ask.assert_called_once()

    @override_settings(AI_API_KEY='')
    def test_chat_endpoint_explains_missing_configuration(self):
        response = self.client.post(
            reverse('chat'),
            data=json.dumps({'message': 'Hello', 'history': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['code'], 'not_configured')
