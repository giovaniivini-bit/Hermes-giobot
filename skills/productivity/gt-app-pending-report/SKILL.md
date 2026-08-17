---
name: gt-app-pending-report
title: GT App - Relatório de Pendências por Email
description: "Gera relatório HTML formatado das pendências em aberto no GT App e envia por email via Gmail. Filtro 'Pendentes' garantido — só itens não marcados."
version: 1.0.0
author: Giovani / Hermes Agent
---

# GT App - Relatório de Pendências por Email

## ⚠️ REGRAS

- **NUNCA** altere tarefas sem permissão explícita (regra da skill `gt-app`).
- Sempre filtrar **"Pendentes"** antes de extrair dados.
- Modelo padrão: `deepseek/deepseek-v4-flash` via OpenRouter (trocar só com autorização).
- Gasto máximo: R$ 0,10/dia.

---

## FLUXO COMPLETO

### Passo 1 — Abrir GT App

```
browser_navigate("https://tasks.136-248-111-213.sslip.io/")
```

### Passo 2 — Filtrar por PENDENTES

```
browser_click(ref do botão "Pendentes")
```

> O snapshot mostra os ref IDs. Botão "Pendentes" geralmente é `@e13` ou próximo a "Todas" e "Concluídas".
> Confirme visualmente clicando para ver o contador atualizado.

### Passo 3 — Expandir todos os cards

Todos os cards começam colapsados. Precisa expandir cada um:

```python
# Após clicar em "Pendentes", fazer snapshot para achar os headings
# Cada heading H2 é clicável — expande o card
for each user heading in snapshot:
    browser_click(ref_do_heading)
    # Pequena pausa natural (a SPA trata)
```

Ou alternativa mais rápida via JS:

```javascript
// Expandir todos os cards de uma vez
var h2s = document.querySelectorAll('h2');
for (var i = 0; i < h2s.length; i++) {
  var section = h2s[i].closest('.list-column');
  if (section) section.classList.remove('collapsed');
}
```

### Passo 4 — Extrair texto das tarefas pendentes

```javascript
// Extrair TODO o texto visível (já filtra automaticamente pelo filtro "Pendentes")
document.body.innerText
```

Em seguida, parsear por usuário. Padrão de estrutura do texto:

```
[NOME_USUARIO]
[Contador numérico]
[Tarefa 1]
[Tarefa 2]
...
[NOME_PRÓXIMO_USUÁRIO]
```

Filtros ao parsear:
- Pular linhas vazias e contadores isolados (`/^\d+$/`)
- Pular "Nenhuma pendência encontrada."
- Manter linha exata como aparece na tela (tags URGENTE ficam grudadas: `URGENTETexto...`)

### Passo 5 — Validar contadores via DOM (precisão obrigatória)

Antes de enviar, confirmar que os números batem:

```javascript
// Validar contagem REAL de unchecked boxes por usuário
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
  var chked = 0, unchkd = 0;
  for (var ci = 0; ci < cbs.length; ci++) {
    if (cbs[ci].checked) chked++; else unchkd++;
  }
  out[u] = {total: cbs.length, checked: chked, pending: unchkd};
});
JSON.stringify(out);
```

> **Protocolo de precisão:** Se `pending_count != items_extraídos`, revisar o parse. Erro comum: misturar concluídas com pendentes.

### Passo 6 — Gerar HTML do email

Montar HTML com a estrutura abaixo. Salvar como `/tmp/gtapp_report.html`.

Estrutura obrigatória do HTML:
- `<h1>` com título + data atual (extrair de `document.querySelector('header')` ou passar hardcoded)
- `<p>` com total geral
- Uma `<div class="user-section">` por usuário com:
  - `<h2>` nome + contador + badge urgente se aplicar
  - Lista `<ul><li>` com cada tarefa pendente
  - Itens URGENTE marcados com classe `urgent`
  - Observações em `<span class="obs">` itálico cinza
- `<div class="footer">` com crédito ao GT App

Template base salvo em referência. Customizar por usuário.

### Passo 7 — Enviar via Gmail

Verificar auth primeiro:

```bash
source /opt/data/venv_google/bin/activate
python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check
```

Se `AUTHENTICATED`, enviar:

```bash
source /opt/data/venv_google/bin/activate
cd /opt/data/skills/productivity/google-workspace/scripts
python -c "
import subprocess, sys
with open('/tmp/gtapp_report.html', 'r') as f:
    html = f.read()
cmd = [sys.executable, 'google_api.py', 'gmail', 'send',
       '--to', DESTINATARIO,
       '--subject', ASSUNTO,
       '--body', html, '--html']
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
"
```

- `DESTINATARIO`: ex `"Giovani@confeccoesoneda.com.br"`
- `ASSUNTO`: formato `"📋 Relatório de Pendências — GT App (DD/MM/AAAA)"`

### Passo 8 — Confirmar sucesso

Verificar no stdout o JSON de resposta:
- `"status": "sent"` → ✅ OK, conterá `id` e `threadId`
- Se erro, ler stderr e corrigir (geralmente auth ou scope insuficiente)

---

## USUÁRIOS CADASTRADOS (ordem no GT App)

| Usuário | Email (provável) |
|---------|-----------------|
| Ketlyn | ketlyn@confeccoesoneda.com.br |
| Ariel | ariel@confeccoesoneda.com.br |
| Giovani | giovani@confeccoesoneda.com.br |
| Joyce | joyce@confeccoesoneda.com.br |
| REUNIÃO CUSTOS | giovani@confeccoesoneda.com.br |
| Nathi | nathi@confeccoesoneda.com.br |
| Thami | thami@confeccoesoneda.com.br |
| Camilla | (email provável) |

---

## DICA: Data dinâmica

Para pegar a data atual formatada BR:

```javascript
// No browser console:
document.querySelectorAll('header .date, banner > span')[0]?.textContent?.trim() || new Date().toLocaleDateString('pt-BR', {weekday:'long', day:'numeric', month:'long', year:'numeric'})
```

Ou hardcoded: `new Date().toLocaleDateString('pt-BR', ...)`
