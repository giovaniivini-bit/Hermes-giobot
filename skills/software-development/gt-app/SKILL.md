---
name: gt-app
title: GT App - Central de Pendencias (Confeccoes Oneda)
description: "Skill especializada no ecossistema GT App da Confeccoes Oneda - sistema de gestao de pendencias + 3 planilhas Google vinculadas (Aviamentos, Cores, Rotativos). Dominio completo: navegacao, tarefas, dashboard, cadastro, consulta a planilhas, KPIs e fluxos. Regra #1: NUNCA alterar tarefas sem permissao."
---

# GT App - Central de Pendencias

## ⚠️ REGRA FUNDAMENTAL (NUNCA VIOLAR)

**🚫 NUNCA modifique, crie, edite, exclua, marque/desmarque tarefas ou pendências sem permissão explícita do usuário (Giovani).**

### REGRA 1 — Orçamento Diário
- **Gasto máximo: R$ 0,10 centavos por dia** (~$0,019 USD)
- Monitorar via cron OpenRouter (12h e 18h BRT)
- Se ultrapassar R$ 0,10 no dia, **avisar Giovani imediatamente**
- Conversão de referência: R$ 0,10 ≈ $0,02 USD (aproximado)

### REGRA 2 — Modelo Fixo
- **Modelo único: `deepseek/deepseek-v4-flash`** via OpenRouter
- **Provedor: OpenRouter** (depósito de $10)
- Só trocar de modelo com **autorização explícita** de Giovani
- Gatilho de troca: usar script/skill `troca-modelo-rapido`

### Demais regras
- Ações **read-only** (listar, visualizar, expandir cards) são sempre OK.
- Qualquer ação de escrita exige confirmação ANTES de executar.
- Exceção: se o usuário PEDIR expressamente para criar/editar/excluir algo, execute e confirme o resultado.

### EXIGÊNCIA DE PRECISÃO ABSOLUTA

Dados de trabalho da Confecções Oneda — **erros NÃO são tolerados.** O usuário corrige duramente qualquer imprecisão.

**Protocolo de Precisão (obrigatório antes de reportar qualquer dado):**

1. **Verificação visual** — Usar `browser_vision` para confirmar números visíveis na tela. O snapshot textual do navegador frequentemente distorce contadores (mostra "0" quando há números reais).
2. **Atribuição correta** — Expandir o card certo e confirmar o nome no heading antes de reportar tarefas. Já houve erro de atribuir tarefas da Ketlyn ao Giovani.
3. **Datas em planilhas** — Validar índices de colunas manualmente (conferir header row). Tratar formato BR (dd/mm/aaaa) e typos comuns (19/062026, 20262026). Ignorar valores lixo ('33007', '#VALUE!').
4. **Ambiguidade** — Quando em dúvida sobre associação de dados, perguntar antes de assumir.
5. **Pós-ação** — Toda operação de escrita deve ser verificada: modal fechou? mensagem de sucesso apareceu? contador/lista reflete a mudança?

> 🔍 Antes de qualquer consulta a planilhas, carregar `skill_view("gt-app", file_path="references/spreadsheets.md")` para verificar as colunas exatas de cada aba — isso elimina erros de índice.

---

## 1. INFORMACOES GERAIS

| Item | Valor |
|------|-------|
| **URL** | `https://tasks.136-248-111-213.sslip.io/` |
| **Nome** | GT App - Central de Pendencias |
| **Empresa** | Confeccoes Oneda |
| **Tema** | Dark mode (fundo escuro) |
| **Data** | Exibe dia da semana + data no header |

---

## 2. NAVEGACAO PRINCIPAL

| Aba | Tipo | Destino |
|-----|------|---------|
| **Pendencias** | Botao | View principal - lista de usuarios/grupos com tarefas |
| **Dashboard** | Botao | KPIs, cards de usuarios com progresso |
| **Aviamentos** | Link | Google Sheets externo (requer auth) |
| **Cores** | Link | Google Sheets externo (requer auth) |
| **Rotativos** | Link | Google Sheets externo (requer auth) |
| **Calendário** | Botao | View de calendário com pendencias por data |

**No header:**
- **Celular**: Abre painel com QR Code + URL para acesso mobile
- **Cadastrar Usuario**: Abre modal de cadastro

---

## 3. PENDENCIAS - VIEW PRINCIPAL

### 3.1 Filtros e Busca
- Campo de busca: "Pesquisar pendencias..."
- Filtros: Todas | Pendentes | Concluidas

### 3.2 Cards de Usuarios/Grupos (ref. 30/07/2026)

