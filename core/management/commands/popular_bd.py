from django.core.management.base import BaseCommand
from core.models import User, ONG, CategoriaAlimento, Alimento, NecessidadeAlimento, Doacao


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de exemplo...')
        
        # Criar superusuário
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superusuário criado (admin/admin123)'))
        
        # Criar cliente de exemplo
        if not User.objects.filter(username='joao').exists():
            cliente = User.objects.create_user(
                username='joao',
                email='joao@example.com',
                password='senha123',
                first_name='João',
                last_name='Silva',
                user_type='cliente',
                telefone='(11) 98765-4321'
            )
            self.stdout.write(self.style.SUCCESS('✓ Cliente criado (joao/senha123)'))
        
        # Criar usuário ONG
        if not User.objects.filter(username='ong_esperanca').exists():
            user_ong1 = User.objects.create_user(
                username='ong_esperanca',
                email='contato@esperanca.org',
                password='senha123',
                first_name='ONG',
                last_name='Esperança',
                user_type='ong'
            )
            
            ong1 = ONG.objects.create(
                user=user_ong1,
                nome='ONG Esperança',
                cnpj='12.345.678/0001-90',
                descricao='Ajudamos famílias carentes com alimentação e educação.',
                endereco_completo='Rua das Flores, 123 - São Paulo, SP',
                telefone_contato='(11) 3456-7890',
                email_contato='contato@esperanca.org',
                responsavel='Maria Santos'
            )
            self.stdout.write(self.style.SUCCESS('✓ ONG Esperança criada (ong_esperanca/senha123)'))
        
        if not User.objects.filter(username='ong_solidaria').exists():
            user_ong2 = User.objects.create_user(
                username='ong_solidaria',
                email='contato@solidaria.org',
                password='senha123',
                first_name='ONG',
                last_name='Solidária',
                user_type='ong'
            )
            
            ong2 = ONG.objects.create(
                user=user_ong2,
                nome='Instituto Solidariedade',
                cnpj='98.765.432/0001-10',
                descricao='Combatendo a fome e promovendo inclusão social.',
                endereco_completo='Av. Paulista, 456 - São Paulo, SP',
                telefone_contato='(11) 2345-6789',
                email_contato='contato@solidaria.org',
                responsavel='Carlos Oliveira'
            )
            self.stdout.write(self.style.SUCCESS('✓ Instituto Solidariedade criado (ong_solidaria/senha123)'))
        
        # Criar categorias
        categorias = [
            ('Grãos e Cereais', 'Arroz, feijão, milho, trigo, etc.'),
            ('Proteínas', 'Carnes, ovos, leite, queijos, etc.'),
            ('Frutas e Verduras', 'Frutas frescas, verduras e legumes'),
            ('Enlatados', 'Alimentos em conserva'),
            ('Bebidas', 'Sucos, água, leite'),
        ]
        
        for nome, desc in categorias:
            CategoriaAlimento.objects.get_or_create(nome=nome, defaults={'descricao': desc})
        
        self.stdout.write(self.style.SUCCESS('✓ Categorias criadas'))
        
        # Criar alimentos
        cat_graos = CategoriaAlimento.objects.get(nome='Grãos e Cereais')
        cat_proteinas = CategoriaAlimento.objects.get(nome='Proteínas')
        cat_frutas = CategoriaAlimento.objects.get(nome='Frutas e Verduras')
        cat_enlatados = CategoriaAlimento.objects.get(nome='Enlatados')
        cat_bebidas = CategoriaAlimento.objects.get(nome='Bebidas')
        
        alimentos = [
            ('Arroz', cat_graos, 'kg'),
            ('Feijão', cat_graos, 'kg'),
            ('Macarrão', cat_graos, 'kg'),
            ('Farinha de Trigo', cat_graos, 'kg'),
            ('Leite', cat_proteinas, 'l'),
            ('Ovos', cat_proteinas, 'un'),
            ('Frango', cat_proteinas, 'kg'),
            ('Banana', cat_frutas, 'kg'),
            ('Maçã', cat_frutas, 'kg'),
            ('Tomate', cat_frutas, 'kg'),
            ('Batata', cat_frutas, 'kg'),
            ('Milho Enlatado', cat_enlatados, 'un'),
            ('Ervilha Enlatada', cat_enlatados, 'un'),
            ('Molho de Tomate', cat_enlatados, 'un'),
            ('Suco de Laranja', cat_bebidas, 'l'),
            ('Água Mineral', cat_bebidas, 'l'),
        ]
        
        for nome, categoria, unidade in alimentos:
            Alimento.objects.get_or_create(
                nome=nome,
                defaults={
                    'categoria': categoria,
                    'unidade_medida': unidade
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Alimentos criados'))
        
        # Criar necessidades para as ONGs
        try:
            ong1 = ONG.objects.get(nome='ONG Esperança')
            ong2 = ONG.objects.get(nome='Instituto Solidariedade')
            
            necessidades_ong1 = [
                ('Arroz', 100, 'urgente', 'Precisamos urgentemente para cestas básicas'),
                ('Feijão', 80, 'alta', 'Essencial para alimentação das famílias'),
                ('Leite', 50, 'alta', 'Para crianças e idosos'),
                ('Ovos', 200, 'media', ''),
                ('Banana', 30, 'baixa', ''),
            ]
            
            for nome_alimento, qtd, prioridade, obs in necessidades_ong1:
                alimento = Alimento.objects.get(nome=nome_alimento)
                NecessidadeAlimento.objects.get_or_create(
                    ong=ong1,
                    alimento=alimento,
                    defaults={
                        'quantidade_necessaria': qtd,
                        'prioridade': prioridade,
                        'observacoes': obs
                    }
                )
            
            necessidades_ong2 = [
                ('Macarrão', 60, 'urgente', 'Nosso estoque está acabando'),
                ('Molho de Tomate', 40, 'media', ''),
                ('Frango', 25, 'alta', 'Proteína essencial'),
                ('Água Mineral', 100, 'alta', 'Para distribuição'),
                ('Farinha de Trigo', 40, 'media', 'Para oficina de panificação'),
            ]
            
            for nome_alimento, qtd, prioridade, obs in necessidades_ong2:
                alimento = Alimento.objects.get(nome=nome_alimento)
                NecessidadeAlimento.objects.get_or_create(
                    ong=ong2,
                    alimento=alimento,
                    defaults={
                        'quantidade_necessaria': qtd,
                        'prioridade': prioridade,
                        'observacoes': obs
                    }
                )
            
            self.stdout.write(self.style.SUCCESS('✓ Necessidades criadas'))
        except ONG.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ ONGs não encontradas, pulando criação de necessidades'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Dados de exemplo criados com sucesso!'))
        self.stdout.write(self.style.SUCCESS('\n📝 Contas criadas:'))
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Cliente: joao / senha123')
        self.stdout.write('   ONG 1: ong_esperanca / senha123')
        self.stdout.write('   ONG 2: ong_solidaria / senha123')
