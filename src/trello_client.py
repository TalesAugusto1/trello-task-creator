"""
Trello API client for the Sprint Generator.
"""

import requests
from typing import Dict, List, Optional
from .models import TrelloConfig


class TrelloAPIError(Exception):
    """Trello API related errors"""
    pass


class TrelloClient:
    """Client for interacting with Trello API"""
    
    def __init__(self, config: TrelloConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Trello-Sprint-Generator/1.0.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a request to Trello API with proper error handling"""
        url = f"{self.config.base_url}/{endpoint}"
        params = kwargs.get('params', {})
        params.update({
            'key': self.config.api_key,
            'token': self.config.token
        })
        kwargs['params'] = params
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TrelloAPIError("Request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise TrelloAPIError("Connection error. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise TrelloAPIError("Authentication failed. Please check your API key and token.")
            elif e.response.status_code == 403:
                raise TrelloAPIError("Access forbidden. Please check your board permissions.")
            elif e.response.status_code == 404:
                raise TrelloAPIError("Resource not found. Please check your board ID.")
            else:
                raise TrelloAPIError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise TrelloAPIError(f"Request failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test the connection to Trello API"""
        try:
            self._make_request('GET', 'members/me')
            return True
        except TrelloAPIError:
            return False
    
    def get_board_lists(self, board_id: str) -> List[Dict]:
        """Get all lists for a board"""
        return self._make_request('GET', f'boards/{board_id}/lists')
    
    def get_board_info(self, board_id: str) -> Dict:
        """Get board information"""
        return self._make_request('GET', f'boards/{board_id}')
    
    def create_card(self, list_id: str, name: str, desc: str = "", 
                   labels: List[str] = None, due: str = None) -> Dict:
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
    
    def create_list(self, board_id: str, name: str) -> Dict:
        """Create a new list on a board"""
        data = {
            'idBoard': board_id,
            'name': name
        }
        return self._make_request('POST', 'lists', json=data)
