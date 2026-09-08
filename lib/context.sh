#!/usr/sbin/bash

# ============================================================
# AI-PACK v2 — Context Builder
# ============================================================

PROJECT_ROOT="$HOME/StoneveldGithub/Whit"

MANIFEST="$PROJECT_ROOT/AI_Context_Pack/ai-pack-v2/manifests/cause_kernel_prototype4.manifest"

OUTPUT_DIR="$PROJECT_ROOT/AI_Context_Pack/ai-pack-v2/output"

mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

OUTPUT_FILE="$OUTPUT_DIR/context_$TIMESTAMP.txt"

# ------------------------------------------------------------
# Validate manifest
# ------------------------------------------------------------

if [[ ! -f "$MANIFEST" ]]; then
    echo "ERROR: Manifest not found:"
    echo "$MANIFEST"
    exit 1
fi

# ------------------------------------------------------------
# Create package header
# ------------------------------------------------------------

{
    echo "============================================================"
    echo "AI-PACK v2 CONTROLLED CONTEXT PACKAGE"
    echo "============================================================"
    echo "Generated: $(date)"
    echo "Project:   $PROJECT_ROOT"
    echo "Manifest:  $MANIFEST"
    echo "============================================================"
    echo
} > "$OUTPUT_FILE"

# ------------------------------------------------------------
# Add manifest information
# ------------------------------------------------------------

{
    echo "==================== MANIFEST ==============================="
    echo
    cat "$MANIFEST"
    echo
    echo "==================== SOURCE FILES ==========================="
} >> "$OUTPUT_FILE"

# ------------------------------------------------------------
# Process each FILE entry
# ------------------------------------------------------------

while IFS= read -r LINE
do

    # Ignore everything that isn't a FILE entry
    [[ "$LINE" != FILE_*=* ]] && continue

    RELATIVE_PATH="${LINE#*=}"

    FULL_PATH="$PROJECT_ROOT/$RELATIVE_PATH"

    # --------------------------------------------------------
    # Verify source file exists
    # --------------------------------------------------------

    if [[ ! -f "$FULL_PATH" ]]; then

        echo "ERROR: Source file not found:"
        echo "$RELATIVE_PATH"

        {
            echo
            echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            echo "MISSING FILE: $RELATIVE_PATH"
            echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        } >> "$OUTPUT_FILE"

        continue
    fi

    # --------------------------------------------------------
    # Add source file to package
    # --------------------------------------------------------

    {
        echo
        echo "============================================================"
        echo "FILE: $RELATIVE_PATH"
        echo "============================================================"
        echo
        cat "$FULL_PATH"
        echo
    } >> "$OUTPUT_FILE"

done < "$MANIFEST"

# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

echo
echo "Context package created:"
echo "$OUTPUT_FILE"
