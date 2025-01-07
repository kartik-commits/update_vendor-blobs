#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

@dataclass
class Section:
    header: str
    content: List[str]

class ProprietaryFileDeduplicator:
    def __init__(self, common_file: str, device_file: str, 
                 dry_run: bool = False, verbose: bool = False):
        self.common_file = Path(common_file)
        self.device_file = Path(device_file)
        self.dry_run = dry_run
        self.verbose = verbose
        self.common_entries: Set[str] = set()
        self.source_line: str = None

    def log(self, message: str, is_verbose: bool = False):
        """Print colored log messages."""
        if not is_verbose or (is_verbose and self.verbose):
            print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message}")

    def validate_files(self):
        """Validate input files existence and permissions."""
        for file_path in [self.common_file, self.device_file]:
            if not file_path.exists():
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} File not found: {file_path}")
                sys.exit(1)
            if not file_path.is_file():
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Not a file: {file_path}")
                sys.exit(1)

    def parse_file(self, file_path: Path) -> List[Section]:
        """Parse file into sections with their content."""
        sections: List[Section] = []
        current_section: Section = None
        
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Handle source line if present
        if lines and "extracted from" in lines[0]:
            self.source_line = lines[0]
            lines = lines[1:]

        for line in lines:
            line = line.rstrip()
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                current_section = Section(header=line, content=[])
            elif current_section is not None and line.strip():
                current_section.content.append(line)

        if current_section and (current_section.content or current_section.header):
            sections.append(current_section)

        return sections

    def load_common_entries(self):
        """Load all entries from common file into a set."""
        sections = self.parse_file(self.common_file)
        for section in sections:
            for line in section.content:
                # Strip any inline comments and whitespace
                entry = line.split('#')[0].strip()
                if entry:
                    self.common_entries.add(entry)
        
        self.log(f"Loaded {len(self.common_entries)} entries from common file", True)

    def process_device_file(self) -> str:
        """Process device file and remove duplicates."""
        sections = self.parse_file(self.device_file)
        output_lines = []
        removed_count = 0
        
        # Add source line if present
        if self.source_line:
            output_lines.append(self.source_line.rstrip())
            output_lines.append('')

        for section in sections:
            if section.content:  # Only process non-empty sections
                output_lines.append(section.header)
                filtered_content = []
                
                for line in section.content:
                    # Split line into content and comment
                    parts = line.split('#', 1)
                    entry = parts[0].strip()
                    
                    if entry in self.common_entries:
                        removed_count += 1
                        self.log(f"Removing duplicate: {line}", True)
                    else:
                        filtered_content.append(line)
                
                if filtered_content:
                    output_lines.extend(filtered_content)
                    output_lines.append('')
                else:
                    output_lines.pop()  # Remove section header if no content left

        # Remove trailing empty lines
        while output_lines and not output_lines[-1]:
            output_lines.pop()

        self.log(f"Found {removed_count} duplicates to remove")
        return '\n'.join(output_lines) + '\n'

    def show_diff(self, new_content: str):
        """Show differences between original and new content."""
        with open(self.device_file, 'r') as f:
            old_content = f.read()

        print(f"\n{Fore.CYAN}Changes to be made:{Style.RESET_ALL}")
        for line in old_content.splitlines():
            line_content = line.split('#')[0].strip()
            if line_content in self.common_entries:
                print(f"{Fore.RED}- {line}{Style.RESET_ALL}")

    def deduplicate(self):
        """Main deduplication process."""
        self.validate_files()
        self.load_common_entries()
        
        new_content = self.process_device_file()
        
        if self.dry_run:
            self.show_diff(new_content)
            self.log("Dry run - no changes made")
        else:
            with open(self.device_file, 'w') as f:
                f.write(new_content)
            self.log("Successfully removed duplicates")

def main():
    parser = argparse.ArgumentParser(
        description="Remove entries from device proprietary files that exist in common file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s common.txt device.txt          # Process files
  %(prog)s -d common.txt device.txt       # Dry run to preview changes
  %(prog)s -v common.txt device.txt       # Verbose output
        """
    )
    
    parser.add_argument('common_file',
                      help='Common proprietary files list')
    parser.add_argument('device_file',
                      help='Device-specific proprietary files list')
    parser.add_argument('-d', '--dry-run', action='store_true',
                      help='Show what would be done without making changes')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose output')

    args = parser.parse_args()

    deduplicator = ProprietaryFileDeduplicator(
        args.common_file,
        args.device_file,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    deduplicator.deduplicate()

if __name__ == '__main__':
    main()
