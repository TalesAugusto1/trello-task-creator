"""
Data models for the Trello Sprint Generator.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TrelloConfig:
    """Configuration for Trello API"""
    api_key: str
    token: str
    base_url: str = "https://api.trello.com/1"
    
    def validate(self) -> bool:
        """Validate the configuration"""
        if not self.api_key or not self.token:
            return False
        if len(self.api_key) < 10 or len(self.token) < 10:
            return False
        return True


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
    labels: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
    
    def get_total_criteria_count(self) -> int:
        """Get total number of acceptance criteria"""
        return len(self.acceptance_criteria)
    
    def get_completion_percentage(self, completed_criteria: int) -> float:
        """Calculate completion percentage based on criteria"""
        if not self.acceptance_criteria:
            return 0.0
        return (completed_criteria / len(self.acceptance_criteria)) * 100


@dataclass
class Milestone:
    """Represents a milestone from the markdown file"""
    title: str
    duration: str
    priority: str
    dependencies: str
    tasks: List[Task]
    
    def get_total_tasks(self) -> int:
        """Get total number of tasks in this milestone"""
        return len(self.tasks)
    
    def get_total_estimated_time(self) -> str:
        """Get total estimated time for all tasks"""
        # This is a simplified calculation - in a real scenario you'd parse the time strings
        return f"{len(self.tasks)} tasks"


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
    
    def get_total_tasks(self) -> int:
        """Get total number of tasks across all milestones"""
        return sum(milestone.get_total_tasks() for milestone in self.milestones)
    
    def get_total_milestones(self) -> int:
        """Get total number of milestones"""
        return len(self.milestones)
    
    def get_milestone_by_title(self, title: str) -> Optional[Milestone]:
        """Find a milestone by its title"""
        for milestone in self.milestones:
            if milestone.title == title:
                return milestone
        return None
