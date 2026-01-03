from django.urls import path
from . import views

app_name = 'tbase_admin'
urlpatterns = [
    path('performance/', views.performance_dashboard, name='performance_dashboard'),
    path('api/stats/', views.get_database_stats, name='get_database_stats'),
    path('cleanup/sessions/', views.cleanup_sessions, name='cleanup_sessions'),
    path('cleanup/sessions/advanced/', views.cleanup_sessions_advanced, name='cleanup_sessions_advanced'),
    path('cleanup/hitcount/', views.cleanup_hitcount, name='cleanup_hitcount'),
    path('optimize/tables/', views.optimize_tables, name='optimize_tables'),
    path('api/optimize-results/', views.get_optimize_results, name='get_optimize_results'),
]