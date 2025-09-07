# 🖥️ GUI User Guide

A comprehensive guide to using the Trello Sprint Generator GUI.

## 🚀 Getting Started

### Launch the GUI
```bash
python gui.py
# or
make gui
```

## 📋 GUI Components

### 🔧 Configuration Section

**Purpose**: Set up your Trello API credentials

**Fields**:
- **API Key**: Your Trello API key (from https://trello.com/app-key)
- **Token**: Your Trello token (generated with read/write permissions)
- **Board ID**: The ID of your target Trello board

**Buttons**:
- **🔍 Test Connection**: Verify your credentials work
- **💾 Load Config**: Load saved configuration from file
- **💾 Save Config**: Save current configuration to file

**Status**: Shows connection status (✅ Success / ❌ Failed)

### 📁 Sprint File Section

**Purpose**: Select and parse your sprint markdown file

**Fields**:
- **Sprint File**: Path to your markdown sprint file

**Buttons**:
- **📂 Browse**: Open file dialog to select sprint file
- **📋 Parse Sprint**: Parse the selected file and show preview

**Status**: Shows file selection and parsing status

### 👀 Sprint Preview Section

**Purpose**: Preview parsed sprint data before generating cards

**Content**:
- Sprint title, duration, focus, priority
- List of milestones with their tasks
- Total task count
- Task details and estimated times

### 🚀 Actions Section

**Purpose**: Generate Trello cards from the parsed sprint

**Fields**:
- **Target List**: Select which Trello list to create cards in

**Buttons**:
- **🔄 Refresh Lists**: Get current lists from your Trello board
- **🔍 Preview Cards**: Show what cards will be created
- **🎯 Generate Cards**: Create all cards in Trello

### 📊 Status Section

**Purpose**: Show progress and current operation status

**Components**:
- **Progress Bar**: Visual progress indicator
- **Status Text**: Current operation description

## 🔄 Workflow

### 1. **Configure API Credentials**
1. Get your API key from https://trello.com/app-key
2. Generate a token with read/write permissions
3. Enter credentials in the Configuration section
4. Click "🔍 Test Connection" to verify
5. Click "💾 Save Config" to save for future use

### 2. **Select Sprint File**
1. Click "📂 Browse" to select your sprint markdown file
2. Click "📋 Parse Sprint" to parse the file
3. Review the preview to ensure everything looks correct

### 3. **Set Target Board**
1. Enter your Trello Board ID
2. Click "🔄 Refresh Lists" to get available lists
3. Select the target list from the dropdown

### 4. **Generate Cards**
1. Click "🔍 Preview Cards" to see what will be created
2. Click "🎯 Generate Cards" to create all cards
3. Monitor progress in the status section

## 🎨 GUI Features

### ✨ Modern Design
- Clean, professional interface
- Intuitive layout with logical grouping
- Modern color scheme and typography
- Responsive layout that adapts to window size

### 🔄 Threading
- All operations run in background threads
- GUI remains responsive during long operations
- Progress indicators for visual feedback

### 💾 Configuration Management
- Save/load configuration from files
- Automatic configuration loading on startup
- Secure credential storage

### 📋 Preview Functionality
- Real-time sprint parsing and preview
- Card generation preview before execution
- Detailed task and milestone information

### 🎯 Error Handling
- Comprehensive error messages
- Graceful handling of API errors
- User-friendly error dialogs

## 🛠️ Troubleshooting

### Common Issues

**"Connection failed"**
- Verify your API key and token are correct
- Check that you have internet connectivity
- Ensure your token has the necessary permissions

**"Parse failed"**
- Check that your markdown file follows the expected format
- Verify the file is not corrupted
- See the markdown format guide in examples/

**"No lists found"**
- Verify your Board ID is correct
- Ensure you have access to the board
- Try refreshing the lists

**"Generation failed"**
- Check that all required fields are filled
- Verify your API credentials are still valid
- Ensure you have write permissions to the board

### Getting Help

- Check the [main documentation](README.md)
- Review the [examples](examples/) directory
- Check the [configuration guide](config/README.md)

## 🎯 Tips for Best Results

1. **Always test connection first** before generating cards
2. **Preview your sprint** to ensure parsing is correct
3. **Use descriptive sprint files** with clear milestone and task structure
4. **Save your configuration** to avoid re-entering credentials
5. **Start with a small test sprint** to verify everything works
6. **Check your Trello board** after generation to verify cards were created correctly
