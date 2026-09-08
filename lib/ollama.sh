#!/usr/sbin/bash

# ============================================================
# AI-PACK v2 — Ollama Interface
# ============================================================

OLLAMA_URL="http://localhost:11434/api/generate"
MODEL="qwen2.5-coder:3b"

PROJECT_ROOT="$HOME/StoneveldGithub/Whit"
OUTPUT_DIR="$PROJECT_ROOT/AI_Context_Pack/ai-pack-v2/output"

mkdir -p "$OUTPUT_DIR"

# ------------------------------------------------------------
# Validate input
# ------------------------------------------------------------

if [[ $# -lt 1 ]]; then
    echo "ERROR: No context file supplied."
    echo
    echo "Usage:"
    echo "  ollama.sh <context_file>"
    exit 1
fi

CONTEXT_FILE="$1"

if [[ ! -f "$CONTEXT_FILE" ]]; then
    echo "ERROR: Context file not found:"
    echo "$CONTEXT_FILE"
    exit 1
fi

# ------------------------------------------------------------
# Display input information
# ------------------------------------------------------------

INPUT_NAME=$(basename "$CONTEXT_FILE")
INPUT_SIZE=$(du -h "$CONTEXT_FILE" | cut -f1)

echo
echo "AI-PACK: Sending context to local AI..."
echo
echo "Model: $MODEL"
echo "Input: $INPUT_NAME"
echo "Size:  $INPUT_SIZE"
echo
# ------------------------------------------------------------
# Build prompt
# ------------------------------------------------------------

PROMPT=$(cat <<EOF
You are analysing a controlled historical software evidence package.

Rules:

1. Treat the supplied files as historical evidence.
2. Do not modify or rewrite the historical source.
3. Distinguish direct evidence from inference.
4. Identify incomplete, experimental, or uncertain components.
5. Do not invent missing information.
6. Analyse the development progression across the supplied files.

Provide a detailed structured technical analysis. Your response must be substantial and must contain these sections:

1. Executive Summary
2. Historical Development
3. Architecture
4. Core Principles
5. Evidence From The Source Files
6. What Is Actually Implemented
7. Incomplete Or Experimental Components
8. Evidence Versus Inference
9. Development Progression Across Prototypes
10. Conclusions And Open Questions

Analyse the supplied files themselves. Do not merely summarize the final program. Compare the different historical versions and explain how the system developed.
Here is the controlled evidence package:

$(cat "$CONTEXT_FILE")
EOF
)
# ------------------------------------------------------------
# Build JSON request
# ------------------------------------------------------------

REQUEST=$(python -c 'import json,sys; print(json.dumps({"model":sys.argv[1],"prompt":sys.argv[2],"stream":False}))' \
    "$MODEL" \
    "$PROMPT")
# ------------------------------------------------------------
# Send to Ollama
# ------------------------------------------------------------

RESPONSE=$(curl -s "$OLLAMA_URL" \
    -H "Content-Type: application/json" \
    -d "$REQUEST")
# ------------------------------------------------------------
# Extract AI response
# ------------------------------------------------------------

AI_RESPONSE=$(python -c '
import json
import sys

data = json.load(sys.stdin)

if "error" in data:
    print("ERROR: " + str(data["error"]))
    sys.exit(1)

response = data.get("response")

if response is None:
    print("ERROR: Ollama response field was not found.")
    sys.exit(1)

print(response)
' <<< "$RESPONSE")
# ------------------------------------------------------------
# Check AI response
# ------------------------------------------------------------

if [[ -z "$AI_RESPONSE" ]]; then
    echo "ERROR: AI returned an empty response."
    exit 1
fi
# ------------------------------------------------------------
# Save analysis
# ------------------------------------------------------------

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE="$OUTPUT_DIR/analysis_$TIMESTAMP.txt"

{
    echo "============================================================"
    echo "AI-PACK v2 — AI ANALYSIS"
    echo "============================================================"
    echo "MODEL:     $MODEL"
    echo "GENERATED: $(date)"
    echo "SOURCE:    $INPUT_NAME"
    echo "============================================================"
    echo
    echo "AI RESPONSE"
    echo "============================================================"
    echo
    echo "$AI_RESPONSE"
    echo
    echo "============================================================"
} > "$OUTPUT_FILE"

echo "AI analysis completed."
echo
echo "Saved:"
echo "$OUTPUT_FILE"
