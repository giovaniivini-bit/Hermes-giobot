# OpenRouter Pricing & Balance Research

How to check current model prices and account balance on OpenRouter programmatically.
Use when the user asks "did our tokens get cheaper", "compare model costs", or wants live pricing/budget data.

## 1. Get all model prices (no auth needed)

```bash
curl -s "https://openrouter.ai/api/v1/models" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data['data']:
    mid = m['id']
    p = m.get('pricing', {})
    p_in  = float(p.get('prompt', 0))          * 1_000_000
    p_out = float(p.get('completion', 0))      * 1_000_000
    p_cache = float(p.get('input_cache_read',0)) * 1_000_000
    print(f'{mid:<50} in:\${p_in:.4f}/M out:\${p_out:.4f}/M cache:\${p_cache:.4f}/M')
"
```

### CRITICAL GOTCHA — per-token, not per-million
The `pricing` fields in this API are **per-token** decimal strings, e.g. `"prompt": "0.00000009"`.
You MUST multiply by 1,000,000 to get the per-1M-token price displayed on the site.
Raw values are `prompt` (input), `completion` (output), `input_cache_read` (cache) — all per token.
Filter by prefix to compare families, e.g. `mid.startswith('deepseek/')`, `'anthropic/claude'`, `'openai/gpt-5'`.

## 2. Get account balance / spend (requires key)

```bash
OR_KEY=$(cat /opt/data/.or_key_b64 | base64 -d)
curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OR_KEY"
```

Returns JSON `data`:
- `limit` (total credit), `limit_remaining`, `usage` (total spent), `usage_daily` (today)
- `is_free_tier` (bool)
On this user's env, key is base64 in `/opt/data/.or_key_b64`; python venv at `/opt/data/venv_google/bin/python3`.

## 3. Provider-level pricing (site UI)

The model page (`https://openrouter.ai/<author>/<model>`) shows a per-provider table
(Input/M, Output/M, Cache read/M, latency, throughput, uptime). Different providers host the
same model at different prices (e.g. DeepSeek V4 Flash: DigitalOcean $0.084/M vs official
DeepSeek $0.14/M). The default "balanced" routing picks a mix of price+speed. Cheapest provider
is not always the one used — note this when comparing "what we pay" vs "list price".

## 4. Official DeepSeek API pricing (for direct-comparison)

`https://api-docs.deepseek.com/quick_start/pricing` — official first-party prices, which can be
cheaper than OpenRouter (esp. cache-hit input). Fields: input cache-hit, input cache-miss, output.
Sample (V4 Flash): cache-hit $0.0028/M, cache-miss $0.14/M, output $0.28/M — cache-hit is ~30-50x
cheaper than OpenRouter's equivalent. Trading away OpenRouter's multi-provider routing for direct
API is the lever when trying to cut cost further.

## Pitfalls
- Article prices (e.g. "$0.03/1M vs $3.15/1M") are often illustrative averages or cache-hit prices — always verify against the live API before quoting.
- The newest model revision is not always cheaper than the prior one (V4 Flash 0423 $0.084/M vs 0731 $0.09/M). Check the current model we actually run, not just the latest listing.