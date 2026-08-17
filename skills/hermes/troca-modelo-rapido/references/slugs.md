# Model Slugs

| Variante | Modelo | Slug OpenRouter |
|----------|--------|----------------|
| flash | DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` |
| V3 | DeepSeek V3.2 | `deepseek/deepseek-v3.2` |
| free | NVIDIA Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` |
| qwen flash, Qwen3.7 | Qwen 3.7 Flash | `qwen/qwen3.7-flash` |

## Comando de troca

```bash
cd /opt/data && /opt/hermes/.venv/bin/hermes config set model.default <slug>
```

## Verificação

Linha 3 de `/opt/data/config.yaml` deve conter o slug desejado:

```
model:
  provider: openrouter
  default: <slug>
```

## Nota sobre restart

A troca só vale para **novas sessões**. Aplicar na atual:
- Telegram: `/new` inicia nova sessão
- Gateway: `hermes gateway restart` (via terminal externo, não de dentro do gateway)
- CLI: sair e abrir nova sessão
