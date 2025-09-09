"""
Main sprint generator class for creating Trello cards.
"""

import re
from typing import Dict, List
from .models import Sprint, Milestone, Task
from .trello_client import TrelloClient
from .utils import clean_title


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
        
        # Create tag reference card first (administrative model)
        tag_reference_card = self._create_tag_reference_card(target_list['id'])
        result['tag_reference_card'] = tag_reference_card
        
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
    
    def _create_tag_reference_card(self, list_id: str) -> Dict:
        """Create a comprehensive tag reference card for administrative purposes"""
        description = """
**🏷️ TAG REFERENCE CARD - Administrative Model**

This card serves as a reference model for all available tags in the project. Use this as a guide for maintaining consistency across all tasks and sprints.

**📋 ACCEPTANCE CRITERIA:**
- [ ] All tag categories are documented
- [ ] Color coding is clearly defined  
- [ ] Usage guidelines are provided
- [ ] Team members understand the tag system

**🎯 PRIORITY TAGS:**
• `Priority: Critical` (Red) - Urgent, must be completed immediately
• `Priority: High` (Orange) - Important, should be completed soon
• `Priority: Medium` (Yellow) - Normal priority, standard timeline
• `Priority: Low` (Green) - Can be completed when time allows

**🔧 TASK TYPE TAGS:**
• `Type: Setup` (Yellow) - Configuration, installation, initialization
• `Type: Development` (Blue) - Coding, implementation, features
• `Type: Testing` (Green) - Testing, validation, quality assurance
• `Type: Documentation` (Sky) - Documentation, guides, manuals
• `Type: Integration` (Purple) - API integration, service connections
• `Type: UI/UX` (Pink) - User interface, user experience, design
• `Type: Architecture` (Black) - System design, patterns, structure

**🎨 FRONTEND TECHNOLOGY TAGS:**
• `Frontend: React` (Blue) - React.js web framework
• `Frontend: Vue.js` (Green) - Vue.js framework
• `Frontend: Angular` (Red) - Angular framework
• `Frontend: TypeScript` (Sky) - TypeScript language
• `Frontend: JavaScript` (Yellow) - JavaScript language
• `Frontend: CSS` (Pink) - Cascading Style Sheets
• `Frontend: HTML` (Orange) - HyperText Markup Language

**📱 APP TECHNOLOGY TAGS:**
• `App: Expo` (Blue) - Expo development platform
• `App: React Native` (Sky) - React Native framework
• `App: Flutter` (Blue) - Flutter framework
• `App: iOS` (Black) - iOS platform
• `App: Android` (Green) - Android platform
• `App: Mobile` (Blue) - General mobile development

**⚙️ BACKEND TECHNOLOGY TAGS:**
• `Backend: Firebase` (Purple) - Firebase platform
• `Backend: Node.js` (Green) - Node.js runtime
• `Backend: Python` (Green) - Python language
• `Backend: Java` (Red) - Java language
• `Backend: Database` (Black) - Database technologies
• `Backend: AWS` (Orange) - Amazon Web Services
• `Backend: REST API` (Sky) - RESTful API

**🔧 DEVOPS TECHNOLOGY TAGS:**
• `DevOps: Git` (Black) - Version control
• `DevOps: GitHub` (Black) - GitHub platform
• `DevOps: npm` (Red) - Node package manager
• `DevOps: ESLint` (Yellow) - Code linting
• `DevOps: Docker` (Blue) - Containerization
• `DevOps: CI/CD` (Green) - Continuous Integration/Deployment

**🧪 TESTING TECHNOLOGY TAGS:**
• `Testing: Jest` (Green) - JavaScript testing framework
• `Testing: Cypress` (Green) - End-to-end testing
• `Testing: Playwright` (Green) - Browser automation
• `Testing: Selenium` (Green) - Web automation

**📊 COMPLEXITY TAGS:**
• `Complexity: Simple` (Green) - Easy tasks, 1-2 hours
• `Complexity: Medium` (Yellow) - Moderate tasks, 3-8 hours
• `Complexity: Complex` (Orange) - Difficult tasks, 9-16 hours
• `Complexity: Very Complex` (Red) - Very difficult tasks, 16+ hours

**🚀 PHASE TAGS:**
• `Phase: Foundation` (Blue) - Project setup, initial configuration
• `Phase: Development` (Green) - Core development work
• `Phase: Testing` (Yellow) - Testing and validation phase
• `Phase: Deployment` (Purple) - Release and deployment phase
• `Phase: Maintenance` (Black) - Ongoing maintenance and support

**📝 USAGE GUIDELINES:**
1. **Maximum 6 tags per task** - Keep it clean and focused
2. **Always include Priority** - Every task needs a priority level
3. **One Task Type only** - Choose the most relevant type
4. **2-3 Technology tags max** - Main framework, key language, platform
5. **Complexity only if not simple** - Hide "Simple" complexity to reduce clutter
6. **Phase only for Foundation/Development** - Most relevant phases only
        """.strip()
        
        # Create the card with all available labels as a demonstration
        all_labels = [
            'Priority: Critical', 'Priority: High', 'Priority: Medium', 'Priority: Low',
            'Type: Setup', 'Type: Development', 'Type: Testing', 'Type: Documentation',
            'Type: Integration', 'Type: UI/UX', 'Type: Architecture',
            'Frontend: React', 'Frontend: TypeScript', 'Frontend: CSS',
            'App: Expo', 'App: iOS', 'App: Android',
            'Backend: Firebase', 'Backend: Node.js', 'Backend: Database',
            'DevOps: Git', 'DevOps: ESLint', 'DevOps: Docker',
            'Testing: Jest', 'Testing: Cypress',
            'Complexity: Medium', 'Complexity: Complex',
            'Phase: Foundation', 'Phase: Development'
        ]
        
        # Get label IDs for the demonstration
        label_ids = [self.label_cache.get(label, '') for label in all_labels if label in self.label_cache]
        
        return self.trello_client.create_card(
            list_id=list_id,
            name="🏷️ TAG REFERENCE CARD - Administrative Model",
            desc=description,
            labels=label_ids
        )
    

    def _create_labels(self, board_id: str, sprint: Sprint):
        """Create necessary labels for the sprint"""
        label_colors = {
            # Priority labels
            'Priority: Critical': 'red',
            'Priority: High': 'orange',
            'Priority: Medium': 'yellow',
            'Priority: Low': 'green',
            
            # Frontend Technology labels
            'Frontend: React': 'blue',
            'Frontend: Vue.js': 'green',
            'Frontend: Angular': 'red',
            'Frontend: Svelte': 'orange',
            'Frontend: TypeScript': 'sky',
            'Frontend: JavaScript': 'yellow',
            'Frontend: CSS': 'pink',
            'Frontend: Sass/SCSS': 'purple',
            'Frontend: Less': 'blue',
            'Frontend: Styled Components': 'green',
            'Frontend: Tailwind CSS': 'sky',
            'Frontend: Bootstrap': 'purple',
            'Frontend: HTML': 'orange',
            'Frontend: Webpack': 'blue',
            'Frontend: Vite': 'green',
            'Frontend: Parcel': 'yellow',
            'Frontend: Redux': 'purple',
            'Frontend: MobX': 'pink',
            'Frontend: Zustand': 'sky',
            'Frontend: Context API': 'blue',
            
            # App Technology labels
            'App: Expo': 'blue',
            'App: React Native': 'sky',
            'App: Flutter': 'blue',
            'App: Ionic': 'green',
            'App: Xamarin': 'purple',
            'App: Cordova/PhoneGap': 'orange',
            'App: iOS': 'black',
            'App: Android': 'green',
            'App: Mobile': 'blue',
            'App: Xcode': 'black',
            'App: Android Studio': 'green',
            'App: Simulator/Emulator': 'sky',
            'App: App Store': 'blue',
            'App: TestFlight': 'purple',
            'App: Fastlane': 'orange',
            
            # Backend Technology labels
            'Backend: Firebase': 'purple',
            'Backend: Node.js': 'green',
            'Backend: Express.js': 'green',
            'Backend: Next.js': 'black',
            'Backend: Nuxt.js': 'green',
            'Backend: Python': 'green',
            'Backend: Django': 'green',
            'Backend: Flask': 'green',
            'Backend: FastAPI': 'green',
            'Backend: Java': 'red',
            'Backend: Spring': 'green',
            'Backend: C#': 'purple',
            'Backend: .NET': 'purple',
            'Backend: PHP': 'purple',
            'Backend: Laravel': 'red',
            'Backend: Symfony': 'black',
            'Backend: Ruby': 'red',
            'Backend: Ruby on Rails': 'red',
            'Backend: Go': 'blue',
            'Backend: Rust': 'orange',
            'Backend: Database': 'black',
            'Backend: MySQL': 'blue',
            'Backend: PostgreSQL': 'blue',
            'Backend: MongoDB': 'green',
            'Backend: Redis': 'red',
            'Backend: SQLite': 'blue',
            'Backend: AWS': 'orange',
            'Backend: Azure': 'blue',
            'Backend: Google Cloud': 'blue',
            'Backend: Heroku': 'purple',
            'Backend: Vercel': 'black',
            'Backend: Netlify': 'green',
            'Backend: REST API': 'sky',
            'Backend: GraphQL': 'pink',
            'Backend: gRPC': 'blue',
            'Backend: Microservices': 'purple',
            
            # DevOps Technology labels
            'DevOps: Git': 'black',
            'DevOps: GitHub': 'black',
            'DevOps: GitLab': 'orange',
            'DevOps: Bitbucket': 'blue',
            'DevOps: npm': 'red',
            'DevOps: Yarn': 'blue',
            'DevOps: pnpm': 'yellow',
            'DevOps: pip': 'green',
            'DevOps: Composer': 'purple',
            'DevOps: ESLint': 'yellow',
            'DevOps: Prettier': 'pink',
            'DevOps: Husky': 'purple',
            'DevOps: lint-staged': 'sky',
            'DevOps: CI/CD': 'green',
            'DevOps: GitHub Actions': 'black',
            'DevOps: Jenkins': 'red',
            'DevOps: Docker': 'blue',
            'DevOps: Kubernetes': 'blue',
            'DevOps: Analytics': 'purple',
            'DevOps: Monitoring': 'green',
            'DevOps: Crashlytics': 'orange',
            'DevOps: Sentry': 'red',
            
            # Testing Technology labels
            'Testing: Jest': 'green',
            'Testing: Cypress': 'green',
            'Testing: Playwright': 'green',
            'Testing: Selenium': 'green',
            'Testing: pytest': 'green',
            'Testing: Mocha': 'green',
            'Testing: Chai': 'green',
            
            # Category labels
            'Category: UI/UX': 'pink',
            'Category: Backend': 'black',
            'Category: Frontend': 'lime',
            'Category: Testing': 'green',
            'Category: DevOps': 'purple',
            'Category: Documentation': 'blue',
            
            # Task type labels
            'Type: Setup': 'yellow',
            'Type: Development': 'blue',
            'Type: Testing': 'green',
            'Type: Documentation': 'sky',
            'Type: Integration': 'purple',
            'Type: UI/UX': 'pink',
            'Type: Architecture': 'black',
            
            # Complexity labels
            'Complexity: Simple': 'green',
            'Complexity: Medium': 'yellow',
            'Complexity: Complex': 'orange',
            'Complexity: Very Complex': 'red',
            
            # Phase labels
            'Phase: Foundation': 'blue',
            'Phase: Development': 'green',
            'Phase: Testing': 'yellow',
            'Phase: Deployment': 'purple',
            'Phase: Maintenance': 'black'
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
{chr(10).join([f"• {clean_title(task.title)} ({task.estimated_time})" for task in milestone.tasks])}
        """.strip()
        
        # Determine milestone priority label
        priority_label = 'Priority: Medium'
        if 'crítica' in milestone.priority.lower() or 'critical' in milestone.priority.lower():
            priority_label = 'Priority: Critical'
        elif 'alta' in milestone.priority.lower() or 'high' in milestone.priority.lower():
            priority_label = 'Priority: High'
        
        return self.trello_client.create_card(
            list_id=list_id,
            name=f"🎯 {clean_title(milestone.title)}",
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
            name=f"📋 {clean_title(task.title)}",
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
