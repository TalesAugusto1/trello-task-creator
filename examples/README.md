# Examples

This directory contains example files for the Trello Sprint Generator.

## 📁 Files

- `example_sprint.md` - Sample sprint file showing the expected markdown format

## 📝 Markdown Format

The tool expects markdown files with this structure:

```markdown
# 🎯 **Sprint Title**

## 📋 **Visão Geral do Sprint**
- **Duração**: 5 dias
- **Foco**: Sprint focus
- **Prioridade**: Crítica
- **Dependências**: None

## 🎯 **MARCO 1.1: Milestone Title**
**Duração**: 2 dias | **Prioridade**: Crítica | **Dependências**: None

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

## 🚀 Usage Examples

### Basic Usage
```bash
python main.py --file examples/example_sprint.md --board-id YOUR_BOARD_ID
```

### Dry Run
```bash
python main.py --file examples/example_sprint.md --board-id YOUR_BOARD_ID --dry-run
```

### Custom List
```bash
python main.py --file examples/example_sprint.md --board-id YOUR_BOARD_ID --list-name "Backlog"
```
