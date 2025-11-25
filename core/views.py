from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal, InvalidOperation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, ONG, Alimento, NecessidadeAlimento, Doacao, CategoriaAlimento


def home(request):
    """Página inicial - redireciona baseado no tipo de usuário"""
    if request.user.is_authenticated:
        if request.user.user_type == 'ong':
            return redirect('core:dashboard_ong')
        else:
            return redirect('core:dashboard_cliente')
    return render(request, 'core/home.html')


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
            
            # Redireciona baseado no tipo de usuário
            if user.user_type == 'ong':
                return redirect('core:dashboard_ong')
            else:
                return redirect('core:dashboard_cliente')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'core/login.html')


def register_view(request):
    """View de registro"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefone = request.POST.get('telefone')
        user_type = request.POST.get('user_type', 'cliente')
        
        if password != password2:
            messages.error(request, 'As senhas não coincidem.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                telefone=telefone,
                user_type=user_type
            )
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('core:login')
    
    return render(request, 'core/register.html')


@login_required
def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:home')


@login_required
def dashboard_cliente(request):
    """Dashboard para clientes - mostra ONGs e suas necessidades"""
    if request.user.user_type != 'cliente':
        return redirect('core:dashboard_ong')
    
    # Buscar todas as ONGs ativas
    ongs = ONG.objects.filter(ativa=True).prefetch_related('necessidades__alimento')
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    
    if search:
        ongs = ongs.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    # Buscar necessidades ativas
    necessidades = NecessidadeAlimento.objects.filter(
        ativa=True,
        ong__ativa=True
    ).select_related('ong', 'alimento', 'alimento__categoria')
    
    if categoria_id:
        necessidades = necessidades.filter(alimento__categoria_id=categoria_id)
    
    if search:
        necessidades = necessidades.filter(
            Q(ong__nome__icontains=search) |
            Q(alimento__nome__icontains=search)
        )
    
    # Minhas doações recentes
    minhas_doacoes = Doacao.objects.filter(doador=request.user).select_related(
        'ong', 'alimento'
    )[:5]
    
    categorias = CategoriaAlimento.objects.all()
    
    context = {
        'ongs': ongs,
        'necessidades': necessidades,
        'minhas_doacoes': minhas_doacoes,
        'categorias': categorias,
        'search': search,
    }
    return render(request, 'core/dashboard_cliente.html', context)


@login_required
def dashboard_ong(request):
    """Dashboard para ONGs - gerenciar necessidades e ver doações"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    # Necessidades da ONG
    necessidades = NecessidadeAlimento.objects.filter(ong=ong).select_related('alimento')
    
    # Doações recebidas
    doacoes_recebidas = Doacao.objects.filter(ong=ong).select_related(
        'doador', 'alimento'
    ).order_by('-data_doacao')[:10]
    
    # Estatísticas
    total_doacoes = Doacao.objects.filter(ong=ong, status='entregue').count()
    total_alimentos = necessidades.aggregate(
        total=Sum('quantidade_recebida')
    )['total'] or 0
    
    context = {
        'ong': ong,
        'necessidades': necessidades,
        'doacoes_recebidas': doacoes_recebidas,
        'total_doacoes': total_doacoes,
        'total_alimentos': total_alimentos,
    }
    return render(request, 'core/dashboard_ong.html', context)


@login_required
def doar_alimento(request, necessidade_id):
    """Realizar doação para uma necessidade específica"""
    if request.user.user_type != 'cliente':
        messages.error(request, 'Apenas clientes podem fazer doações.')
        return redirect('core:home')
    
    necessidade = get_object_or_404(
        NecessidadeAlimento.objects.select_related('ong', 'alimento'),
        id=necessidade_id,
        ativa=True
    )
    
    if request.method == 'POST':
        quantidade = request.POST.get('quantidade')
        mensagem = request.POST.get('mensagem', '')
        
        try:
            quantidade = float(quantidade)
            if quantidade <= 0:
                raise ValueError()
            
            # Criar doação
            doacao = Doacao.objects.create(
                doador=request.user,
                ong=necessidade.ong,
                alimento=necessidade.alimento,
                quantidade=quantidade,
                mensagem=mensagem,
                status='pendente'
            )
            
            messages.success(
                request,
                f'Doação de {quantidade} {necessidade.alimento.get_unidade_medida_display()} '
                f'de {necessidade.alimento.nome} realizada com sucesso!'
            )
            return redirect('core:minhas_doacoes')
            
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade inválida.')
    
    context = {
        'necessidade': necessidade,
    }
    return render(request, 'core/doar_alimento.html', context)


