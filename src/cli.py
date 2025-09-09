"""
Command-line interface for the Trello Sprint Generator.
"""

import argparse
import sys
from typing import Optional
from .config import ConfigManager, ConfigError
from .trello_client import TrelloClient, TrelloAPIError
from .markdown_parser import MarkdownParser, MarkdownParseError
from .sprint_generator import SprintGenerator, SprintGeneratorError


class CLI:
    """Command-line interface for the Trello Sprint Generator"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description='Generate Trello cards from sprint markdown files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --file sprint1.md --board-id YOUR_BOARD_ID
  %(prog)s --file sprint1.md --board-id YOUR_BOARD_ID --list-name "Backlog"
  %(prog)s --file sprint1.md --board-id YOUR_BOARD_ID --dry-run
  %(prog)s --test-connection
            """
        )
        
        parser.add_argument(
            '--file', '-f',
            help='Path to the sprint markdown file'
        )
        parser.add_argument(
            '--board-id', '-b',
            help='Trello board ID'
        )
        parser.add_argument(
            '--list-name', '-l',
            default='Backlog',
            help='Target list name (default: Backlog)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and display results without creating cards'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test connection to Trello API'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments"""
        try:
            parsed_args = self.parser.parse_args(args)
            
            # Handle test connection
            if parsed_args.test_connection:
                return self._test_connection(parsed_args.verbose)
            
            # Validate required arguments for main operation
            if not parsed_args.file:
                self.parser.error("--file is required for card generation")
            if not parsed_args.board_id:
                self.parser.error("--board-id is required for card generation")
            
            return self._generate_cards(parsed_args)
            
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _test_connection(self, verbose: bool) -> int:
        """Test connection to Trello API"""
        try:
            print("🔍 Testing connection to Trello API...")
            
            config = ConfigManager.load_config()
            client = TrelloClient(config)
            
            if client.test_connection():
                print("✅ Connection successful!")
                if verbose:
                    print(f"   API Key: {config.api_key[:8]}...")
                    print(f"   Token: {config.token[:8]}...")
                return 0
            else:
                print("❌ Connection failed!")
                return 1
                
        except ConfigError as e:
            print(f"❌ Configuration error: {e}")
            return 1
        except TrelloAPIError as e:
            print(f"❌ Trello API error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1
    
    def _generate_cards(self, args) -> int:
        """Generate Trello cards from sprint file"""
        try:
            # Load configuration
            config = ConfigManager.load_config()
            client = TrelloClient(config)
            
            # Parse sprint file
            parser = MarkdownParser(args.file)
            sprint = parser.parse_sprint()
            
            print(f"📋 Parsed Sprint: {sprint.title}")
            print(f"🎯 Milestones: {sprint.get_total_milestones()}")
            print(f"📝 Total Tasks: {sprint.get_total_tasks()}")
            
            if args.dry_run:
                return self._show_dry_run_results(sprint)
            
            # Generate cards
            generator = SprintGenerator(client)
            result = generator.generate_cards(sprint, args.board_id, args.list_name)
            
            print(f"\n✅ Successfully created:")
            print(f"  🏷️  Tag reference card: {result['tag_reference_card']['name']}")
            print(f"  📋 Sprint card: {result['sprint_card']['name']}")
            print(f"  🎯 Milestone cards: {len(result['milestone_cards'])}")
            print(f"  📝 Task cards: {len(result['task_cards'])}")
            print(f"  🏷️  Labels created: {len(result['created_labels'])}")
            
            return 0
            
        except ConfigError as e:
            print(f"❌ Configuration error: {e}")
            return 1
        except MarkdownParseError as e:
            print(f"❌ Markdown parsing error: {e}")
            return 1
        except TrelloAPIError as e:
            print(f"❌ Trello API error: {e}")
            return 1
        except SprintGeneratorError as e:
            print(f"❌ Sprint generation error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _show_dry_run_results(self, sprint) -> int:
        """Show dry run results"""
        print("\n🔍 Dry run - no cards will be created")
        print(f"Sprint: {sprint.title}")
        
        for milestone in sprint.milestones:
            print(f"  Milestone: {milestone.title} ({len(milestone.tasks)} tasks)")
            for task in milestone.tasks:
                print(f"    Task: {task.title}")
        
        return 0


def main():
    """Main entry point for the CLI"""
    cli = CLI()
    sys.exit(cli.run())
