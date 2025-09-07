# Configuration Guide

This directory contains configuration files for the Trello Sprint Generator.

## 🔧 Setup

### 1. Copy the template
```bash
cp trello_config.json.template trello_config.json
```

### 2. Get your Trello API credentials
1. Go to [https://trello.com/app-key](https://trello.com/app-key)
2. Copy your **API Key**
3. Generate a **Token** with read/write permissions
4. Copy your **Board ID** from the Trello board URL

### 3. Configure credentials

#### Option A: Environment Variables (Recommended)
```bash
export TRELLO_API_KEY="your_api_key_here"
export TRELLO_TOKEN="your_token_here"
```

#### Option B: Secrets File
Create `secrets.env`:
```bash
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
```

#### Option C: Config File (Fallback)
Edit `trello_config.json`:
```json
{
  "api_key": "your_api_key_here",
  "token": "your_token_here",
  "board_id": "your_board_id_here"
}
```

## 🔒 Security

- Never commit `secrets.env` or `trello_config.json` to version control
- These files are automatically excluded by `.gitignore`
- Use environment variables in production environments

## 📝 Files

- `trello_config.json.template` - Template configuration file
- `secrets.env` - Your API credentials (create this file)
- `trello_config.json` - Fallback configuration (create this file)