@login_required
def minhas_doacoes(request):
    """Ver histórico de doações do cliente"""
    if request.user.user_type != 'cliente':
        return redirect('core:dashboard_ong')
    
    doacoes = Doacao.objects.filter(doador=request.user).select_related(
        'ong', 'alimento'
    ).order_by('-data_doacao')
    
    context = {
        'doacoes': doacoes,
    }
    return render(request, 'core/minhas_doacoes.html', context)


@login_required
def ong_detalhes(request, ong_id):
    """Detalhes de uma ONG específica"""
    ong = get_object_or_404(ONG, id=ong_id, ativa=True)
    necessidades = NecessidadeAlimento.objects.filter(
        ong=ong,
        ativa=True
    ).select_related('alimento')
    
    context = {
        'ong': ong,
        'necessidades': necessidades,
    }
    return render(request, 'core/ong_detalhes.html', context)


@login_required
def atualizar_status_doacao(request, doacao_id):
    """ONG atualiza o status de uma doação"""
    if request.user.user_type != 'ong':
        messages.error(request, 'Apenas ONGs podem atualizar status de doações.')
        return redirect('core:home')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    doacao = get_object_or_404(Doacao, id=doacao_id, ong=ong)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        
        if novo_status in ['confirmada', 'em_transito', 'entregue', 'cancelada']:
            status_anterior = doacao.status
            doacao.status = novo_status
            doacao.save()
            
            # Atualizar quantidade recebida quando confirmada ou entregue
            if novo_status in ['confirmada', 'entregue'] and status_anterior == 'pendente':
                try:
                    necessidade = NecessidadeAlimento.objects.get(
                        ong=ong,
                        alimento=doacao.alimento
                    )
                    necessidade.quantidade_recebida += doacao.quantidade
                    necessidade.save()
                    
                    # Verificar se a necessidade foi completada
                    if necessidade.quantidade_recebida >= necessidade.quantidade_necessaria:
                        necessidade.ativa = False
                        necessidade.save()
                        messages.success(
                            request,
                            f'🎉 Parabéns! A necessidade de {doacao.alimento.nome} foi completada! '
                            f'Total recebido: {necessidade.quantidade_recebida} {doacao.alimento.get_unidade_medida_display()}'
                        )
                    else:
                        messages.success(
                            request,
                            f'Doação {doacao.get_status_display().lower()}! Quantidade atualizada: '
                            f'+{doacao.quantidade} {doacao.alimento.get_unidade_medida_display()} '
                            f'({necessidade.percentual_recebido:.0f}% da meta)'
                        )
                except NecessidadeAlimento.DoesNotExist:
                    messages.success(request, f'Status atualizado para: {doacao.get_status_display()}')
            else:
                messages.success(request, f'Status atualizado para: {doacao.get_status_display()}')
        else:
            messages.error(request, 'Status inválido.')
    
    return redirect('core:dashboard_ong')


