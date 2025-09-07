# Trello Sprint Generator

A powerful tool to automatically generate Trello cards from markdown sprint files. Perfect for converting detailed sprint planning documents into organized Trello boards with tasks, milestones, and acceptance criteria.

## Features

- ✅ **Automatic Card Creation** - Converts markdown sprints into Trello cards
- ✅ **Rich Task Details** - Includes descriptions, technical requirements, and deliverables
- ✅ **Interactive Checklists** - Creates acceptance criteria as checklists
- ✅ **Milestone Organization** - Groups tasks by sprints/milestones
- ✅ **Clean Card Names** - Removes markdown formatting for professional appearance
- ✅ **Flexible Configuration** - Multiple ways to configure API credentials

## Setup

### 1. Get Trello API Credentials

1. Go to [https://trello.com/app-key](https://trello.com/app-key)
2. Copy your **API Key**
3. Generate a **Token** with read/write permissions
4. Copy your **Board ID** from the Trello board URL

### 2. Configure Credentials

Choose one of these methods:

#### Method A: Environment Variables (Recommended)
```bash
export TRELLO_API_KEY="your_api_key_here"
export TRELLO_TOKEN="your_token_here"
```

#### Method B: Secrets File
Create a `secrets.env` file:
```bash
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
```

#### Method C: Config File (Fallback)
Create a `trello_config.json` file:
```json
{
  "api_key": "your_api_key_here",
  "token": "your_token_here",
  "board_id": "your_board_id_here"
}
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python trello_sprint_generator.py --file sprints.md --board-id YOUR_BOARD_ID
```

### Advanced Options
```bash
python trello_sprint_generator.py \
  --file sprints.md \
  --board-id YOUR_BOARD_ID \
  --list-name "Backlog" \
  --dry-run
```

### Options
- `--file, -f`: Path to the sprint markdown file (required)
- `--board-id, -b`: Trello board ID (required)
- `--list-name, -l`: Target list name (default: "Backlog")
- `--dry-run`: Preview results without creating cards

## Markdown Format

The tool expects markdown files with this structure:

```markdown
# 🎯 **Sprint Title**

## 🎯 **MARCO 1.1: Milestone Title**
**Duração**: 2 dias | **Prioridade**: Crítica | **Dependências**: Nenhuma

#### **Tarefa 1.1.1: Task Title**
**Tempo Estimado**: 4 horas | **Responsável**: Team Member

**Descrição**: Task description here.

**Critérios de Aceitação**:
- [ ] Acceptance criteria 1
- [ ] Acceptance criteria 2

**Requisitos Técnicos**:
- Technical requirement 1
- Technical requirement 2

**Entregáveis**:
- Deliverable 1
- Deliverable 2
```

## Security

- Never commit API credentials to version control
- Use environment variables or the `secrets.env` file
- The `secrets.env` file is automatically excluded from git

## Examples

See `example_sprint.md` for a complete example of the expected markdown format.

## License

MIT License - feel free to use and modify as needed.