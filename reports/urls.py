from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report dashboard (main view)
    path('', views.report_dashboard, name='overview'),
    
    # List all saved reports
    path('saved', views.ReportListView.as_view(), name='list'),
    
    # Standard report creation
    path('create/daily/', lambda request: views.create_standard_report(request, 'daily'), name='create_daily'),
    path('create/weekly/', lambda request: views.create_standard_report(request, 'weekly'), name='create_weekly'),
    path('create/monthly/', lambda request: views.create_standard_report(request, 'monthly'), name='create_monthly'),
    path('create/yearly/', lambda request: views.create_standard_report(request, 'yearly'), name='create_yearly'),
    
    # Custom report creation
    path('create/custom/', views.create_custom_report, name='create_custom'),
    
    # Report details and actions
    path('<int:pk>/', views.ReportDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.ReportDeleteView.as_view(), name='delete'),
    path('<int:pk>/download/', views.download_report, name='download'),
]