@login_required
def gerenciar_necessidades_ong(request):
    """Página para ONG gerenciar suas necessidades de alimentos"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    necessidades = NecessidadeAlimento.objects.filter(ong=ong).select_related(
        'alimento', 'alimento__categoria'
    ).order_by('-ativa', '-prioridade', 'alimento__nome')
    
    # Calcular estatísticas
    total_necessidades = necessidades.count()
    necessidades_ativas = necessidades.filter(ativa=True).count()
    necessidades_concluidas = total_necessidades - necessidades_ativas
    
    context = {
        'ong': ong,
        'necessidades': necessidades,
        'total_necessidades': total_necessidades,
        'necessidades_ativas': necessidades_ativas,
        'necessidades_concluidas': necessidades_concluidas,
    }
    return render(request, 'core/gerenciar_necessidades.html', context)


@login_required
def adicionar_necessidade(request):
    """Adicionar nova necessidade de alimento"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    if request.method == 'POST':
        alimento_id = request.POST.get('alimento')
        quantidade_str = request.POST.get('quantidade_necessaria')
        prioridade = request.POST.get('prioridade')
        observacoes = request.POST.get('observacoes', '')
        
        try:
            alimento = Alimento.objects.get(id=alimento_id)
            
            # Converter e validar quantidade
            quantidade_dec = Decimal(str(quantidade_str))
            if quantidade_dec <= 0:
                messages.error(request, 'A quantidade deve ser maior que zero.')
                return render(request, 'core/adicionar_necessidade.html', {
                    'ong': ong,
                    'alimentos': Alimento.objects.all().select_related('categoria').order_by('categoria__nome', 'nome'),
                    'categorias': CategoriaAlimento.objects.all(),
                })
            
            # Verificar se já existe necessidade ativa para este alimento
            if NecessidadeAlimento.objects.filter(ong=ong, alimento=alimento, ativa=True).exists():
                messages.error(request, f'Já existe uma necessidade ativa para {alimento.nome}.')
            else:
                NecessidadeAlimento.objects.create(
                    ong=ong,
                    alimento=alimento,
                    quantidade_necessaria=quantidade_dec,
                    prioridade=prioridade,
                    observacoes=observacoes,
                    ativa=True
                )
                messages.success(request, f'Necessidade de {alimento.nome} adicionada com sucesso!')
            
            return redirect('core:gerenciar_necessidades_ong')
        except Alimento.DoesNotExist:
            messages.error(request, 'Alimento não encontrado.')
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, 'Quantidade inválida.')
    
    alimentos = Alimento.objects.all().select_related('categoria').order_by('categoria__nome', 'nome')
    categorias = CategoriaAlimento.objects.all()
    
    context = {
        'ong': ong,
        'alimentos': alimentos,
        'categorias': categorias,
    }
    return render(request, 'core/adicionar_necessidade.html', context)


@login_required
def editar_necessidade(request, necessidade_id):
    """Editar necessidade existente"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    necessidade = get_object_or_404(NecessidadeAlimento, id=necessidade_id, ong=ong)
    
    if request.method == 'POST':
        quantidade_str = request.POST.get('quantidade_necessaria')
        prioridade = request.POST.get('prioridade')
        observacoes = request.POST.get('observacoes', '')
        ativa = request.POST.get('ativa') == 'on'

        try:
            # Converter para Decimal e validar
            quantidade_dec = Decimal(str(quantidade_str))
            if quantidade_dec < necessidade.quantidade_recebida:
                messages.error(request, 'A quantidade necessária não pode ser menor que a já recebida.')
            else:
                necessidade.quantidade_necessaria = quantidade_dec
                necessidade.prioridade = prioridade
                necessidade.observacoes = observacoes
                necessidade.ativa = ativa
                necessidade.save()
                messages.success(request, f'Necessidade de {necessidade.alimento.nome} atualizada!')
                return redirect('core:gerenciar_necessidades_ong')
        except (InvalidOperation, TypeError):
            messages.error(request, 'Quantidade inválida.')
    
    context = {
        'ong': ong,
        'necessidade': necessidade,
    }
    return render(request, 'core/editar_necessidade.html', context)


@login_required
def excluir_necessidade(request, necessidade_id):
    """Excluir (desativar) necessidade"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    necessidade = get_object_or_404(NecessidadeAlimento, id=necessidade_id, ong=ong)
    
    if request.method == 'POST':
        necessidade.ativa = False
        necessidade.save()
        messages.success(request, f'Necessidade de {necessidade.alimento.nome} desativada.')
    
    return redirect('core:gerenciar_necessidades_ong')


@login_required
def gerenciar_doacoes_ong(request):
    """Página para ONG gerenciar todas as doações"""
    if request.user.user_type != 'ong':
        return redirect('core:dashboard_cliente')
    
    try:
        ong = request.user.ong_profile
    except ONG.DoesNotExist:
        messages.error(request, 'Você precisa ter um perfil de ONG cadastrado.')
        return redirect('core:home')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    
    doacoes = Doacao.objects.filter(ong=ong).select_related('doador', 'alimento').order_by('-data_doacao')
    
    if status_filter:
        doacoes = doacoes.filter(status=status_filter)
    
    # Estatísticas por status
    stats = {
        'pendente': Doacao.objects.filter(ong=ong, status='pendente').count(),
        'confirmada': Doacao.objects.filter(ong=ong, status='confirmada').count(),
        'em_transito': Doacao.objects.filter(ong=ong, status='em_transito').count(),
        'entregue': Doacao.objects.filter(ong=ong, status='entregue').count(),
        'cancelada': Doacao.objects.filter(ong=ong, status='cancelada').count(),
    }
    
    context = {
        'ong': ong,
        'doacoes': doacoes,
        'stats': stats,
        'status_filter': status_filter,
    }
    return render(request, 'core/gerenciar_doacoes.html', context)


