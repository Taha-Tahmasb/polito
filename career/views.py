from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import CompanyForm, JobApplicationForm
from .models import Company, JobApplication


class CareerOwnerMixin(LoginRequiredMixin):
    login_url = reverse_lazy('portfolio:login')

    def get_companies(self):
        return Company.objects.filter(owner=self.request.user)

    def get_applications(self):
        return JobApplication.objects.filter(owner=self.request.user).select_related('company')


class CareerDashboardView(CareerOwnerMixin, TemplateView):
    template_name = 'career/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = self.get_applications()
        status_counts = applications.values('status').annotate(total=Count('id')).order_by('status')
        active_count = applications.filter(status__in=JobApplication.active_statuses()).count()
        context.update(
            {
                'total_applications': applications.count(),
                'active_applications': active_count,
                'interview_count': applications.filter(status=JobApplication.Status.INTERVIEW).count(),
                'offer_count': applications.filter(status=JobApplication.Status.OFFER).count(),
                'follow_ups': applications.filter(
                    follow_up_on__isnull=False,
                    status__in=JobApplication.active_statuses(),
                ).order_by('follow_up_on')[:5],
                'recent_applications': applications.order_by('-created_at')[:6],
                'status_rows': status_counts,
            }
        )
        return context


class JobApplicationListView(CareerOwnerMixin, ListView):
    model = JobApplication
    template_name = 'career/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        queryset = self.get_applications().order_by('follow_up_on', '-applied_at')
        status = self.request.GET.get('status')
        query = self.request.GET.get('q')
        if status:
            queryset = queryset.filter(status=status)
        if query:
            queryset = queryset.filter(Q(role__icontains=query) | Q(company__name__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'status_choices': JobApplication.Status.choices,
                'selected_status': self.request.GET.get('status', ''),
                'search_query': self.request.GET.get('q', ''),
            }
        )
        return context


class CompanyCreateView(CareerOwnerMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'career/form.html'
    success_url = reverse_lazy('career:application-create')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Company saved. Now add the job application details.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add target company'
        context['form_hint'] = 'Keep a reusable company record for every opportunity you track.'
        return context


class JobApplicationCreateView(CareerOwnerMixin, CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'career/form.html'
    success_url = reverse_lazy('career:applications')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Application saved. Keep the next follow-up visible.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Track job application'
        context['form_hint'] = 'Record the role, source, status, contact, and next step in one place.'
        context['empty_company_cta'] = not self.get_companies().exists()
        return context


class JobApplicationUpdateView(CareerOwnerMixin, UpdateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'career/form.html'
    success_url = reverse_lazy('career:applications')

    def get_queryset(self):
        return self.get_applications()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Application updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update application'
        context['form_hint'] = 'Refresh the status, follow-up date, and notes after every contact.'
        return context


class JobApplicationDeleteView(CareerOwnerMixin, DeleteView):
    model = JobApplication
    template_name = 'career/confirm_delete.html'
    success_url = reverse_lazy('career:applications')

    def get_queryset(self):
        return self.get_applications()

    def form_valid(self, form):
        messages.success(self.request, 'Application removed.')
        return super().form_valid(form)
