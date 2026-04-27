from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Company, JobApplication


class CareerTrackerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jobhunter', password='secret123')
        self.other_user = User.objects.create_user(username='private', password='secret123')
        self.company = Company.objects.create(owner=self.user, name='Northstar Labs', location='Remote')
        self.other_company = Company.objects.create(owner=self.other_user, name='Hidden Corp')
        self.application = JobApplication.objects.create(
            owner=self.user,
            company=self.company,
            role='Junior Django Developer',
            status=JobApplication.Status.INTERVIEW,
            source='Referral',
            next_step='Send portfolio link',
            follow_up_on=timezone.localdate(),
        )
        JobApplication.objects.create(
            owner=self.other_user,
            company=self.other_company,
            role='Secret Role',
            status=JobApplication.Status.APPLIED,
        )

    def test_career_dashboard_requires_login(self):
        response = self.client.get(reverse('career:dashboard'))
        self.assertRedirects(response, '/login/?next=/career/')

    def test_dashboard_shows_owned_pipeline_stats(self):
        self.client.login(username='jobhunter', password='secret123')
        response = self.client.get(reverse('career:dashboard'))

        self.assertContains(response, 'Career command center')
        self.assertContains(response, 'Junior Django Developer')
        self.assertContains(response, 'Northstar Labs')
        self.assertNotContains(response, 'Secret Role')

    def test_application_create_assigns_owner_and_filters_companies(self):
        self.client.login(username='jobhunter', password='secret123')
        response = self.client.post(
            reverse('career:application-create'),
            {
                'company': self.company.pk,
                'role': 'Python Intern',
                'status': JobApplication.Status.APPLIED,
                'source': 'Company site',
                'job_url': 'https://example.com/jobs/python-intern',
                'location': 'Turin',
                'salary_range': '',
                'contact_name': '',
                'contact_email': '',
                'next_step': 'Follow up in one week',
                'applied_at': '2026-04-20',
                'follow_up_on': '2026-04-27',
                'notes': 'Tailored CV submitted.',
            },
        )

        self.assertRedirects(response, reverse('career:applications'))
        self.assertTrue(JobApplication.objects.filter(owner=self.user, role='Python Intern').exists())

    def test_application_form_rejects_other_users_company(self):
        self.client.login(username='jobhunter', password='secret123')
        response = self.client.post(
            reverse('career:application-create'),
            {
                'company': self.other_company.pk,
                'role': 'Should Not Save',
                'status': JobApplication.Status.APPLIED,
                'applied_at': '2026-04-20',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(JobApplication.objects.filter(role='Should Not Save').exists())

    def test_application_update_blocks_other_users_records(self):
        other_application = JobApplication.objects.get(owner=self.other_user)
        self.client.login(username='jobhunter', password='secret123')
        response = self.client.get(reverse('career:application-edit', args=[other_application.pk]))

        self.assertEqual(response.status_code, 404)


class SeedCareerDataCommandTests(TestCase):
    def test_seed_career_data_creates_demo_pipeline(self):
        call_command('seed_career_data', username='career_demo')

        user = User.objects.get(username='career_demo')
        self.assertEqual(Company.objects.filter(owner=user).count(), 3)
        self.assertEqual(JobApplication.objects.filter(owner=user).count(), 3)
        self.assertTrue(JobApplication.objects.filter(owner=user, status=JobApplication.Status.INTERVIEW).exists())