| Card | Heading | Pendencias |
|------|---------|------------|
| Ketlyn | heading Ketlyn | 6 |
| Ariel | heading Ariel | 5 |
| Giovani | heading Giovani | 26 |
| Joyce | heading Joyce | 8 |
| REUNIAO CUSTOS | heading REUNIAO CUSTOS | 13 |
| B31 - entrega dia 31/07 | heading B31 | 7 |
| Nathi (Nathalia) | heading Nathi | 7 |
| B32 - entrega 07/08 | heading B32 | 12 |
| Thami | heading Thami | 7 |
| Agenda de Tarefas | heading Agenda de Tarefas | — |

### 3.3 Elementos de Cada Card (colapsado)
- Heading clicavel: Expande/recolhe a lista de tarefas
- Botao envelope: Enviar mensagem
- Botao "+": Adicionar nova pendencia
- Contador numerico: Total de pendencias
- Icone lixeira: Excluir

### 3.4 Estrutura de Cada Tarefa (quando expandido)
- Checkbox (marcar como concluida)
- Classificacao: Urgente | Semanal | Mensal | Limpar Classificacao
- Acoes: Editar | Excluir | Anexar imagem | Compartilhar
- Descricao da tarefa (texto)
- Observacoes: campo "Adicionar observacoes..." (textarea)
- Timer | Confirmar

---

## 4. CRIAR NOVA PENDENCIA

### Fluxo:
1. Navegar para Pendencias
2. Clicar no botao "+" do usuario desejado
3. Modal "Nova Pendencia ( {Nome} )" aparece

### Campos do Modal:
- **Descricao da Pendencia** - input text (id="task-text"), placeholder "O que precisa ser feito?"
- **Observacao** - textarea, placeholder "Algum detalhe relevante..."
- **Classificacao** - dropdown: Nenhuma / Urgente / Semanal / Mensal

### Botoes: Cancelar (cinza) | Adicionar (azul, `.btn.btn-submit`)

### Tecnica de Interacao (funciona comprovadamente):
```javascript
// Preencher descricao (disparar eventos do SPA)
var input = document.getElementById('task-text');
var nativeSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeSetter.call(input, 'texto da tarefa');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));

// Submeter formulario
var form = input.closest('form');
form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
```

### Verificacao de Sucesso:
- Modal fecha
- Mensagem verde "Pendencia adicionada com sucesso!"
- Card do usuario incrementa o contador
- Expandir card mostra nova tarefa no topo da lista

---

## 5. DASHBOARD

### KPIs (linha superior):
- **TOTAL PENDENTES** - Soma geral (ex: 74)
- **ITENS URGENTES** - Total de itens Urgentes (ex: 13)
- **MAIS CARREGADO** - Pessoa com mais pendencias (ex: Giovani (17))

### Grid de Cards (3x3):
Cada card: foto, nome, e-mail, total pendencias, barra de progresso, breakdown por Urgente/Semanal/Mensal/Comum.

---

## 6. CADASTRAR USUARIO

Botao "Cadastrar Usuario" no header - Modal com campos **Nome** e **E-mail** - Botoes Cancelar | Cadastrar.

---

## 7. CELULAR (ACESSO MOBILE)

Botao "Celular" - Painel com QR Code + URL `https://vast-pots-matter.loca.lt` + instrucao de Wi-Fi.

---

## 8. BROWSER QUIRKS & TROUBLESHOOTING

| Problema | Solucao |
|----------|---------|
| Snapshot retorna "(empty page)" | Re-navegar: `browser_navigate(url)` |
| Elementos do modal nao aparecem no snapshot | Usar `browser_console` + DOM + `browser_vision` |
| `.click()` via JS nao funciona no Adicionar | Usar `form.dispatchEvent(new Event('submit'))` |
| Input value muda mas nao persiste | Usar native value setter + disparar `input`/`change` events |
| Snapshot mostra "0" mas visao mostra numeros reais | Confiar em `browser_vision` para contagens |
| `browser_vision` falha: sem provedor configurado | Usar fallback via workflow abaixo (secao 10) |
| Pagina fica em branco apos navegacao | Re-navegar para URL principal |
| Ref IDs mudam entre sessoes | Sempre pegar snapshot mais recente |

---

## 9. QUERY PATTERNS TESTADOS

### 9.1 Cross-sheet report (consultar multiplas planilhas de uma vez)
Quando o usuario pede dados de **aviamentos + cores + rotativos** simultaneamente, consultar as 3 planilhas em paralelo via `delegate_task` ou loop unico:

```python
SHEETS = {
    "Aviamentos": {"id": "1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc", "range": "PENDENTES!A1:L", "prev_col": 8, "prod_col": 5},
    "Cores (ESTILO)": {"id": "1j7k8WWvE9m4YZrw7qadANIcx_XtOzAlwYfWnm0AC5sA", "range": "ESTILO!A1:O", "prev_col": 9, "prod_col": 4},
    "Rotativos": {"id": "1uQGFBQjMI4Gnyq8eIMxRqFArmr00bEazGQVrHRD9vlY", "range": "PENDENTES!A1:K", "prev_col": 6, "prod_col": 0},
}
```

