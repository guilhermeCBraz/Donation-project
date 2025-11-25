from django.core.management.base import BaseCommand
from core.models import User, ONG, Alimento, Doacao


class Command(BaseCommand):
    help = 'Cria doações de exemplo para testar o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando doações de exemplo...')
        
        try:
            # Buscar cliente
            cliente = User.objects.get(username='joao')
            
            # Buscar ONGs
            ong1 = ONG.objects.get(nome='ONG Esperança')
            ong2 = ONG.objects.get(nome='Instituto Solidariedade')
            
            # Buscar alimentos
            arroz = Alimento.objects.get(nome='Arroz')
            feijao = Alimento.objects.get(nome='Feijão')
            macarrao = Alimento.objects.get(nome='Macarrão')
            leite = Alimento.objects.get(nome='Leite')
            
            # Criar doações com diferentes status
            doacoes = [
                {
                    'doador': cliente,
                    'ong': ong1,
                    'alimento': arroz,
                    'quantidade': 10,
                    'status': 'pendente',
                    'mensagem': 'Espero que ajude! Deus abençoe o trabalho de vocês.'
                },
                {
                    'doador': cliente,
                    'ong': ong1,
                    'alimento': feijao,
                    'quantidade': 5,
                    'status': 'confirmada',
                    'mensagem': 'Doação confirmada pela ONG, aguardando entrega.'
                },
                {
                    'doador': cliente,
                    'ong': ong2,
                    'alimento': macarrao,
                    'quantidade': 8,
                    'status': 'em_transito',
                    'mensagem': 'Doação a caminho!'
                },
                {
                    'doador': cliente,
                    'ong': ong2,
                    'alimento': leite,
                    'quantidade': 12,
                    'status': 'pendente',
                    'mensagem': ''
                },
            ]
            
            for dados in doacoes:
                doacao, created = Doacao.objects.get_or_create(
                    doador=dados['doador'],
                    ong=dados['ong'],
                    alimento=dados['alimento'],
                    defaults={
                        'quantidade': dados['quantidade'],
                        'status': dados['status'],
                        'mensagem': dados['mensagem']
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Doação criada: {dados['alimento'].nome} → {dados['ong'].nome} ({dados['status']})"
                        )
                    )
            
            self.stdout.write(self.style.SUCCESS('\n✅ Doações de exemplo criadas com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {str(e)}'))
