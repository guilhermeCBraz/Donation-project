from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticação
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/ong/', views.dashboard_ong, name='dashboard_ong'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    
    # Doações
    path('doar/<int:necessidade_id>/', views.doar_alimento, name='doar_alimento'),
    path('minhas-doacoes/', views.minhas_doacoes, name='minhas_doacoes'),
    
    # Gerenciamento ONG - Doações
    path('ong/gerenciar-doacoes/', views.gerenciar_doacoes_ong, name='gerenciar_doacoes_ong'),
    path('ong/atualizar-status/<int:doacao_id>/', views.atualizar_status_doacao, name='atualizar_status_doacao'),
    
    # Gerenciamento ONG - Necessidades
    path('ong/gerenciar-necessidades/', views.gerenciar_necessidades_ong, name='gerenciar_necessidades_ong'),
    path('ong/adicionar-necessidade/', views.adicionar_necessidade, name='adicionar_necessidade'),
    path('ong/editar-necessidade/<int:necessidade_id>/', views.editar_necessidade, name='editar_necessidade'),
    path('ong/excluir-necessidade/<int:necessidade_id>/', views.excluir_necessidade, name='excluir_necessidade'),
    
    # ONGs
    path('ong/<int:ong_id>/', views.ong_detalhes, name='ong_detalhes'),
    
    # API
    path('api/status/', views.api_status, name='api_status'),
]