### 9.2 Cores em atraso (ESTILO — PREVISÃO < hoje, não recebidas)
```python
from datetime import date, datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
svc = build('sheets', 'v4', credentials=creds)

TODAY = date(2026, 7, 8)  # atualizar

def pars(s):
    if not s or str(s).strip() in ("-","","N/A","#VALUE!"): return None
    s = str(s).strip().replace("20262026","2026")
    try: return datetime.strptime(s, "%d/%m/%Y").date()
    except: return None

# ESTILO (ID das cores)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1j7k8WWvE9m4YZrw7qadANIcx_XtOzAlwYfWnm0AC5sA",
    range="ESTILO!A1:O"
).execute().get("values", [])
# Col: 0=TINT,1=RESP,2=COLEC,3=SIT,4=PANT,5=COR,9=PREV,12=REC,13=ENV,14=OBS

for row in rows[1:]:
    if not row or len(row) < 10: continue
    prev = pars(row[9])
    if not prev or prev >= TODAY: continue
    rec, env = pars(row[12]), pars(row[13])
    obs = row[14] if len(row)>14 else ""
    if rec or env or "RECEBIDO" in obs.upper(): continue
    print(f"{row[1]} | {row[5]} | atraso {(TODAY-prev).days}d")
```

### 9.3 Previstos para amanhã / esta semana
```python
target = date(2026, 7, 9)  # data alvo
start, end = date(2026, 7, 6), date(2026, 7, 10)  # range semana

# CORES (ESTILO, col 9 = PREVISÃO)
rows = svc.spreadsheets().values().get(...).execute().get("values",[])
for row in rows[1:]:
    prev = pars(row[9]) if len(row)>9 else None
    if prev == target:  # ou start <= prev <= end
        print(f"{row[1]} | {row[5]} | Pantone {row[4]} | Prev: {prev}")

# AVIAMENTOS (PENDENTES, col 8 = PREVISÃO)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc",
    range="PENDENTES!A1:L"
).execute().get("values", [])
for row in rows[1:]:
    prev = pars(row[8]) if len(row)>8 else None
    if prev and start <= prev <= end:
        print(f"{row[0]:<10s} | Prod {row[5]:<20s} | {row[3]:<20s} | Prev: {prev}")

# ROTATIVOS (PENDENTES, col 6 = PREV. MESA)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1uQGFBQjMI4Gnyq8eIMxRqFArmr00bEazGQVrHRD9vlY",
    range="PENDENTES!A1:K"
).execute().get("values", [])
for row in rows[1:]:
    prev = pars(row[6]) if len(row)>6 else None
    if prev == target:
        print(f"{row[0]} | FID {row[2]} | Prev mesa: {prev}")
```

---

## 10. FLUXOS PRÁTICOS

### Listar pendencias de um usuario
```markdown
browser_click(ref do heading do usuario) - expandir card
browser_vision(question='Quais tarefas estao visiveis?') - ler tarefas
```

### Listar TODAS as pendências de todos os usuarios (metodo correto)

⚠️ **PITFALL CRITICO**: Nunca leia `document.body.innerText` na view "Todas" (sem filtro) e tente correlacionar linhas com checkbox state. A abordagem quebra porque multi-linhas, botoes e labels se misturam no texto. Isso gera listas com tarefas CONCLUÍDAS erradas junto com as pendentes — o usuario corrige duramente.

**Workflow correto (3 passos):**

1. **Clicar no filtro "Pendentes"** primeiro para mostrar SÓ itens nao marcados:
```javascript
// No snapshot do browser, clicar no botao "Pendentes" (ex: ref=e13)
browser_click(e13)
```

2. **Ler `body.innerText` AGORA** — so contem tarefas pendentes (limpo):
```javascript
document.body.innerText.split('\n').map(l=>l.trim()).filter(l=>l&&l.length>2)
```
Parso manualmente: procura nomes de usuario conhecidos → próxima linha é contador → seguido de linhas de tarefas até proximo usuario.
Usuarios conhecidos: Ketlyn, Ariel, Giovani, Joyce, REUNIÃO CUSTOS, Nathi, Thami, Camilla.

