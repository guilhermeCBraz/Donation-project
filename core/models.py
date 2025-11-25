from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Modelo de usuário customizado"""
    USER_TYPE_CHOICES = (
        ('cliente', 'Cliente'),
        ('ong', 'ONG'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='cliente',
        verbose_name='Tipo de Usuário'
    )
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, verbose_name='Endereço')
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ONG(models.Model):
    """Modelo para ONGs cadastradas no sistema"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ong_profile',
        verbose_name='Usuário'
    )
    nome = models.CharField(max_length=200, verbose_name='Nome da ONG')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    descricao = models.TextField(verbose_name='Descrição')
    endereco_completo = models.TextField(verbose_name='Endereço Completo')
    telefone_contato = models.CharField(max_length=20, verbose_name='Telefone de Contato')
    email_contato = models.EmailField(verbose_name='Email de Contato')
    responsavel = models.CharField(max_length=200, verbose_name='Responsável')
    foto = models.ImageField(upload_to='ongs/', blank=True, null=True, verbose_name='Foto')
    ativa = models.BooleanField(default=True, verbose_name='Ativa')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    
    class Meta:
        verbose_name = 'ONG'
        verbose_name_plural = 'ONGs'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class CategoriaAlimento(models.Model):
    """Categorias de alimentos"""
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    
    class Meta:
        verbose_name = 'Categoria de Alimento'
        verbose_name_plural = 'Categorias de Alimentos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Alimento(models.Model):
    """Alimentos disponíveis no sistema"""
    nome = models.CharField(max_length=200, verbose_name='Nome')
    categoria = models.ForeignKey(
        CategoriaAlimento,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alimentos',
        verbose_name='Categoria'
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    unidade_medida = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'Quilograma'),
            ('g', 'Grama'),
            ('l', 'Litro'),
            ('ml', 'Mililitro'),
            ('un', 'Unidade'),
            ('cx', 'Caixa'),
            ('pct', 'Pacote'),
        ],
        default='kg',
        verbose_name='Unidade de Medida'
    )
    
    class Meta:
        verbose_name = 'Alimento'
        verbose_name_plural = 'Alimentos'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_unidade_medida_display()})"


class NecessidadeAlimento(models.Model):
    """Necessidades de alimentos das ONGs"""
    ong = models.ForeignKey(
        ONG,
        on_delete=models.CASCADE,
        related_name='necessidades',
        verbose_name='ONG'
    )
    alimento = models.ForeignKey(
        Alimento,
        on_delete=models.CASCADE,
        related_name='necessidades',
        verbose_name='Alimento'
    )
    quantidade_necessaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantidade Necessária'
    )
    quantidade_recebida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Quantidade Recebida'
    )
    prioridade = models.CharField(
        max_length=10,
        choices=[
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente'),
        ],
        default='media',
        verbose_name='Prioridade'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    ativa = models.BooleanField(default=True, verbose_name='Ativa')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    
    class Meta:
        verbose_name = 'Necessidade de Alimento'
        verbose_name_plural = 'Necessidades de Alimentos'
        unique_together = ['ong', 'alimento']
        ordering = ['-prioridade', 'alimento__nome']
    
    def __str__(self):
        return f"{self.ong.nome} - {self.alimento.nome} ({self.quantidade_necessaria})"
    
    @property
    def quantidade_faltante(self):
        return max(0, self.quantidade_necessaria - self.quantidade_recebida)
    
    @property
    def percentual_recebido(self):
        if self.quantidade_necessaria > 0:
            return (self.quantidade_recebida / self.quantidade_necessaria) * 100
        return 0


class Doacao(models.Model):
    """Registro de doações realizadas"""
    doador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doacoes_realizadas',
        verbose_name='Doador'
    )
    ong = models.ForeignKey(
        ONG,
        on_delete=models.CASCADE,
        related_name='doacoes_recebidas',
        verbose_name='ONG Beneficiada'
    )
    alimento = models.ForeignKey(
        Alimento,
        on_delete=models.CASCADE,
        related_name='doacoes',
        verbose_name='Alimento'
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantidade'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('confirmada', 'Confirmada'),
            ('em_transito', 'Em Trânsito'),
            ('entregue', 'Entregue'),
            ('cancelada', 'Cancelada'),
        ],
        default='pendente',
        verbose_name='Status'
    )
    mensagem = models.TextField(blank=True, verbose_name='Mensagem do Doador')
    data_doacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Doação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data_doacao']
    
    def __str__(self):
        return f"{self.doador.username} → {self.ong.nome} - {self.alimento.nome} ({self.quantidade})"
