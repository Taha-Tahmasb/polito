from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from career.models import Company, JobApplication


class Command(BaseCommand):
    help = 'Create a demo job-search pipeline for the Career Hub app.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo', help='User that receives the sample career data.')

    def handle(self, *args, **options):
        username = options['username']
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com'},
        )

        if JobApplication.objects.filter(owner=user).exists():
            self.stdout.write(self.style.WARNING(f'Career data already exists for "{username}". Nothing changed.'))
            return

        today = timezone.localdate()
        northstar = Company.objects.create(owner=user, name='Northstar Labs', website='https://example.com', location='Remote')
        finstack = Company.objects.create(owner=user, name='Finstack Studio', location='Hybrid')
        greenbyte = Company.objects.create(owner=user, name='Greenbyte Cloud', location='Turin')

        JobApplication.objects.bulk_create(
            [
                JobApplication(
                    owner=user,
                    company=northstar,
                    role='Junior Django Developer',
                    status=JobApplication.Status.INTERVIEW,
                    source='Referral',
                    location='Remote',
                    next_step='Send portfolio link and prepare API discussion.',
                    applied_at=today,
                    follow_up_on=today,
                    notes='Strong fit for Django, auth, dashboards, and tests.',
                ),
                JobApplication(
                    owner=user,
                    company=finstack,
                    role='Backend Python Intern',
                    status=JobApplication.Status.APPLIED,
                    source='Company careers page',
                    location='Hybrid',
                    next_step='Follow up with recruiter.',
                    applied_at=today,
                    follow_up_on=today.replace(day=min(today.day + 3, 28)),
                ),
                JobApplication(
                    owner=user,
                    company=greenbyte,
                    role='Data Platform Trainee',
                    status=JobApplication.Status.SAVED,
                    source='LinkedIn',
                    location='Turin',
                    next_step='Customize CV around SQL and reporting projects.',
                    applied_at=today,
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS(f'Seeded Career Hub data for "{username}".'))
