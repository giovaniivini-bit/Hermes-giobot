# OpenRouter Pricing Analysis

Workflow para comparar precos de modelos e provedores no OpenRouter.

## Quick Reference: APIs

### Listar todos os modelos com precos

```bash
curl -s "https://openrouter.ai/api/v1/models" | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = data.get('data', [])
for m in models:
    mid = m.get('id','')
    p = m.get('pricing', {})
    p_in = float(p.get('prompt', 0)) * 1_000_000
    p_out = float(p.get('completion', 0)) * 1_000_000
    p_cache = float(p.get('input_cache_read', 0)) * 1_000_000 if p.get('input_cache_read') else 0
    ctx = m.get('context_length', '?')
    name = m.get('name', mid)
    print(f'{mid:<55} | in: \${p_in:>7.4f}/M | out: \${p_out:>7.4f}/M | cache: \${p_cache:.4f}/M | ctx: {ctx}')
"
```

> **Nota:** A API retorna precos **por token**. O script acima converte para `/1M tokens` multiplicando por 1.000.000.

### Filtrar modelos por faixa de preco

```bash
# Modelos com input entre X e Y
curl -s "https://openrouter.ai/api/v1/models" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data['data']:
    p = float(m['pricing'].get('prompt', 0)) * 1_000_000
    if 0 < p < 0.09:
        print(f\"{m['id'][:55]} | in: \${p:.4f}/M\")
"
```

### Consultar saldo e gasto da chave OpenRouter

```bash
source /opt/data/venv_google/bin/activate
python3 -c "
import base64, json, urllib.request
with open('/opt/data/.or_key_b64') as f:
    key = base64.b64decode(f.read().strip()).decode()
req = urllib.request.Request('https://openrouter.ai/api/v1/auth/key',
    headers={'Authorization': f'Bearer {key}'})
d = json.loads(urllib.request.urlopen(req, timeout=15).read())['data']
print(f\"Gasto: \${d['usage']:.2f} de \${d['limit']:.2f}\")
print(f\"Disponivel: \${d['limit_remaining']:.2f}\")
print(f\"Hoje: \${d['usage_daily']:.4f}\")
"
```

## Comparacao Provedor a Provedor

Para um modelo especifico, a pagina web mostra a tabela de provedores com:
- **Input /M** e **Output /M** — preco por milhao de tokens
- **Cache read /M** — preco com cache hit
- **Latencia** (s) — tempo de resposta
- **Throughput** (tps) — tokens por segundo
- **Uptime** (%) — disponibilidade

URL: `https://openrouter.ai/<author>/<model>` (ex: `deepseek/deepseek-v4-flash`)

## Fatores de Decisao (preco + velocidade)

| Fator | O que observar |
|-------|---------------|
| Custo puro | Provedores com desconto (StreamLake -37%, Baidu -37%, GMICloud -33%) vs preco cheio |
| Velocidade | Preferir latencia < 1s e throughput > 30 tps para agentes com tool calling |
| Cache | Cache read barato é crucial para system prompts grandes e repetitivos |
| Uptime | > 99% é seguro; < 97% tem risco de queda |
| Fallback | OpenRouter roteia para outro provedor se o principal cair (so no modo Balanced) |

## Exemplo: DeepSeek V4 Flash (0423) vs Qwen 3.7 Flash

| | DeepSeek V4 Flash (Baidu) | Qwen 3.7 Flash (Alibaba) |
|---|---|---|
| Input/M | $0,088 | **$0,03** |
| Output/M | $0,176 | **$0,13** |
| Cache/M | $0,0176 | **$0,006** |
| Latencia | 0,78s | 1,06s |
| Throughput | 81 tps | 29 tps |
| Contexto | 1M | 1M |
| Provedores | Multiplos (fallback) | Unico (Alibaba) |