from django.core.management.base import BaseCommand
from core.models import Doacao, NecessidadeAlimento, ONG, Alimento
import random


class Command(BaseCommand):
    help = 'Reinicia o banco de doações e necessidades'

    def handle(self, *args, **kwargs):
        # Limpar
        Doacao.objects.all().delete()
        NecessidadeAlimento.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ Banco limpo!'))
        
        # Criar necessidades
        ongs = ONG.objects.all()
        alimentos = list(Alimento.objects.all())
        
        if not ongs.exists():
            self.stdout.write(self.style.ERROR('❌ Nenhuma ONG cadastrada!'))
            return
        
        if not alimentos:
            self.stdout.write(self.style.ERROR('❌ Nenhum alimento cadastrado!'))
            return
        
        for ong in ongs:
            # Selecionar 5 alimentos aleatórios para cada ONG
            alimentos_selecionados = random.sample(alimentos, min(5, len(alimentos)))
            for alimento in alimentos_selecionados:
                NecessidadeAlimento.objects.create(
                    ong=ong,
                    alimento=alimento,
                    quantidade_necessaria=round(random.uniform(10, 100), 2),
                    prioridade=random.choice(['baixa', 'media', 'alta']),
                    observacoes=f'Necessidade de {alimento.nome} para {ong.nome}',
                    ativa=True
                )
        
        total_necessidades = NecessidadeAlimento.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✅ Criadas {total_necessidades} necessidades'))
        self.stdout.write(self.style.SUCCESS(f'✅ {ongs.count()} ONGs com necessidades cadastradas'))
