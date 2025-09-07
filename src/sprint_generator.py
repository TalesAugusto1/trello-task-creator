"""
Main sprint generator class for creating Trello cards.
"""

import re
from typing import Dict, List
from .models import Sprint, Milestone, Task
from .trello_client import TrelloClient


class SprintGeneratorError(Exception):
    """Sprint generator related errors"""
    pass


class SprintGenerator:
    """Main class for generating Trello cards from sprint markdown"""
    
    def __init__(self, trello_client: TrelloClient):
        self.trello_client = trello_client
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
        target_list = self._find_or_create_target_list(available_lists, target_list_name, board_id)
        
        result = {
            'sprint_card': None,
            'milestone_cards': [],
            'task_cards': [],
            'created_labels': []
        }
        
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
    
    def _find_or_create_target_list(self, available_lists: List[Dict], target_list_name: str, board_id: str) -> Dict:
        """Find the target list or create it if it doesn't exist"""
        # Find the target list
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
        
        return target_list
    
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
