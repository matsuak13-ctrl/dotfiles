#!/bin/bash
# Get directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=== AI & Notion News Mailer Setup (Re-implemented) ==="

# 1. Create Python virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
else
    echo "Virtual environment (.venv) already exists."
fi

# 2. Upgrade pip and install requirements
echo "Installing dependencies from requirements.txt..."
.venv/bin/python3 -m pip install --upgrade pip
.venv/bin/python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

# 3. Create .env if not exists (CRITICAL: Never overwrite existing .env)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "Please update the newly created '.env' file with your credentials (GEMINI_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD)."
    else
        echo "Warning: .env.example not found. Cannot create .env template."
    fi
else
    echo "'.env' file already exists. Preserving existing configuration (WILL NOT OVERWRITE)."
fi

# 4. Make run.sh and setup.sh executable
echo "Making scripts executable..."
chmod +x run.sh
chmod +x setup.sh

echo ""
echo "=== Setup Completed Successfully ==="
echo "Next Steps:"
echo "1. Verify that your '.env' file contains valid credentials."
echo "2. Test the script manually by running:"
echo "   ./.venv/bin/python main.py"
echo "3. Register the scheduler in launchd to run daily at 8:00 AM."
echo ""
