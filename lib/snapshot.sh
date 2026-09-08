#!/usr/sbin/bash

# ============================================================
# AI-PACK v2 — Snapshot Engine
# ============================================================

# The project we want to snapshot
PROJECT_ROOT="$HOME/StoneveldGithub/Whit"

# Where snapshots will be stored
OUTPUT_DIR="$HOME/StoneveldGithub/Whit/AI_Context_Pack/ai-pack-v2/output"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Create a timestamp for this snapshot
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Final snapshot filename
OUTPUT_FILE="$OUTPUT_DIR/snapshot_$TIMESTAMP.txt"

# Create the snapshot header
{
    echo "============================================================"
    echo "AI-PACK v2 PROJECT SNAPSHOT"
    echo "============================================================"
    echo "Generated: $(date)"
    echo "Project: $PROJECT_ROOT"
    echo "============================================================"
} > "$OUTPUT_FILE"

echo "Snapshot created:"
echo "$OUTPUT_FILE"
#!/usr/sbin/bash

# ============================================================
# AI-PACK v2 — Snapshot Engine
# ============================================================

PROJECT_ROOT="$HOME/StoneveldGithub/Whit"
OUTPUT_DIR="$HOME/StoneveldGithub/Whit/AI_Context_Pack/ai-pack-v2/output"

mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE="$OUTPUT_DIR/snapshot_$TIMESTAMP.txt"

# ------------------------------------------------------------
# Snapshot header
# ------------------------------------------------------------

{
    echo "============================================================"
    echo "AI-PACK v2 PROJECT SNAPSHOT"
    echo "============================================================"
    echo "Generated: $(date)"
    echo "Project:   $PROJECT_ROOT"
    echo "============================================================"
    echo
} > "$OUTPUT_FILE"

# ------------------------------------------------------------
# Collect project files
# ------------------------------------------------------------

find "$PROJECT_ROOT" \
    -type d \( \
        -name ".git" \
        -o -name "__pycache__" \
        -o -name ".venv" \
        -o -name "venv" \
        -o -name "build" \
        -o -name "dist" \
        -o -name "target" \
        -o -name ".cache" \
    \) -prune \
    -o -type f \( \
        -name "*.py" \
        -o -name "*.sh" \
        -o -name "*.c" \
        -o -name "*.cpp" \
        -o -name "*.h" \
        -o -name "*.hpp" \
        -o -name "*.md" \
        -o -name "*.txt" \
        -o -name "*.log" \
    \) \
    ! -path "$OUTPUT_DIR/*" \
    -print0 |
sort -z |
while IFS= read -r -d '' FILE
do
    RELATIVE_PATH="${FILE#$PROJECT_ROOT/}"

    {
        echo
        echo "============================================================"
        echo "FILE: $RELATIVE_PATH"
        echo "============================================================"
        echo
        cat "$FILE"
        echo
    } >> "$OUTPUT_FILE"

done

# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

echo "Snapshot created:"
echo "$OUTPUT_FILE"