@login_required
def dashboard_admin(request):
    """Dashboard administrativo completo"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado. Apenas administradores.')
        return redirect('core:home')
    
    from django.db.models import Count, Sum, Q
    from datetime import datetime, timedelta
    
    # Estatísticas gerais
    total_usuarios = User.objects.count()
    total_clientes = User.objects.filter(user_type='cliente').count()
    total_usuarios_ong = User.objects.filter(user_type='ong').count()
    total_ongs = ONG.objects.count()
    ongs_ativas = ONG.objects.filter(ativa=True).count()
    
    total_alimentos = Alimento.objects.count()
    total_categorias = CategoriaAlimento.objects.count()
    
    total_necessidades = NecessidadeAlimento.objects.count()
    necessidades_ativas = NecessidadeAlimento.objects.filter(ativa=True).count()
    necessidades_completadas = NecessidadeAlimento.objects.filter(ativa=False).count()
    
    total_doacoes = Doacao.objects.count()
    doacoes_pendentes = Doacao.objects.filter(status='pendente').count()
    doacoes_confirmadas = Doacao.objects.filter(status='confirmada').count()
    doacoes_em_transito = Doacao.objects.filter(status='em_transito').count()
    doacoes_entregues = Doacao.objects.filter(status='entregue').count()
    doacoes_canceladas = Doacao.objects.filter(status='cancelada').count()
    
    # Doações dos últimos 7 dias
    sete_dias_atras = datetime.now() - timedelta(days=7)
    doacoes_recentes = Doacao.objects.filter(data_doacao__gte=sete_dias_atras).count()
    
    # Top 5 ONGs que mais receberam doações
    top_ongs = ONG.objects.annotate(
        num_doacoes=Count('doacoes_recebidas', filter=Q(doacoes_recebidas__status='entregue'))
    ).order_by('-num_doacoes')[:5]
    
    # Top 5 doadores
    top_doadores = User.objects.filter(user_type='cliente').annotate(
        num_doacoes=Count('doacoes_realizadas', filter=Q(doacoes_realizadas__status='entregue'))
    ).order_by('-num_doacoes')[:5]
    
    # Top 5 alimentos mais doados
    top_alimentos = Alimento.objects.annotate(
        total_doacoes=Count('doacoes', filter=Q(doacoes__status='entregue'))
    ).order_by('-total_doacoes')[:5]
    
    # Últimas atividades
    ultimas_doacoes = Doacao.objects.select_related('doador', 'ong', 'alimento').order_by('-data_doacao')[:10]
    ultimos_usuarios = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_usuarios_ong': total_usuarios_ong,
        'total_ongs': total_ongs,
        'ongs_ativas': ongs_ativas,
        'total_alimentos': total_alimentos,
        'total_categorias': total_categorias,
        'total_necessidades': total_necessidades,
        'necessidades_ativas': necessidades_ativas,
        'necessidades_completadas': necessidades_completadas,
        'total_doacoes': total_doacoes,
        'doacoes_pendentes': doacoes_pendentes,
        'doacoes_confirmadas': doacoes_confirmadas,
        'doacoes_em_transito': doacoes_em_transito,
        'doacoes_entregues': doacoes_entregues,
        'doacoes_canceladas': doacoes_canceladas,
        'doacoes_recentes': doacoes_recentes,
        'top_ongs': top_ongs,
        'top_doadores': top_doadores,
        'top_alimentos': top_alimentos,
        'ultimas_doacoes': ultimas_doacoes,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'core/dashboard_admin.html', context)


@api_view(['GET'])
def api_status(request):
    """Endpoint de API para verificar o status do sistema"""
    return Response({
        'status': 'online',
        'message': 'Donation Project API está funcionando!',
        'total_ongs': ONG.objects.filter(ativa=True).count(),
        'total_necessidades': NecessidadeAlimento.objects.filter(ativa=True).count(),
        'total_doacoes': Doacao.objects.count(),
    })
