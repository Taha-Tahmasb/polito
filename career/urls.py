from django.urls import path

from .views import (
    CareerDashboardView,
    CompanyCreateView,
    JobApplicationCreateView,
    JobApplicationDeleteView,
    JobApplicationListView,
    JobApplicationUpdateView,
)

app_name = 'career'

urlpatterns = [
    path('', CareerDashboardView.as_view(), name='dashboard'),
    path('applications/', JobApplicationListView.as_view(), name='applications'),
    path('applications/create/', JobApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/edit/', JobApplicationUpdateView.as_view(), name='application-edit'),
    path('applications/<int:pk>/delete/', JobApplicationDeleteView.as_view(), name='application-delete'),
    path('companies/create/', CompanyCreateView.as_view(), name='company-create'),
]
