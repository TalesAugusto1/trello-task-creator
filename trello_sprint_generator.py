#!/usr/bin/env python3
"""
Trello Sprint Generator

A tool to automatically generate Trello cards from markdown sprint files.
Parses sprint markdown files and creates organized cards with checklists, labels, and due dates.

Usage:
    python trello_sprint_generator.py --file sprint1.md --board-id YOUR_BOARD_ID
"""

import argparse
import json
import re
import requests
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class TrelloConfig:
    """Configuration for Trello API"""
    api_key: str
    token: str
    base_url: str = "https://api.trello.com/1"


@dataclass
class Task:
    """Represents a task from the markdown file"""
    title: str
    description: str
    estimated_time: str
    responsible: str
    acceptance_criteria: List[str]
    technical_requirements: List[str]
    deliverables: List[str]
    priority: str = "Medium"
    labels: List[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class Milestone:
    """Represents a milestone from the markdown file"""
    title: str
    duration: str
    priority: str
    dependencies: str
    tasks: List[Task]


@dataclass
class Sprint:
    """Represents a complete sprint"""
    title: str
    duration: str
    focus: str
    priority: str
    dependencies: str
    milestones: List[Milestone]
    success_metrics: List[str]
    definition_of_done: List[str]


class MarkdownParser:
    """Parses markdown sprint files into structured data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self._read_file()
    
    def _read_file(self) -> str:
        """Read the markdown file content"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Sprint file not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def parse_sprint(self) -> Sprint:
        """Parse the markdown content into a Sprint object"""
        # Extract sprint overview
        sprint_title = self._extract_sprint_title()
        sprint_info = self._extract_sprint_info()
        
        # Extract milestones and tasks
        milestones = self._extract_milestones()
        
        # Extract success metrics and definition of done
        success_metrics = self._extract_success_metrics()
        definition_of_done = self._extract_definition_of_done()
        
        return Sprint(
            title=sprint_title,
            duration=sprint_info.get('duration', ''),
            focus=sprint_info.get('focus', ''),
            priority=sprint_info.get('priority', 'Medium'),
            dependencies=sprint_info.get('dependencies', ''),
            milestones=milestones,
            success_metrics=success_metrics,
            definition_of_done=definition_of_done
        )
    
    def _extract_sprint_title(self) -> str:
        """Extract sprint title from markdown"""
        title_match = re.search(r'# 🎯 \*\*(.+?)\*\*', self.content)
        return title_match.group(1) if title_match else "Sprint"
    
    def _extract_sprint_info(self) -> Dict[str, str]:
        """Extract sprint overview information"""
        info = {}
        
        # Extract duration
        duration_match = re.search(r'\*\*Duração\*\*:\s*(.+?)(?:\n|$)', self.content)
        if duration_match:
            info['duration'] = duration_match.group(1).strip()
        
        # Extract focus
        focus_match = re.search(r'\*\*Foco\*\*:\s*(.+?)(?:\n|$)', self.content)
        if focus_match:
            info['focus'] = focus_match.group(1).strip()
        
        # Extract priority
        priority_match = re.search(r'\*\*Prioridade\*\*:\s*(.+?)(?:\n|$)', self.content)
        if priority_match:
            info['priority'] = priority_match.group(1).strip()
        
        # Extract dependencies
        dependencies_match = re.search(r'\*\*Dependências\*\*:\s*(.+?)(?:\n|$)', self.content)
        if dependencies_match:
            info['dependencies'] = dependencies_match.group(1).strip()
        
        return info
    
    def _extract_milestones(self) -> List[Milestone]:
        """Extract milestones and their tasks"""
        milestones = []
        
        # Find all milestone headers first
        milestone_header_pattern = r'## 🎯 \*\*(.+?)\*\*'
        milestone_headers = re.finditer(milestone_header_pattern, self.content)
        
        for i, header_match in enumerate(milestone_headers):
            title = header_match.group(1).strip()
            start_pos = header_match.start()
            
            # Find the next milestone or end of content
            next_milestone_pattern = r'## 🎯 \*\*'
            next_matches = list(re.finditer(next_milestone_pattern, self.content[start_pos + 1:]))
            
            if next_matches:
                end_pos = start_pos + 1 + next_matches[0].start()
            else:
                end_pos = len(self.content)
            
            # Extract the milestone content
            milestone_content = self.content[start_pos:end_pos]
            
            # Extract duration, priority, dependencies from the content
            duration_match = re.search(r'\*\*Duração\*\*:\s*(.+?)(?:\s*\||$)', milestone_content)
            priority_match = re.search(r'\*\*Prioridade\*\*:\s*(.+?)(?:\s*\||$)', milestone_content)
            dependencies_match = re.search(r'\*\*Dependências\*\*:\s*(.+?)(?:\n|$)', milestone_content)
            
            duration = duration_match.group(1).strip() if duration_match else ""
            priority = priority_match.group(1).strip() if priority_match else ""
            dependencies = dependencies_match.group(1).strip() if dependencies_match else ""
            
            # Extract tasks for this milestone
            tasks = self._extract_tasks_for_milestone(milestone_content)
            
            milestone = Milestone(
                title=title,
                duration=duration,
                priority=priority,
                dependencies=dependencies,
                tasks=tasks
            )
            milestones.append(milestone)
        
        return milestones
    
    def _extract_tasks_for_milestone(self, milestone_content: str) -> List[Task]:
        """Extract tasks from a milestone section"""
        tasks = []
        
        # Find all task sections within the milestone - capture full task content
        # Only match lines that start with #### (tasks), not ### (milestones)
        task_pattern = r'#### \*\*(.+?)\*\*\s*\*\*Tempo Estimado\*\*:\s*(.+?)\s*\|\s*\*\*Responsável\*\*:\s*(.+?)(?=####|---|$)'
        task_matches = re.finditer(task_pattern, milestone_content, re.DOTALL)
        
        for match in task_matches:
            title = match.group(1).strip()
            estimated_time = match.group(2).strip()
            responsible = match.group(3).strip()
            
            # Extract description, criteria, requirements, and deliverables
            task_content = match.group(0)
            description = self._extract_task_description(task_content)
            acceptance_criteria = self._extract_acceptance_criteria(task_content)
            technical_requirements = self._extract_technical_requirements(task_content)
            deliverables = self._extract_deliverables(task_content)
            
            # Determine priority based on milestone priority
            priority = self._determine_task_priority(task_content)
            
            # Extract labels
            labels = self._extract_task_labels(task_content)
            
            task = Task(
                title=title,
                description=description,
                estimated_time=estimated_time,
                responsible=responsible,
                acceptance_criteria=acceptance_criteria,
                technical_requirements=technical_requirements,
                deliverables=deliverables,
                priority=priority,
                labels=labels
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_task_description(self, task_content: str) -> str:
        """Extract task description"""
        desc_match = re.search(r'\*\*Descrição\*\*:\s*(.+?)(?=\*\*Critérios|\*\*Requisitos|\*\*Entregáveis|$)', task_content, re.DOTALL)
        return desc_match.group(1).strip() if desc_match else ""
    
    def _extract_acceptance_criteria(self, task_content: str) -> List[str]:
        """Extract acceptance criteria as a list"""
        criteria = []
        criteria_match = re.search(r'\*\*Critérios de Aceitação\*\*:(.+?)(?=\*\*Requisitos|\*\*Entregáveis|$)', task_content, re.DOTALL)
        
        if criteria_match:
            criteria_text = criteria_match.group(1)
            # Extract checkbox items
            checkbox_pattern = r'- \[ \] (.+?)(?:\n|$)'
            criteria_matches = re.findall(checkbox_pattern, criteria_text)
            criteria.extend(criteria_matches)
        
        return criteria
    
    def _extract_technical_requirements(self, task_content: str) -> List[str]:
        """Extract technical requirements"""
        requirements = []
        req_match = re.search(r'\*\*Requisitos Técnicos\*\*:(.+?)(?=\*\*Entregáveis|$)', task_content, re.DOTALL)
        
        if req_match:
            req_text = req_match.group(1)
            # Extract code blocks and bullet points
            code_pattern = r'```[\w]*\n(.*?)\n```'
            code_matches = re.findall(code_pattern, req_text, re.DOTALL)
            requirements.extend(code_matches)
            
            # Extract bullet points
            bullet_pattern = r'- (.+?)(?:\n|$)'
            bullet_matches = re.findall(bullet_pattern, req_text)
            requirements.extend(bullet_matches)
        
        return requirements
    
    def _extract_deliverables(self, task_content: str) -> List[str]:
        """Extract deliverables"""
        deliverables = []
        deliv_match = re.search(r'\*\*Entregáveis\*\*:(.+?)(?=---|$)', task_content, re.DOTALL)
        
        if deliv_match:
            deliv_text = deliv_match.group(1)
            bullet_pattern = r'- (.+?)(?:\n|$)'
            deliv_matches = re.findall(bullet_pattern, deliv_text)
            deliverables.extend(deliv_matches)
        
        return deliverables
    
    def _determine_task_priority(self, task_content: str) -> str:
        """Determine task priority based on content"""
        if 'crítica' in task_content.lower() or 'critical' in task_content.lower():
            return 'High'
        elif 'alta' in task_content.lower() or 'high' in task_content.lower():
            return 'High'
        elif 'baixa' in task_content.lower() or 'low' in task_content.lower():
            return 'Low'
        else:
            return 'Medium'
    
    def _extract_task_labels(self, task_content: str) -> List[str]:
        """Extract labels for the task"""
        labels = []
        
        # Add priority-based labels
        if 'crítica' in task_content.lower() or 'critical' in task_content.lower():
            labels.append('Priority: Critical')
        elif 'alta' in task_content.lower() or 'high' in task_content.lower():
            labels.append('Priority: High')
        elif 'baixa' in task_content.lower() or 'low' in task_content.lower():
            labels.append('Priority: Low')
        
        # Add technology-based labels
        if 'expo' in task_content.lower():
            labels.append('Technology: Expo')
        if 'firebase' in task_content.lower():
            labels.append('Technology: Firebase')
        if 'typescript' in task_content.lower():
            labels.append('Technology: TypeScript')
        if 'react' in task_content.lower():
            labels.append('Technology: React')
        if 'ui' in task_content.lower() or 'ux' in task_content.lower():
            labels.append('Category: UI/UX')
        if 'backend' in task_content.lower():
            labels.append('Category: Backend')
        if 'frontend' in task_content.lower():
            labels.append('Category: Frontend')
        
        return labels
    
    def _extract_success_metrics(self) -> List[str]:
        """Extract success metrics"""
        metrics = []
        metrics_match = re.search(r'## 📊 \*\*Métricas de Sucesso do Sprint \d+\*\*(.+?)(?=##|$)', self.content, re.DOTALL)
        
        if metrics_match:
            metrics_text = metrics_match.group(1)
            checkbox_pattern = r'- \[ \] (.+?)(?:\n|$)'
            metrics_matches = re.findall(checkbox_pattern, metrics_text)
            metrics.extend(metrics_matches)
        
        return metrics
    
    def _extract_definition_of_done(self) -> List[str]:
        """Extract definition of done items"""
        done_items = []
        done_match = re.search(r'## 📋 \*\*Definição de Pronto do Sprint \d+\*\*(.+?)(?=##|$)', self.content, re.DOTALL)
        
        if done_match:
            done_text = done_match.group(1)
            checkbox_pattern = r'- \[ \] (.+?)(?:\n|$)'
            done_matches = re.findall(checkbox_pattern, done_text)
            done_items.extend(done_matches)
        
        return done_items


class TrelloClient:
    """Client for interacting with Trello API"""
    
    def __init__(self, config: TrelloConfig):
        self.config = config
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a request to Trello API"""
        url = f"{self.config.base_url}/{endpoint}"
        params = kwargs.get('params', {})
        params.update({
            'key': self.config.api_key,
            'token': self.config.token
        })
        kwargs['params'] = params
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Trello API request failed: {e}")
    
    def get_board_lists(self, board_id: str) -> List[Dict]:
        """Get all lists for a board"""
        return self._make_request('GET', f'boards/{board_id}/lists')
    
    def create_card(self, list_id: str, name: str, desc: str = "", labels: List[str] = None, due: str = None) -> Dict:
        """Create a new card"""
        data = {
            'idList': list_id,
            'name': name,
            'desc': desc
        }
        
        if due:
            data['due'] = due
        
        if labels:
            data['idLabels'] = ','.join(labels)
        
        return self._make_request('POST', 'cards', json=data)
    
    def create_checklist(self, card_id: str, name: str, items: List[str]) -> Dict:
        """Create a checklist on a card"""
        checklist_data = {
            'idCard': card_id,
            'name': name
        }
        
        checklist = self._make_request('POST', 'checklists', json=checklist_data)
        
        # Add items to the checklist
        for item in items:
            self._make_request('POST', f'checklists/{checklist["id"]}/checkItems', 
                             json={'name': item})
        
        return checklist
    
    def get_or_create_label(self, board_id: str, name: str, color: str = "blue") -> str:
        """Get existing label or create a new one"""
        # First, try to get existing labels
        labels = self._make_request('GET', f'boards/{board_id}/labels')
        
        for label in labels:
            if label['name'] == name:
                return label['id']
        
        # Create new label if not found
        label_data = {
            'name': name,
            'color': color
        }
        
        new_label = self._make_request('POST', f'boards/{board_id}/labels', json=label_data)
        return new_label['id']


class SprintGenerator:
    """Main class for generating Trello cards from sprint markdown"""
    
    def __init__(self, config: TrelloConfig):
        self.config = config
        self.trello_client = TrelloClient(config)
        self.label_cache = {}
    
    def list_available_lists(self, board_id: str) -> List[Dict]:
        """List all available lists on the board"""
        try:
            lists = self.trello_client.get_board_lists(board_id)
            print(f"📋 Available lists on board:")
            for i, list_info in enumerate(lists):
                print(f"  {i+1}. {list_info['name']} (ID: {list_info['id']})")
            return lists
        except Exception as e:
            print(f"❌ Error fetching lists: {e}")
            return []

    def generate_cards(self, sprint: Sprint, board_id: str, target_list_name: str = "Backlog") -> Dict:
        """Generate Trello cards from sprint data"""
        # First, show available lists
        available_lists = self.list_available_lists(board_id)
        
        # Find the target list or use the first available list
        target_list = None
        for list_info in available_lists:
            if list_info['name'] == target_list_name:
                target_list = list_info
                break
        
        if not target_list and available_lists:
            target_list = available_lists[0]
            print(f"⚠️  List '{target_list_name}' not found. Using '{target_list['name']}' instead.")
        elif not target_list:
            print(f"❌ No lists found on board. Creating '{target_list_name}' list...")
            target_list = self.trello_client.create_list(board_id, target_list_name)
        
        result = {
            'sprint_card': None,
            'milestone_cards': [],
            'task_cards': [],
            'created_labels': []
        }
        
        # Use the target list we found/created
        lists = [target_list]
        
        # Create labels
        self._create_labels(board_id, sprint)
        
        # Create sprint overview card
        sprint_card = self._create_sprint_card(sprint, target_list['id'])
        result['sprint_card'] = sprint_card
        
        # Create milestone cards
        for milestone in sprint.milestones:
            milestone_card = self._create_milestone_card(milestone, target_list['id'], sprint)
            result['milestone_cards'].append(milestone_card)
            
            # Create task cards for this milestone
            for task in milestone.tasks:
                task_card = self._create_task_card(task, milestone, target_list['id'], sprint)
                result['task_cards'].append(task_card)
        
        return result
    
    def _clean_title(self, title: str) -> str:
        """Clean title by removing markdown formatting and metadata"""
        # Remove markdown bold formatting
        title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
        
        # Remove markdown headers
        title = re.sub(r'^#+\s*', '', title)
        
        # Remove any trailing metadata patterns
        title = re.sub(r'\s*\*\*Duração\*\*:.*$', '', title)
        title = re.sub(r'\s*\*\*Prioridade\*\*:.*$', '', title)
        title = re.sub(r'\s*\*\*Dependências\*\*:.*$', '', title)
        
        # Clean up extra whitespace
        title = title.strip()
        
        return title

    def _create_labels(self, board_id: str, sprint: Sprint):
        """Create necessary labels for the sprint"""
        label_colors = {
            'Priority: Critical': 'red',
            'Priority: High': 'orange',
            'Priority: Medium': 'yellow',
            'Priority: Low': 'green',
            'Technology: Expo': 'blue',
            'Technology: Firebase': 'purple',
            'Technology: TypeScript': 'sky',
            'Technology: React': 'blue',
            'Category: UI/UX': 'pink',
            'Category: Backend': 'black',
            'Category: Frontend': 'lime'
        }
        
        # Collect all unique labels from tasks
        all_labels = set()
        for milestone in sprint.milestones:
            for task in milestone.tasks:
                all_labels.update(task.labels)
        
        # Create labels
        for label_name in all_labels:
            color = label_colors.get(label_name, 'blue')
            label_id = self.trello_client.get_or_create_label(board_id, label_name, color)
            self.label_cache[label_name] = label_id
    
    def _create_sprint_card(self, sprint: Sprint, list_id: str) -> Dict:
        """Create the main sprint overview card"""
        description = f"""
**🎯 Sprint Overview**

**Duration:** {sprint.duration}
**Focus:** {sprint.focus}
**Priority:** {sprint.priority}
**Dependencies:** {sprint.dependencies}

**📊 Success Metrics:**
{chr(10).join([f"• {metric}" for metric in sprint.success_metrics])}

**📋 Definition of Done:**
{chr(10).join([f"• {item}" for item in sprint.definition_of_done])}

**📈 Milestones:**
{chr(10).join([f"• {milestone.title} ({milestone.duration})" for milestone in sprint.milestones])}
        """.strip()
        
        return self.trello_client.create_card(
            list_id=list_id,
            name=f"🎯 {sprint.title}",
            desc=description,
            labels=[self.label_cache.get('Priority: High', '')]
        )
    
    def _create_milestone_card(self, milestone: Milestone, list_id: str, sprint: Sprint) -> Dict:
        """Create a milestone card"""
        description = f"""
**🎯 Milestone Overview**

**Duration:** {milestone.duration}
**Priority:** {milestone.priority}
**Dependencies:** {milestone.dependencies}

**📋 Tasks ({len(milestone.tasks)}):**
{chr(10).join([f"• {self._clean_title(task.title)} ({task.estimated_time})" for task in milestone.tasks])}
        """.strip()
        
        # Determine milestone priority label
        priority_label = 'Priority: Medium'
        if 'crítica' in milestone.priority.lower() or 'critical' in milestone.priority.lower():
            priority_label = 'Priority: Critical'
        elif 'alta' in milestone.priority.lower() or 'high' in milestone.priority.lower():
            priority_label = 'Priority: High'
        
        return self.trello_client.create_card(
            list_id=list_id,
            name=f"🎯 {self._clean_title(milestone.title)}",
            desc=description,
            labels=[self.label_cache.get(priority_label, '')]
        )
    
    def _create_task_card(self, task: Task, milestone: Milestone, list_id: str, sprint: Sprint) -> Dict:
        """Create a task card with checklist"""
        description = f"""
**📝 Task Details**

**Estimated Time:** {task.estimated_time}
**Responsible:** {task.responsible}
**Milestone:** {milestone.title}

**📋 Description:**
{task.description}

**🔧 Technical Requirements:**
{chr(10).join([f"• {req}" for req in task.technical_requirements])}

**📦 Deliverables:**
{chr(10).join([f"• {deliv}" for deliv in task.deliverables])}
        """.strip()
        
        # Create the card
        card = self.trello_client.create_card(
            list_id=list_id,
            name=f"📋 {self._clean_title(task.title)}",
            desc=description,
            labels=[self.label_cache.get(label, '') for label in task.labels if label in self.label_cache]
        )
        
        # Create acceptance criteria checklist
        if task.acceptance_criteria:
            self.trello_client.create_checklist(
                card_id=card['id'],
                name="✅ Acceptance Criteria",
                items=task.acceptance_criteria
            )
        
        return card


def load_config() -> TrelloConfig:
    """Load Trello configuration from environment variables or secrets file"""
    # First try to load from environment variables
    api_key = os.getenv('TRELLO_API_KEY')
    token = os.getenv('TRELLO_TOKEN')
    
    # If not found, try to load from secrets.env file
    if not api_key or not token:
        secrets_file = 'secrets.env'
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'TRELLO_API_KEY':
                            api_key = value
                        elif key == 'TRELLO_TOKEN':
                            token = value
    
    # If still not found, try to load from config file (fallback)
    if not api_key or not token:
        config_file = 'trello_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                api_key = config_data.get('api_key')
                token = config_data.get('token')
    
    if not api_key or not token:
        raise Exception("Trello API credentials not found. Please set TRELLO_API_KEY and TRELLO_TOKEN environment variables, create secrets.env file, or create trello_config.json")
    
    return TrelloConfig(api_key=api_key, token=token)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Trello cards from sprint markdown files')
    parser.add_argument('--file', '-f', required=True, help='Path to the sprint markdown file')
    parser.add_argument('--board-id', '-b', required=True, help='Trello board ID')
    parser.add_argument('--list-name', '-l', default='To Do', help='Target list name (default: To Do)')
    parser.add_argument('--dry-run', action='store_true', help='Parse and display results without creating cards')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        
        # Parse sprint file
        parser = MarkdownParser(args.file)
        sprint = parser.parse_sprint()
        
        print(f"📋 Parsed Sprint: {sprint.title}")
        print(f"🎯 Milestones: {len(sprint.milestones)}")
        print(f"📝 Total Tasks: {sum(len(m.tasks) for m in sprint.milestones)}")
        
        if args.dry_run:
            print("\n🔍 Dry run - no cards will be created")
            print(f"Sprint: {sprint.title}")
            for milestone in sprint.milestones:
                print(f"  Milestone: {milestone.title} ({len(milestone.tasks)} tasks)")
                for task in milestone.tasks:
                    print(f"    Task: {task.title}")
            return
        
        # Generate cards
        generator = SprintGenerator(config)
        result = generator.generate_cards(sprint, args.board_id, args.list_name)
        
        print(f"\n✅ Successfully created:")
        print(f"  📋 Sprint card: {result['sprint_card']['name']}")
        print(f"  🎯 Milestone cards: {len(result['milestone_cards'])}")
        print(f"  📝 Task cards: {len(result['task_cards'])}")
        print(f"  🏷️  Labels created: {len(result['created_labels'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
