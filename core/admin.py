from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ONG, CategoriaAlimento, Alimento, NecessidadeAlimento, Doacao


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'first_name', 'last_name', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'telefone', 'endereco')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'telefone', 'endereco')}),
    )


@admin.register(ONG)
class ONGAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'responsavel', 'telefone_contato', 'ativa', 'data_cadastro']
    list_filter = ['ativa', 'data_cadastro']
    search_fields = ['nome', 'cnpj', 'responsavel', 'email_contato']
    readonly_fields = ['data_cadastro']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'nome', 'cnpj', 'descricao', 'foto')
        }),
        ('Contato', {
            'fields': ('endereco_completo', 'telefone_contato', 'email_contato', 'responsavel')
        }),
        ('Status', {
            'fields': ('ativa', 'data_cadastro')
        }),
    )


@admin.register(CategoriaAlimento)
class CategoriaAlimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']


@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'unidade_medida']
    list_filter = ['categoria', 'unidade_medida']
    search_fields = ['nome', 'descricao']


@admin.register(NecessidadeAlimento)
class NecessidadeAlimentoAdmin(admin.ModelAdmin):
    list_display = ['ong', 'alimento', 'quantidade_necessaria', 'quantidade_recebida', 'prioridade', 'ativa']
    list_filter = ['prioridade', 'ativa', 'ong']
    search_fields = ['ong__nome', 'alimento__nome']
    readonly_fields = ['data_criacao']


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ['doador', 'ong', 'alimento', 'quantidade', 'status', 'data_doacao']
    list_filter = ['status', 'data_doacao', 'ong']
    search_fields = ['doador__username', 'ong__nome', 'alimento__nome']
    readonly_fields = ['data_doacao', 'data_atualizacao']
    fieldsets = (
        ('Informações da Doação', {
            'fields': ('doador', 'ong', 'alimento', 'quantidade')
        }),
        ('Status e Mensagem', {
            'fields': ('status', 'mensagem')
        }),
        ('Datas', {
            'fields': ('data_doacao', 'data_atualizacao')
        }),
    )