3. **Verificar contagens via DOM** para garantir precisão absoluta:
```javascript
var unameList = ['Ketlyn','Ariel','Giovani','Joyce','REUNIÃO CUSTOS','Nathi','Thami','Camilla'];
var h2s = document.querySelectorAll('h2');
var out = {};
unameList.forEach(function(u) {
  var tgtH2 = null;
  for (var i = 0; i < h2s.length; i++) {
    if (h2s[i].textContent.trim() === u) { tgtH2 = h2s[i]; break; }
  }
  if (!tgtH2) { out[u] = 'NOT_FOUND'; return; }
  var section = tgtH2.closest('.list-column');
  if (!section) { out[u] = 'NO_SECTION'; return; }
  var cbs = section.querySelectorAll('input[type="checkbox"]');
  var chk = 0; for (var j = 0; j < cbs.length; j++) { if (!cbs[j].checked) chk++; }
  out[u] = {pending: chk, total: cbs.length};
});
JSON.stringify(out)
```
Cada `<section class="list-column ...">` por usuario tem todos os checkboxes. Count unchecked dá o numero exato. Compare com a listagem do passo 2 — devem bater.

### Extrair observações de cada tarefa pendente
Após listar tarefas com body.innerText, as observações aparecem como linhas separadas abaixo de cada descrição. Estrutura típica:
```
Descricao da tarefa ...\nObservação relevante ...\nNomeDoProximoUsuario\n```
Para mapear corretamente: cada linha após uma descricao (e antes do proximo nome de usuario) é observação daquela tarefa. Pule conteudos como "Adicionar observações..." (placeholder vazio).

### Criar pendencia
```
browser_click(ref do + do usuario) - modal
browser_console(expression='...native setter...') - preencher
browser_console(expression='form.submit()') - salvar
browser_vision - confirmar
```

### Ver Dashboard
```
browser_click(ref do Dashboard) - KPIs + grid
```

---

## 11. REFERENCIAS

Para dados detalhados de cada planilha (colunas, amostras de dados, estrutura completa):
`skill_view("gt-app", file_path="references/spreadsheets.md")`

---

## 12. PLANILHAS GOOGLE VINCULADAS

O GT App linka 3 Google Sheets que sao **parte integrante do sistema**.

### Credenciais de Acesso
- Token: `/opt/data/google_token.json`
- Venv: `/opt/data/venv_google/`
- API: Google Sheets v4

### 1. PENDENCIA AVIAMENTOS
| Item | Dado |
|------|------|
| **ID** | `1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc` |
| **Abas** | PENDENTES (12 ativos), RESOLVIDOS (183), Tab. Dinamica, Detalhe1-HI |
| **Responsaveis** | ANA, NATHALIA, JOYCE |
| **Fornecedores-chave** | AL (25%), LINEAR (22%), HI (10%) |
| **Live** | Botoes Hering Inverno 27 (BRASIL BOTOES), Cadarcos Summer II (AL), Etiquetas (QUALITA, HI) |

### 2. PENDENCIA DE CORES - TINTURARIA
| Item | Dado |
|------|------|
| **ID** | `1j7k8WWvE9m4YZrw7qadANIcx_XtOzAlwYfWnm0AC5sA` |
| **Abas** | ESTILO (50), CORES APROVADAS (94), PPCP (146), Tab. Dinamica, Atrasos |
| **Pendentes por responsavel** | ANA (17), C&A (1), NATHALIA (1) - Total 19 |
| **Atrasos** | **ANA** - 9 cores em atraso |
| **Clientes** | Centauro, Hering (Inverno 27), C&A (Summer II), ASICS SS27 |

### 3. PENDENCIA ROTATIVOS
| Item | Dado |
|------|------|
| **ID** | `1uQGFBQjMI4Gnyq8eIMxRqFArmr00bEazGQVrHRD9vlY` |
| **Abas** | PENDENTES (10 ativos), RESOLVIDOS (20) |
| **Live** | 10 cilindros em aberto (Hering/Lancaster), previsoes ate 16/07 |

### Exemplo de consulta padrao
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
service = build('sheets', 'v4', credentials=creds)

data = service.spreadsheets().values().get(
    spreadsheetId='1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc',
    range='PENDENTES!A1:L'
).execute()
```

---

## 13. USUARIOS CADASTRADOS (ref. 30/07/2026)

| Nome | E-mail | Pendencias |
|------|--------|------------|
| Ketlyn | ketlyn@confeccoesoneda.com.br | 6 |
| Ariel | ariel@confeccoesoneda.com.br | 5 |
| Giovani | giovani@confeccoesoneda.com.br | 26 |
| Joyce | joyce@confeccoesoneda.com.br | 8 |
| REUNIAO CUSTOS | giovani@confeccoesoneda.com.br | 13 |
| B31 - entrega dia 31/07 | giovani@confeccoesoneda.com.br | 7 |
| Nathi (Nathalia) | provavelmente nathi@confeccoesoneda.com.br | 7 |
| B32 - entrega 07/08 | giovani@confeccoesoneda.com.br | 12 |
| Thami | provavelmente thami@confeccoesoneda.com.br | 7 |