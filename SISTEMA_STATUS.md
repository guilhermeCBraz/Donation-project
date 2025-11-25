# 📋 Sistema de Atualização de Status das Doações

## Como o Status da Doação Muda de "Pendente"?

O sistema implementa um **fluxo completo de gerenciamento de doações** que permite às ONGs atualizar o status conforme a doação progride.

## 🔄 Fluxo de Status

```
Pendente → Confirmada → Em Trânsito → Entregue
    ↓          ↓            ↓
 Cancelada  Cancelada   (só pode ir para Entregue)
```

## 📊 Status Disponíveis

### 1. **Pendente** (Status inicial)
- Criada automaticamente quando o cliente faz a doação
- Aguardando confirmação da ONG
- ONG pode: Confirmar ✓ ou Cancelar ✗

### 2. **Confirmada**
- ONG confirmou que vai receber a doação
- Doação está sendo organizada
- ONG pode: Marcar como "Em Trânsito" 🚚 ou Cancelar ✗

### 3. **Em Trânsito**
- Doação está a caminho da ONG
- Só pode avançar para "Entregue" ✅

### 4. **Entregue** (Final)
- Doação foi recebida com sucesso
- **Importante**: Atualiza automaticamente a quantidade recebida na necessidade
- Status final - não pode ser alterado

### 5. **Cancelada** (Final)
- Doação não pôde ser realizada
- Status final - não pode ser alterado

## 🎯 Como as ONGs Atualizam o Status

### Método 1: Dashboard da ONG
1. Faça login como ONG
2. No dashboard, clique em "Gerenciar Todas as Doações"
3. Na lista de doações, selecione o novo status no dropdown
4. Clique em "Atualizar"

### Método 2: Direto no Admin
1. Acesse `/admin/`
2. Vá em "Doações"
3. Selecione a doação
4. Altere o campo "Status"
5. Salve

## ⚙️ Atualização Automática de Quantidades

Quando uma doação é marcada como **"Entregue"**:

1. O sistema automaticamente adiciona a quantidade doada à `quantidade_recebida` da necessidade
2. Atualiza o percentual de progresso
3. Exibe mensagem de sucesso com os detalhes

**Exemplo:**
```
Necessidade: Arroz - 100kg necessário, 20kg recebido
Doação entregue: 10kg
Resultado: 100kg necessário, 30kg recebido (30%)
```

## 🔐 Permissões

- **Clientes**: Apenas visualizam o status de suas doações
- **ONGs**: Podem atualizar o status das doações recebidas
- **Admin**: Pode editar qualquer doação

## 💡 Exemplo Prático

### Cenário: Cliente João doa 10kg de arroz

1. **Cliente faz a doação**
   - Status inicial: **Pendente**
   - Mensagem: "Espero que ajude!"

2. **ONG recebe notificação**
   - Acessa "Gerenciar Doações"
   - Vê doação pendente de João
   - Confirma doação → Status: **Confirmada**

3. **ONG organiza recebimento**
   - Doador leva/envia o alimento
   - ONG marca como **Em Trânsito**

4. **ONG recebe a doação**
   - Marca como **Entregue**
   - Sistema atualiza automaticamente:
     - Quantidade recebida: +10kg
     - Mensagem: "Doação marcada como entregue! Quantidade atualizada: +10.0 kg"

## 🌟 URLs do Sistema

- **Dashboard ONG**: `/dashboard/ong/`
- **Gerenciar Doações**: `/ong/gerenciar-doacoes/`
- **Atualizar Status**: `/ong/atualizar-status/<id>/` (POST)
- **Admin**: `/admin/core/doacao/`

## 🧪 Testando o Sistema

1. **Faça login como cliente** (`joao` / `senha123`)
   - Faça uma doação para alguma ONG
   - Acesse "Minhas Doações" - verá status "Pendente"

2. **Faça login como ONG** (`ong_esperanca` / `senha123`)
   - Acesse "Gerenciar Doações"
   - Veja a doação pendente
   - Atualize para "Confirmada"
   - Continue atualizando: Em Trânsito → Entregue

3. **Verifique a atualização**
   - Dashboard da ONG mostrará a quantidade atualizada
   - Cliente verá status "Entregue" em suas doações

## 📱 Interface Visual

O sistema usa **badges coloridos** para facilitar a identificação:

- 🟡 **Pendente**: Badge amarelo
- 🔵 **Confirmada**: Badge azul claro
- 🔷 **Em Trânsito**: Badge azul
- 🟢 **Entregue**: Badge verde
- 🔴 **Cancelada**: Badge vermelho

## 🔧 Código Relevante

**View de atualização** (`views.py`):
```python
@login_required
def atualizar_status_doacao(request, doacao_id):
    # Valida permissões
    # Atualiza status
    # Se entregue, atualiza quantidade_recebida
    # Exibe mensagem de confirmação
```

**URL** (`urls.py`):
```python
path('ong/atualizar-status/<int:doacao_id>/', 
     views.atualizar_status_doacao, 
     name='atualizar_status_doacao'),
```

**Template** (`gerenciar_doacoes.html`):
```html
<form method="post" action="{% url 'core:atualizar_status_doacao' doacao.id %}">
    <select name="status">
        <option value="confirmada">✓ Confirmar</option>
        <option value="em_transito">🚚 Em Trânsito</option>
        <option value="entregue">✅ Entregue</option>
        <option value="cancelada">✗ Cancelar</option>
    </select>
    <button type="submit">Atualizar</button>
</form>
```

---

**Desenvolvido para facilitar o gerenciamento de doações e manter doadores e ONGs sempre informados! 📦❤️**
