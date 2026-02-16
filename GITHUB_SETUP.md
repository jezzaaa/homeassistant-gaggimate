# GitHub Setup Instructions

Your GaggiMate Home Assistant integration is ready to be pushed to GitHub! Follow these steps:

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the **+** icon in the top right corner
3. Select **New repository**
4. Fill in the repository details:
   - **Repository name**: `homeassistant-gaggimate`
   - **Description**: "Home Assistant custom integration for GaggiMate espresso machines"
   - **Visibility**: Public (required for HACS)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **Create repository**

## Step 2: Push Your Code to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
cd /home/jpl/homeassistant-gaggimate

# Add the remote repository
git remote add origin https://github.com/jezzaaa/homeassistant-gaggimate.git

# Push your code
git push -u origin main
```

**Alternative using SSH** (if you have SSH keys set up):
```bash
git remote add origin git@github.com:jezzaaa/homeassistant-gaggimate.git
git push -u origin main
```

## Step 3: Create a Release (Required for HACS)

1. Go to your repository on GitHub
2. Click on **Releases** (right sidebar)
3. Click **Create a new release**
4. Fill in the release details:
   - **Tag version**: `v0.1.0` (or `0.1.0`)
   - **Release title**: `v0.1.0 - Initial Release`
   - **Description**: 
     ```
     Initial release of GaggiMate Home Assistant integration
     
     Features:
     - Full WebSocket support with real-time updates
     - 17 sensors for comprehensive monitoring
     - Power switch, mode selector, profile selector
     - Bluetooth scale scanning
     - Firmware update management
     - mDNS discovery support
     ```
5. Click **Publish release**

## Step 4: Add to HACS

### Option A: Add as Custom Repository (Immediate)

Users can add your integration immediately:

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **three dots** menu (top right)
4. Select **Custom repositories**
5. Add your repository URL: `https://github.com/jezzaaa/homeassistant-gaggimate`
6. Select category: **Integration**
7. Click **Add**

### Option B: Submit to HACS Default Repository (Takes Time)

To make your integration available in HACS by default:

1. Go to [HACS Default Repository](https://github.com/hacs/default)
2. Click **Issues** → **New Issue**
3. Select **Add repository to HACS**
4. Fill in the form with your repository details
5. Wait for HACS team review and approval

## Step 5: Update README Badges

The README.md has already been updated with your GitHub username (jezzaaa). After pushing to GitHub, you're all set!

## Step 6: Test Installation

Test that users can install your integration:

1. In Home Assistant, go to HACS → Integrations
2. Add your repository as a custom repository
3. Search for "GaggiMate"
4. Click Install
5. Restart Home Assistant
6. Add the integration via Settings → Devices & Services

## Maintenance Tips

### Creating New Releases

When you make updates:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push

# Create a new release on GitHub
# Tag: v0.2.0, v0.3.0, etc.
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes

Update the version in `custom_components/gaggimate/manifest.json` when releasing.

## Repository Structure

Your repository now contains:

```
homeassistant-gaggimate/
├── .gitignore                          # Git ignore rules
├── LICENSE                             # MIT License
├── README.md                           # Main documentation
├── hacs.json                           # HACS configuration
└── custom_components/
    └── gaggimate/
        ├── __init__.py                 # Integration entry point
        ├── manifest.json               # Integration metadata
        ├── const.py                    # Constants
        ├── coordinator.py              # WebSocket coordinator
        ├── config_flow.py              # Setup flow
        ├── sensor.py                   # Sensor platform
        ├── binary_sensor.py            # Binary sensor platform
        ├── switch.py                   # Switch platform
        ├── select.py                   # Select platform
        ├── button.py                   # Button platform
        ├── update.py                   # Update platform
        ├── strings.json                # UI strings
        └── translations/
            └── en.json                 # English translations
```

## Support

If you need help:
- GitHub Issues: For bug reports and feature requests
- Home Assistant Community: For general discussion
- HACS Discord: For HACS-specific questions

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code to GitHub
3. ✅ Create initial release (v0.1.0)
4. ✅ Update README badges with your username
5. ✅ Test installation via HACS
6. 📢 Share with the community!

Good luck with your integration! 🎉
