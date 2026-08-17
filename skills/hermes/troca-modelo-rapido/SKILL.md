---
name: troca-modelo-rapido
description: "Troca rapida de modelo do Hermes Agent. REGRA: modelo fixo deepseek v4 flash. So trocar com autorizacao explicita de Giovani - NUNCA em resposta a gatilhos automaticos."
version: "2.2.0"
author: Giovani
---

# Troca Rapida de Modelo

Skill para trocar o modelo do Hermes Agent.

## REGRA FUNDAMENTAL

**Modelo FIXO: `deepseek/deepseek-v4-flash` via OpenRouter. So trocar com autorizacao explicita de Giovani.**

- **NUNCA** trocar por iniciativa propria, gatilho automatico, palavra-chave ou padrao.
- **NENHUM padrao abaixo autoriza troca automaticamente.** Apenas um comando explicito do tipo "pode trocar para X" vale.
- Apos receber autorizacao verbal, confirmar de volta: \"Confirma que quer trocar de modelo?\" antes de executar — a menos que a autorizacao seja inequivoca e entusiasmada (ex: \"Vamos trocar!\" com nome do modelo). Nesse caso prossiga diretamente sem confirmacao extra.
- Se o usuario rejeitar um modelo sugerido e propor outro, isso conta como autorizacao explicita para o modelo proposto.

## Budget Awareness

- Gasto maximo diario: **R$ 0,10 (~$0,02 USD)**. Se ultrapassar, avisar imediatamente.
- Consultar gasto atual via OpenRouter API:
  ```bash
  /opt/data/venv_google/bin/python /opt/data/scripts/log_usage.py
  ```
  Saida: gasto hoje, periodo, restante de $8.00.
- Ao sugerir modelo alternativo (raro — requer autorizacao), verificar preco no OpenRouter.

## Mapeamento de Slugs (CONSULTA — so executar apos autorizacao)

| Intencao do usuario | Modelo | Slug OpenRouter |
|--------------------|--------|----------------|
| "padrao", "voltar", "flash", "V4" | DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` |
| "V3" | DeepSeek V3.2 | `deepseek/deepseek-v3.2` |
| "gratis", "free", "nemotron" | NVIDIA Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` |
| "Qwen 3.7", "Qwen Flash" | Qwen 3.7 Flash | `qwen/qwen3.7-flash` |

> ⚠️ Tabela meramente informativa — consultar apenas quando o usuario JA autorizou a troca. So o modelo padrao (flash) e permitido sem autorizacao.

## Procedimento (so executar apos autorizacao EXPLICITA)

1. Identificar o slug alvo conforme tabela
2. Executar troca:
   ```bash
   cd /opt/data && /opt/hermes/.venv/bin/hermes config set model.default <slug>
   ```
3. Verificar se `model.default` no config foi atualizado
4. Responder: `✅ <modelo> ativo.`
5. Informar que a troca so vale para nova sessao (precisa de /new ou restart do gateway)

## Caminhos

- Config: `/opt/data/config.yaml`
- Hermes CLI: `/opt/hermes/.venv/bin/hermes`
- Planilha de logs OR: `TESTE-CLEITON-123` (ID: `18KZeG6S8pODXEu580CX-UJogSLNrkjjH7DwSL18b86k`)
- Script de consulta de gasto: `/opt/data/scripts/log_usage.py`

## References

- `references/slugs.md` — tabela completa de slugs com comandos de troca e verificacao
- `references/pricing-analysis.md` — workflow para comparar precos de modelos e provedores no OpenRouter (preco, latencia, throughput, cache)

## Pitfalls

- **Nao usar `hermes model`** — requer terminal interativo. Use `hermes config set model.default`.
- **Nao esperar que a troca afete a sessao atual.** So vale apos restart do gateway ou /new.
- **Nao trocar sem autorizacao explicita.** Nenhum gatilho automatico e valido.
- **Nao sugerir trocas por conta propria.** Apenas responder a pedidos diretos.
- **Provider e sempre OpenRouter** — slugs devem seguir formato `provedor/modelo` (ex: `deepseek/deepseek-v4-flash`).
