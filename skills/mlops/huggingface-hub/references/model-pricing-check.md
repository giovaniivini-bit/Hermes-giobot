# Model Access & Pricing Check — OpenRouter Workflow

Condensed from the former `model-access-pricing-check` skill.

## OpenRouter Lookup

1. Navigate to `https://openrouter.ai/models`
2. Use the search box (ref=e25) to enter the model identifier
3. Press Enter
4. In the results, locate the model entry and extract:
   - Model ID (shown as e.g. `Z.ai: GLM 5.2`)
   - Pricing line: `$input / $output` per 1M tokens
5. If no result appears, the model is not available on OpenRouter

## Provider Site Check (optional)

Navigate to the provider's homepage (e.g., `https://z.ai` for Z.AI models).
Look for a `/pricing` page. Check for free tier, trial, or subscription.

## Determine Cost

- If pricing shows `$0.00` for both input and output → free
- Otherwise → record the USD per 1M tokens
- If provider site indicates a paid plan required → confirm cost

## Output Format

Return a concise sentence:
- `Model <ID> is available on OpenRouter: $<input>/1M in, $<output>/1M out.`
- If not on OpenRouter: `Model <ID> not found on OpenRouter.`
- Add provider info if relevant: `Provider <site> offers <free/paid> access.`

## Pitfalls

- The OpenRouter search may show similar names; verify the exact model ID.
- Some providers hide pricing behind login; look for "Sign up for free" or "Buy Now".
- Prices may change; treat as approximate.
