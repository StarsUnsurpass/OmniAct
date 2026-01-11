#!/bin/bash
set -e

echo ">>> Setting up OmniAct Environment..."

# 1. Install Python dependencies
if [ -f "agent/requirements.txt" ]; then
    echo ">>> Installing Python dependencies..."
    pip install -r agent/requirements.txt
fi

# 2. Build Rust Extension
echo ">>> Building Rust 'vision_core' extension..."
# Check if maturin is installed, if not, it should have been installed by requirements.txt
# We assume the user is in a venv or has permission.
maturin develop --manifest-path crates/vision_core/Cargo.toml

echo ">>> Setup Complete!"
echo "Run the agent with: python agent/main.py"
