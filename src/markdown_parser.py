"""
Markdown parser for sprint files.
"""

import re
from typing import Dict, List
from .models import Sprint, Milestone, Task


class MarkdownParseError(Exception):
    """Markdown parsing related errors"""
    pass


class MarkdownParser:
    """Parses markdown sprint files into structured data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self._read_file()
    
    def _read_file(self) -> str:
        """Read the markdown file content with proper error handling"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if not content.strip():
                    raise MarkdownParseError(f"File is empty: {self.file_path}")
                return content
        except FileNotFoundError:
            raise MarkdownParseError(f"Sprint file not found: {self.file_path}")
        except UnicodeDecodeError:
            raise MarkdownParseError(f"File encoding error. Please ensure the file is UTF-8 encoded: {self.file_path}")
        except Exception as e:
            raise MarkdownParseError(f"Error reading file: {e}")
    
    def parse_sprint(self) -> Sprint:
        """Parse the markdown content into a Sprint object"""
        try:
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
        except Exception as e:
            raise MarkdownParseError(f"Failed to parse sprint: {e}")
    
    def _extract_sprint_title(self) -> str:
        """Extract sprint title from markdown"""
        title_match = re.search(r'# 🎯 \*\*(.+?)\*\*', self.content)
        if not title_match:
            raise MarkdownParseError("Sprint title not found. Expected format: # 🎯 **Title**")
        return title_match.group(1).strip()
    
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
        
        if not milestones:
            raise MarkdownParseError("No milestones found. Expected format: ## 🎯 **Milestone Title**")
        
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
        content_lower = task_content.lower()
        if 'crítica' in content_lower or 'critical' in content_lower:
            return 'High'
        elif 'alta' in content_lower or 'high' in content_lower:
            return 'High'
        elif 'baixa' in content_lower or 'low' in content_lower:
            return 'Low'
        else:
            return 'Medium'
    
    def _extract_task_labels(self, task_content: str) -> List[str]:
        """Extract optimized labels for the task with intelligent prioritization"""
        content_lower = task_content.lower()
        
        # Get all possible labels
        all_labels = []
        
        # Priority (always include)
        priority_label = self._get_priority_label(content_lower)
        all_labels.append(priority_label)
        
        # Task type (always include the most relevant one)
        task_type_label = self._get_primary_task_type(task_content, content_lower)
        if task_type_label:
            all_labels.append(task_type_label)
        
        # Technology (limit to 2-3 most important)
        tech_labels = self._get_priority_technologies(task_content, content_lower)
        all_labels.extend(tech_labels)
        
        # Complexity (only if not simple)
        complexity_label = self._get_complexity_label(task_content, content_lower)
        if complexity_label and 'Simple' not in complexity_label:
            all_labels.append(complexity_label)
        
        # Phase (only for foundation/development phases)
        phase_label = self._get_phase_label(task_content, content_lower)
        if phase_label and phase_label in ['Phase: Foundation', 'Phase: Development']:
            all_labels.append(phase_label)
        
        # Limit total labels to maximum 6 for better UI
        return all_labels[:6]
    
    def _get_priority_label(self, content_lower: str) -> str:
        """Get priority label"""
        if 'crítica' in content_lower or 'critical' in content_lower:
            return 'Priority: Critical'
        elif 'alta' in content_lower or 'high' in content_lower:
            return 'Priority: High'
        elif 'baixa' in content_lower or 'low' in content_lower:
            return 'Priority: Low'
        else:
            return 'Priority: Medium'
    
    def _get_primary_task_type(self, task_content: str, content_lower: str) -> str:
        """Get the most relevant task type (only one)"""
        # Priority order for task types
        if any(keyword in content_lower for keyword in ['configurar', 'configuração', 'setup', 'instalar', 'instalação', 'inicializar', 'inicialização']):
            return 'Type: Setup'
        elif any(keyword in content_lower for keyword in ['implementar', 'implementação', 'criar', 'desenvolver', 'desenvolvimento', 'código', 'programar']):
            return 'Type: Development'
        elif any(keyword in content_lower for keyword in ['testar', 'teste', 'testing', 'validar', 'verificar', 'debug']):
            return 'Type: Testing'
        elif any(keyword in content_lower for keyword in ['documentar', 'documentação', 'document', 'readme', 'guia', 'manual']):
            return 'Type: Documentation'
        elif any(keyword in content_lower for keyword in ['integrar', 'integração', 'conectar', 'conexão', 'api', 'serviço']):
            return 'Type: Integration'
        elif any(keyword in content_lower for keyword in ['interface', 'tela', 'componente', 'design', 'layout', 'visual', 'ui', 'ux']):
            return 'Type: UI/UX'
        elif any(keyword in content_lower for keyword in ['arquitetura', 'estrutura', 'padrão', 'pattern', 'organização']):
            return 'Type: Architecture'
        else:
            return 'Type: Development'  # Default
    
    def _get_priority_technologies(self, task_content: str, content_lower: str) -> List[str]:
        """Get 2-3 most important technology labels"""
        tech_labels = []
        
        # Priority 1: Main framework/platform
        if 'expo' in content_lower:
            tech_labels.append('App: Expo')
        elif 'react native' in content_lower:
            tech_labels.append('App: React Native')
        elif 'react' in content_lower and 'native' not in content_lower:
            tech_labels.append('Frontend: React')
        elif 'firebase' in content_lower:
            tech_labels.append('Backend: Firebase')
        elif 'node' in content_lower or 'nodejs' in content_lower:
            tech_labels.append('Backend: Node.js')
        
        # Priority 2: Key language
        if 'typescript' in content_lower or 'ts' in content_lower:
            tech_labels.append('Frontend: TypeScript')
        elif 'javascript' in content_lower or 'js' in content_lower:
            tech_labels.append('Frontend: JavaScript')
        elif 'python' in content_lower:
            tech_labels.append('Backend: Python')
        
        # Priority 3: Platform (only if mobile)
        if any(keyword in content_lower for keyword in ['ios', 'iphone', 'android', 'mobile', 'móvel']):
            if 'ios' in content_lower or 'iphone' in content_lower:
                tech_labels.append('App: iOS')
            elif 'android' in content_lower:
                tech_labels.append('App: Android')
            elif 'mobile' in content_lower or 'móvel' in content_lower:
                tech_labels.append('App: Mobile')
        
        # Limit to 3 technology labels
        return tech_labels[:3]
    
    def _get_complexity_label(self, task_content: str, content_lower: str) -> str:
        """Get complexity label only if not simple"""
        # Extract estimated time and determine complexity
        time_match = re.search(r'tempo estimado[:\s]*(\d+)\s*(hora|hour|dia|day|semana|week)', content_lower)
        if time_match:
            time_value = int(time_match.group(1))
            time_unit = time_match.group(2)
            
            # Convert to hours for comparison
            if 'dia' in time_unit or 'day' in time_unit:
                time_value *= 8  # Assume 8 hours per day
            elif 'semana' in time_unit or 'week' in time_unit:
                time_value *= 40  # Assume 40 hours per week
            
            if time_value <= 2:
                return 'Complexity: Simple'
            elif time_value <= 8:
                return 'Complexity: Medium'
            elif time_value <= 16:
                return 'Complexity: Complex'
            else:
                return 'Complexity: Very Complex'
        
        # Additional complexity indicators
        if any(keyword in content_lower for keyword in ['complexo', 'difícil', 'desafiador', 'complex', 'challenging']):
            return 'Complexity: Complex'
        
        return None
    
    def _get_phase_label(self, task_content: str, content_lower: str) -> str:
        """Get phase label only for foundation/development"""
        if any(keyword in content_lower for keyword in ['inicialização', 'setup', 'configuração', 'primeira', 'foundation']):
            return 'Phase: Foundation'
        elif any(keyword in content_lower for keyword in ['desenvolvimento', 'implementação', 'core', 'principal']):
            return 'Phase: Development'
        else:
            return None
    
    
    
    
    
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
