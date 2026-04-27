from django import forms

from .models import Company, JobApplication


class DateInput(forms.DateInput):
    input_type = 'date'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'location', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'company',
            'role',
            'status',
            'source',
            'job_url',
            'location',
            'salary_range',
            'contact_name',
            'contact_email',
            'next_step',
            'applied_at',
            'follow_up_on',
            'notes',
        ]
        widgets = {
            'applied_at': DateInput(),
            'follow_up_on': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['company'].queryset = Company.objects.filter(owner=user)
