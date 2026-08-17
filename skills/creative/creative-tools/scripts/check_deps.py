#!/usr/bin/env python3
"""
check_deps.py — Verify a ComfyUI workflow's dependencies (custom nodes, models,
embeddings) against a running server.

Improvements over v1:
  - Cloud-aware endpoint mapping (handles `/api/experiment/models/{folder}` and
    `/api/object_info` variants verified against live cloud API)
  - Distinguishes 200-empty (genuinely no models in folder) vs 404
    (folder doesn't exist) vs 403 (auth/tier issue) — no silent passes
  - Outputs concrete remediation commands (e.g. `comfy node install <name>`)
    when nodes are missing
  - Detects embedding references inside prompt strings as model deps
  - Skips check on cloud free tier `/api/object_info` (403) without false alarm
  - Accepts API key from CLI flag or $COMFY_CLOUD_API_KEY env var

Usage:
    python3 check_deps.py workflow_api.json
    python3 check_deps.py workflow_api.json --host 127.0.0.1 --port 8188
    python3 check_deps.py workflow_api.json --host https://cloud.comfy.org

Stdlib-only. Python 3.10+.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    DEFAULT_LOCAL_HOST, ENV_API_KEY,
    emit_json, folder_aliases_for, http_get, is_cloud_host,
    iter_embedding_refs, iter_model_deps, iter_nodes, parse_model_list,
    resolve_api_key, resolve_url, unwrap_workflow,
)


# Known node → custom-node-package map. When a workflow needs a node we don't
# recognize, suggesting the right `comfy node install ...` makes the difference
# between a working agent and a stuck one.
NODE_TO_PACKAGE: dict[str, str] = {
    # rgthree (Reroute is JS-only and doesn't appear in /object_info)
    \"Power Lora Loader (rgthree)\": \"rgthree-comfy\",
    \"Image Comparer (rgthree)\": \"rgthree-comfy\",
    \"Seed (rgthree)\": \"rgthree-comfy\",
    \"Display Any (rgthree)\": \"rgthree-comfy\",
    \"Display Int (rgthree)\": \"rgthree-comfy\",
    # Impact pack
    \"FaceDetailer\": \"comfyui-impact-pack\",
    \"DetailerForEach\": \"comfyui-impact-pack\",
    \"BboxDetectorSEGS\": \"comfyui-impact-pack\",
    \"SAMLoader\": \"comfyui-impact-pack\",
    \"ImpactWildcardProcessor\": \"comfyui-impact-pack\",
    # Impact subpack (separate package)
    \"UltralyticsDetectorProvider\": \"comfyui-impact-subpack\",
    # Was Node Suite
    \"Image Save\": \"was-node-suite-comfyui\",
    \"Number Counter\": \"was-node-suite-comfyui\",
    \"Text String\": \"was-node-suite-comfyui\",
    # easy-use
    \"easy fullLoader\": \"comfyui-easy-use\",
    \"easy positive\": \"comfyui-easy-use\",
    \"easy negative\": \"comfyui-easy-use\",
    \"easy seed\": \"comfyui-easy-use\",
    \"easy imageSave\": \"comfyui-easy-use\",
    # Video Helper Suite
    \"VHS_VideoCombine\": \"comfyui-videohelpersuite\",
    \"VHS_LoadVideo\": \"comfyui-videohelpersuite\",
    \"VHS_LoadAudio\": \"comfyui-videohelpersuite\",
    # AnimateDiff
    \"ADE_AnimateDiffLoaderWithContext\": \"comfyui-animatediff-evolved\",
    \"ADE_AnimateDiffLoaderGen1\": \"comfyui-animatediff-evolved\",
    \"ADE_LoadAnimateDiffModel\": \"comfyui-animatediff-evolved\",
    # ControlNet aux preprocessors (full class names)
    \"CannyEdgePreprocessor\": \"comfyui_controlnet_aux\",
    \"DWPreprocessor\": \"comfyui_controlnet_aux\",
    \"OpenposePreprocessor\": \"comfyui_controlnet_aux\",
    \"DepthAnythingPreprocessor\": \"comfyui_controlnet_aux\",
    \"Zoe_DepthAnythingPreprocessor\": \"comfyui_controlnet_aux\",
    \"AnimalPosePreprocessor\": \"comfyui_controlnet_aux\",
    # IPAdapter Plus
    \"IPAdapterAdvanced\": \"comfyui_ipadapter_plus\",
    \"IPAdapterUnifiedLoader\": \"comfyui_ipadapter_plus\",
    \"IPAdapterModelLoader\": \"comfyui_ipadapter_plus\",
    \"IPAdapterInsightFaceLoader\": \"comfyui_ipadapter_plus\",
    # InstantID
    \"InstantIDModelLoader\": \"comfyui_instantid\",
    \"ApplyInstantID\": \"comfyui_instantid\",
    # Comfy essentials (note: registry slug uses underscore, not hyphen)
    \"GetImageSize+\": \"comfyui_essentials\",
    \"ImageBatchMultiple+\": \"comfyui_essentials\",
    # pysssss
    \"ShowText|pysssss\": \"comfyui-custom-scripts\",
    \"PreviewImage|pysssss\": \"comfyui-custom-scripts\",
    # SUPIR
    \"SUPIR_Upscale\": \"comfyui-supir\",
    \"SUPIR_first_stage\": \"comfyui-supir\",
    # GGUF (case-sensitive registry slug)
    \"UNETLoaderGGUF\": \"ComfyUI-GGUF\",
    \"DualCLIPLoaderGGUF\": \"ComfyUI-GGUF\",
    # Florence2
    \"Florence2Run\": \"comfyui-florence2\",
    # WAS
    \"Image Filter Adjustments\": \"was-node-suite-comfyui\",
    # Photomaker (case-sensitive)
    \"PhotoMakerLoader\": \"ComfyUI-PhotoMaker-Plus\",
    # Wan video (case-sensitive)
    \"WanVideoSampler\": \"ComfyUI-WanVideoWrapper\",
    \"WanVideoModelLoader\": \"ComfyUI-WanVideoWrapper\",
}

# Nodes whose package isn't on the comfy registry — need git-URL install via
# ComfyUI-Manager. We surface a helpful hint instead of an unrunnable command.
NODE_TO_GIT_URL: dict[str, str] = {
    \"HunyuanVideoSampler\": \"https://github.com/kijai/ComfyUI-HunyuanVideoWrapper\",
    \"HunyuanVideoModelLoader\": \"https://github.com/kijai/ComfyUI-HunyuanVideoWrapper\",
}


def fetch_object_info(url: str, headers: dict) -> tuple[set[str] | None, dict | None]:
    \"\"\"Returns (installed_node_set, error_info). Error info is a dict if we
    couldn't query (e.g. cloud free tier), else None.
    \"\"\"\n    r = http_get(url, headers=headers, retries=2, timeout=30)\n    if r.status == 200:\n        try:\n            data = r.json()\n            if isinstance(data, dict):\n                return set(data.keys()), None\n        except Exception:\n            pass\n        return None, {\"http_status\": 200, \"reason\": \"non-dict response\"}\n    if r.status == 403:\n        try:\n            body = r.json()\n        except Exception:\n            body = {\"raw\": r.text()[:200]}\n        return None, {\"http_status\": 403, \"reason\": \"forbidden\", \"body\": body}\n    if r.status == 404:\n        return None, {\"http_status\": 404, \"reason\": \"endpoint not found\"}\n    return None, {\"http_status\": r.status, \"reason\": \"unexpected\", \"body\": r.text()[:200]}\n\n\ndef _fetch_one_folder(\n    base: str, folder: str, headers: dict, *, is_cloud: bool,\n) -> tuple[set[str] | None, dict | None]:\n    \"\"\"Single-folder fetch, no aliasing. Returns (installed_set, error_info).\"\"\"\n    url = resolve_url(base, f\"/models/{folder}\", is_cloud=is_cloud)\n    r = http_get(url, headers=headers, retries=2, timeout=30)\n    if r.status == 200:\n        try:\n            return parse_model_list(r.json()), None\n        except Exception:\n            return set(), {\"http_status\": 200, \"reason\": \"non-list response\"}\n    if r.status == 404:\n        body_text = r.text()\n        try:\n            body = r.json()\n        except Exception:\n            body = {\"raw\": body_text[:200]}\n        code = body.get(\"code\") if isinstance(body, dict) else None\n        if code == \"folder_not_found\":\n            # Folder is genuinely empty/missing on server — not the same as\n            # \"endpoint missing\". Return empty set with informational error.\n            return set(), {\"http_status\": 404, \"reason\": \"folder_empty_or_unknown\", \"body\": body}\n        return None, {\"http_status\": 404, \"reason\": \"endpoint not found\", \"body\": body}\n    if r.status == 403:\n        try:\n            body = r.json()\n        except Exception:\n            body = {}\n        return None, {\"http_status\": 403, \"reason\": \"forbidden\", \"body\": body}\n    return None, {\"http_status\": r.status, \"reason\": \"unexpected\"}\n\n\ndef fetch_models_for_folder(\n    base: str, folder: str, headers: dict, *, is_cloud: bool,\n) -> tuple[set[str] | None, dict | None]:\n    \"\"\"Fetch installed models for a folder, trying aliases.\n\n    Folder renames over time (e.g. unet → diffusion_models, clip → text_encoders)\n    mean a workflow asking for a model in `unet` may need to look in\n    `diffusion_models`. We union models from every reachable alias.\n\n    Returns (combined_set | None, last_error | None).\n    \"\"\"\n    aliases = folder_aliases_for(folder)\n    combined: set[str] = set()\n    any_success = False\n    last_err: dict | None = None\n    for alias in aliases:\n        models, err = _fetch_one_folder(base, alias, headers, is_cloud=is_cloud)\n        if models is not None:\n            combined.update(models)\n            any_success = True\n            last_err = None\n        else:\n            last_err = err\n    if not any_success:\n        return None, last_err\n    return combined, None\n\n\ndef fetch_embeddings(base: str, headers: dict, *, is_cloud: bool) -> tuple[set[str] | None, dict | None]:\n    \"\"\"Local ComfyUI exposes /embeddings; cloud uses /experiment/models/embeddings.\"\"\"\n    if is_cloud:\n        return fetch_models_for_folder(base, \"embeddings\", headers, is_cloud=True)\n    # Local: dedicated /embeddings returns a flat list of names\n    r = http_get(resolve_url(base, \"/embeddings\", is_cloud=False), headers=headers, retries=2)\n    if r.status == 200:\n        try:\n            data = r.json()\n            if isinstance(data, list):\n                # Strip extensions from the registered names since prompt syntax\n                # usually omits them (\"embedding:goodvibes\" vs \"goodvibes.pt\")\n                names = set()\n                for n in data:\n                    if isinstance(n, str):\n                        names.add(n)\n                        # Also store stem for fuzzy matching\n                        names.add(Path(n).stem)\n                return names, None\n        except Exception:\n            pass\n    return None, {\"http_status\": r.status, \"reason\": \"unexpected\"}\n\n\ndef normalize_for_match(name: str) -> set[str]:\n    \"\"\"Generate matching variants of a model name (with/without extension, slashes, etc.)\"\"\"\n    s = {name}\n    s.add(Path(name).stem)\n    s.add(Path(name).name)\n    # ComfyUI sometimes strips/keeps the leading folder\n    if \"/\" in name or \"\\\\\" in name:\n        flat = name.replace(\"\\\\\", \"/\").split(\"/\")[-1]\n        s.add(flat)\n        s.add(Path(flat).stem)\n    return {x for x in s if x}\n\n\ndef model_present(needed: str, installed: set[str]) -> bool:\n    if not installed:\n        return False\n    needed_variants = normalize_for_match(needed)\n    installed_norm: set[str] = set()\n    for inst in installed:\n        installed_norm.update(normalize_for_match(inst))\n    return bool(needed_variants & installed_norm)\n\n\ndef suggest_install_command(node_class: str) -> str | None:\n    pkg = NODE_TO_PACKAGE.get(node_class)\n    if pkg:\n        return f\"comfy node install {pkg}\"\n    return None\n\n\ndef suggest_git_url(node_class: str) -> str | None:\n    \"\"\"For nodes not on the registry, return a git URL the user can hand to\n    ComfyUI-Manager's `/manager/queue/install` endpoint.\"\"\"\n    return NODE_TO_GIT_URL.get(node_class)\n\n\ndef check_deps(\n    workflow: dict, host: str, *, api_key: str | None = None,\n) -> dict:\n    headers: dict[str, str] = {}\n    if api_key:\n        headers[\"X-API-Key\"] = api_key\n\n    is_cloud = is_cloud_host(host)\n    base = host.rstrip(\"/\")\n\n    # ---- 1. Required nodes ----\n    required_nodes: set[str] = set()\n    for _, node in iter_nodes(workflow):\n        required_nodes.add(node[\"class_type\"])\n\n    object_info_url = resolve_url(base, \"/object_info\", is_cloud=is_cloud)\n    installed_nodes, obj_err = fetch_object_info(object_info_url, headers)\n\n    missing_nodes: list[dict] = []\n    node_check_skipped = False\n    if installed_nodes is None:\n        # Couldn't query (e.g. cloud free tier). Don't false-alarm; mark skipped.\n        node_check_skipped = True\n    else:\n        for cls in sorted(required_nodes):\n            if cls not in installed_nodes:\n                entry = {\"class_type\": cls}\n                cmd = suggest_install_command(cls)\n                git_url = suggest_git_url(cls)\n                if cmd:\n                    entry[\"fix_command\"] = cmd\n                elif git_url:\n                    entry[\"fix_git_url\"] = git_url\n                    entry[\"fix_hint\"] = (\n                        f\"Not on registry. Install via Manager with this git URL: {git_url}\"\n                    )\n                else:\n                    entry[\"fix_hint\"] = (\n                        \"Search https://registry.comfy.org or \"\n                        \"use ComfyUI-Manager UI to find the package providing this node.\"\n                    )\n                missing_nodes.append(entry)\n\n    # ---- 2. Required models ----\n    model_cache: dict[str, tuple[set[str] | None, dict | None]] = {}\n    missing_models: list[dict] = []\n    folder_errors: dict[str, dict] = {}\n\n    for dep in iter_model_deps(workflow):\n        folder = dep[\"folder\"]\n        if folder not in model_cache:\n            model_cache[folder] = fetch_models_for_folder(\n                base, folder, headers, is_cloud=is_cloud,\n            )\n        installed, err = model_cache[folder]\n        if installed is None:\n            # Couldn't enumerate this folder — record once\n            folder_errors.setdefault(folder, err or {})\n            # Don't flag as missing (we don't know); the folder_errors block surfaces this\n            continue\n        if not model_present(dep[\"value\"], installed):\n            entry = dict(dep)\n            entry[\"fix_hint\"] = (\n                f\"comfy model download --url <URL> --relative-path models/{folder} \"\n                f\"--filename {dep['value']!r}\"\n            )\n            missing_models.append(entry)\n\n    # ---- 3. Embedding refs in prompts ----\n    emb_installed, emb_err = fetch_embeddings(base, headers, is_cloud=is_cloud)\n    missing_embeddings: list[dict] = []\n    seen_emb: set[tuple[str, str]] = set()\n    for nid, emb_name in iter_embedding_refs(workflow):\n        if (nid, emb_name) in seen_emb:\n            continue\n        seen_emb.add((nid, emb_name))\n        if emb_installed is None:\n            # Couldn't enumerate — skip silently here, surface the error in the\n            # folder_errors block\n            continue\n        if not model_present(emb_name, emb_installed):\n            missing_embeddings.append({\n                \"node_id\": nid,\n                \"embedding_name\": emb_name,\n                \"folder\": \"embeddings\",\n                \"fix_hint\": (\n                    f\"Download {emb_name}.pt or .safetensors and place in \"\n                    f\"models/embeddings/, or `comfy model download --url <URL> \"\n                    f\"--relative-path models/embeddings`\"\n                ),\n            })\n\n    if emb_err and emb_installed is None:\n        folder_errors.setdefault(\"embeddings\", emb_err)\n\n    is_ready = (\n        not node_check_skipped\n        and not missing_nodes\n        and not missing_models\n        and not missing_embeddings\n    )\n\n    return {\n        \"is_ready\": is_ready,\n        \"node_check_skipped\": node_check_skipped,\n        \"node_check_skip_reason\": obj_err if node_check_skipped else None,\n        \"missing_nodes\": missing_nodes,\n        \"missing_models\": missing_models,\n        \"missing_embeddings\": missing_embeddings,\n        \"folder_errors\": folder_errors,\n        # 0 is a legitimate count (e.g. empty server). Use None only when not queried.\n        \"installed_node_count\": len(installed_nodes) if installed_nodes is not None else None,\n        \"required_node_count\": len(required_nodes),\n        \"required_nodes\": sorted(required_nodes),\n        \"host\": base,\n        \"is_cloud\": is_cloud,\n    }\n\n\ndef main(argv: list[str] | None = None) -> int:\n    p = argparse.ArgumentParser(description=\"Check ComfyUI workflow dependencies against a running server\")\n    p.add_argument(\"workflow\", help=\"Path to workflow API JSON file\")\n    p.add_argument(\"--host\", default=DEFAULT_LOCAL_HOST, help=\"ComfyUI server URL\")\n    p.add_argument(\"--port\", type=int, help=\"Server port (overrides --host port)\")\n    p.add_argument(\"--api-key\", help=f\"API key for cloud (or set ${ENV_API_KEY} env var)\")\n    p.add_argument(\"--strict\", action=\"store_true\",\n                   help=\"Exit non-zero if node check is skipped (e.g. on cloud free tier)\")\n    args = p.parse_args(argv)\n\n    host = args.host\n    if args.port is not None:\n        # Strip any port from host and append --port\n        from urllib.parse import urlparse, urlunparse\n        parsed = urlparse(host if \"://\" in host else f\"http://{host}\")\n        new_netloc = f\"{parsed.hostname}:{args.port}\"\n        host = urlunparse(parsed._replace(netloc=new_netloc))\n\n    api_key = resolve_api_key(args.api_key)\n\n    wf_path = Path(args.workflow).expanduser()\n    if not wf_path.exists():\n        emit_json({\"error\": f\"Workflow file not found: {args.workflow}\"})\n        return 1\n    try:\n        with wf_path.open() as f:\n            payload = json.load(f)\n        workflow = unwrap_workflow(payload)\n    except ValueError as e:\n        emit_json({\"error\": str(e)})\n        return 1\n    except json.JSONDecodeError as e:\n        emit_json({\"error\": f\"Invalid JSON: {e}\"})\n        return 1\n\n    try:\n        result = check_deps(workflow, host=host, api_key=api_key)\n    except Exception as e:\n        emit_json({\"error\": f\"Dep check failed: {e}\", \"host\": host})\n        return 1\n\n    emit_json(result)\n\n    if not result[\"is_ready\"]:\n        return 1\n    if args.strict and result[\"node_check_skipped\"]:\n        return 1\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())