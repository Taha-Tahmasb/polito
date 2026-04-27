from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property


class Company(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='career_companies', on_delete=models.CASCADE)
    name = models.CharField(max_length=140)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('owner', 'name')
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class JobApplication(models.Model):
    class Status(models.TextChoices):
        SAVED = 'saved', 'Saved'
        APPLIED = 'applied', 'Applied'
        SCREENING = 'screening', 'Screening'
        INTERVIEW = 'interview', 'Interview'
        OFFER = 'offer', 'Offer'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='job_applications', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='applications', on_delete=models.CASCADE)
    role = models.CharField(max_length=160)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SAVED)
    source = models.CharField(max_length=120, blank=True, help_text='LinkedIn, referral, company site, or job board')
    job_url = models.URLField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    salary_range = models.CharField(max_length=80, blank=True)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    next_step = models.CharField(max_length=180, blank=True)
    applied_at = models.DateField(default=timezone.localdate)
    follow_up_on = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['follow_up_on', '-applied_at', 'company__name']

    def __str__(self):
        return f'{self.role} at {self.company.name}'

    @cached_property
    def days_since_applied(self):
        return max((timezone.localdate() - self.applied_at).days, 0)

    @property
    def needs_follow_up(self):
        return bool(self.follow_up_on and self.follow_up_on <= timezone.localdate() and self.status in self.active_statuses())

    @classmethod
    def active_statuses(cls):
        return [cls.Status.SAVED, cls.Status.APPLIED, cls.Status.SCREENING, cls.Status.INTERVIEW]
