# Quick Start Guide

Get your Dexcom menubar app running in 5 minutes!

## Step 1: Setup Python Environment

```bash
cd dexcom-menubar-app

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Enable Dexcom Share

On your iPhone/Android with Dexcom G7 app:

1. Open Dexcom G7 app
2. Tap Settings (gear icon)
3. Tap Share
4. Enable Share
5. Note your username and password

## Step 3: Set Up Credentials

Run the interactive setup script:

```bash
./setup-credentials.sh

# Or directly
python -m dexcom_menubar.setup
```

Follow the prompts to enter:
1. Your Dexcom Share username
2. Your Dexcom Share password
3. Your region (US or Outside US)

The script will test your credentials and save them securely to macOS Keychain.

## Step 4: Run the App

```bash
# Simple way
./run.sh

# Or directly
python -m dexcom_menubar.app
```

The app will appear in your menubar showing your glucose reading!

## That's it!

You should now see your glucose reading in the menubar like: `120 →`

The app will:
- Update automatically every 5 minutes
- Show recent readings when clicked
- Display trend arrows (⬆, →, ⬇, etc.)

## Troubleshooting

**App doesn't start?**
```bash
# Check Python version (needs 3.8+)
python3 --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Authentication fails?**
- Verify credentials work on share.dexcom.com
- Make sure Share is enabled in the Dexcom app
- Try both "US" and "Outside US" regions

**No data showing?**
- Wait 5 minutes for first reading
- Click "Refresh Now" in the menu
- Check that your CGM is transmitting to your phone

## Need Help?

See the full [README.md](README.md) for detailed documentation.
