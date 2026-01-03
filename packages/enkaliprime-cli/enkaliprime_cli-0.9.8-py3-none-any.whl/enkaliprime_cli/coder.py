"""
Coding Assistant Mode for EnkaliPrime CLI.

Provides specialized coding assistance with project planning, file operations,
and implementation tracking.
"""

import os
import json
import typer
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from typing import Optional, Dict, Any, List
import keyring

from .ui import console, Header, cyber_panel, print_success, print_error, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT
from .commands.chat import provider_manager, SERVICE_NAME, create_client, OllamaCloudProvider

class ImplementationPlan:
    """Represents a structured implementation plan for a coding project."""

    def __init__(self, title: str, description: str, tasks: List[Dict[str, Any]]):
        self.title = title
        self.description = description
        self.tasks = tasks
        self.current_task_index = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "tasks": self.tasks,
            "current_task_index": self.current_task_index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImplementationPlan':
        plan = cls(data["title"], data["description"], data["tasks"])
        plan.current_task_index = data.get("current_task_index", 0)
        return plan

    def get_current_task(self) -> Optional[Dict[str, Any]]:
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def mark_task_complete(self) -> bool:
        """Mark current task as complete and move to next."""
        if self.current_task_index < len(self.tasks):
            self.tasks[self.current_task_index]["completed"] = True
            self.current_task_index += 1
            return True
        return False

    def get_progress_percentage(self) -> float:
        """Get completion percentage."""
        if not self.tasks:
            return 100.0
        completed = sum(1 for task in self.tasks if task.get("completed", False))
        return (completed / len(self.tasks)) * 100

class FileSystemManager:
    """Safe file system operations for the coding assistant."""

    def __init__(self, base_directory: str = "."):
        self.base_directory = Path(base_directory).resolve()
        self.ensure_base_directory()

    def ensure_base_directory(self):
        """Ensure base directory exists."""
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def create_directory(self, path: str) -> bool:
        """Create a directory safely."""
        try:
            full_path = (self.base_directory / path).resolve()
            # Ensure it's within our base directory for safety
            if not str(full_path).startswith(str(self.base_directory)):
                print_error("Cannot create directory outside project scope")
                return False

            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {path}")
            return True
        except Exception as e:
            print_error(f"Failed to create directory {path}: {e}")
            return False

    def write_file(self, path: str, content: str, overwrite: bool = False) -> bool:
        """Write content to a file safely."""
        try:
            full_path = (self.base_directory / path).resolve()

            # Ensure it's within our base directory for safety
            if not str(full_path).startswith(str(self.base_directory)):
                print_error("Cannot write file outside project scope")
                return False

            if full_path.exists() and not overwrite:
                if not Confirm.ask(f"File {path} already exists. Overwrite?"):
                    return False

            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            print_success(f"Wrote {len(content)} characters to: {path}")
            return True
        except Exception as e:
            print_error(f"Failed to write file {path}: {e}")
            return False

    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file."""
        try:
            full_path = (self.base_directory / path).resolve()

            # Ensure it's within our base directory for safety
            if not str(full_path).startswith(str(self.base_directory)):
                print_error("Cannot read file outside project scope")
                return None

            if not full_path.exists():
                print_error(f"File {path} does not exist")
                return None

            content = full_path.read_text(encoding='utf-8')
            print_success(f"Read {len(content)} characters from: {path}")
            return content
        except Exception as e:
            print_error(f"Failed to read file {path}: {e}")
            return None

    def list_directory(self, path: str = ".") -> List[str]:
        """List contents of a directory."""
        try:
            full_path = (self.base_directory / path).resolve()

            # Ensure it's within our base directory for safety
            if not str(full_path).startswith(str(self.base_directory)):
                print_error("Cannot list directory outside project scope")
                return []

            if not full_path.exists():
                print_error(f"Directory {path} does not exist")
                return []

            items = []
            for item in full_path.iterdir():
                relative_path = item.relative_to(self.base_directory)
                items.append(str(relative_path))

            return sorted(items)
        except Exception as e:
            print_error(f"Failed to list directory {path}: {e}")
            return []

class CodingAssistant:
    """Main coding assistant interface."""

    def __init__(self, agent_name: str = "Code Assistant", provider: str = "auto",
                 model: str = None, local: bool = False, cloud: bool = False):
        self.agent_name = agent_name
        self.provider = provider
        self.model = model
        self.local = local
        self.cloud = cloud

        # Initialize components
        self.client = self._create_client()
        self.fs_manager = FileSystemManager()
        self.current_plan: Optional[ImplementationPlan] = None
        self.session_active = False

    def _create_client(self):
        """Create AI client for coding tasks."""
        # Apply coding-specific system prompt
        system_prompt = """
        You are an expert coding assistant. Your role is to help users build software projects by:

        1. Creating detailed implementation plans when asked
        2. Writing clean, well-documented code
        3. Following best practices and modern conventions
        4. Explaining your reasoning and approach
        5. Providing alternative solutions when appropriate

        When creating implementation plans, structure them as JSON with:
        - title: Project title
        - description: Brief overview
        - tasks: Array of task objects with 'title', 'description', 'files' (array of file paths), and 'dependencies' (optional)

        Always consider security, performance, and maintainability in your suggestions.
        """

        # Set the preferred provider based on our parameters
        if self.cloud:
            cloud_api_key = keyring.get_password(SERVICE_NAME, "ollama_cloud_api_key")
            if not cloud_api_key:
                raise Exception("Ollama cloud API key not configured")
            provider_manager.set_preferred_provider("cloud")
            provider_manager.providers['cloud'] = OllamaCloudProvider(cloud_api_key)
        elif self.local:
            provider_manager.set_preferred_provider("ollama")
        else:
            provider_manager.set_preferred_provider("remote")

        # Get the client
        client = provider_manager.get_client()

        # Store system prompt for use with all client types
        self._system_prompt = system_prompt

        # Apply coding system prompt if the client supports it
        if hasattr(client, 'set_system_prompt'):
            client.set_system_prompt(system_prompt)

        return client

    def send_coding_message(self, message: str, **kwargs) -> str:
        """Send a message using the appropriate client method."""
        if hasattr(self.client, 'send_message'):
            # EnkaliPrime client
            return self.client.send_message(message=message, session_id="coder", loading=False, **kwargs)
        elif hasattr(self.client, 'generate'):
            # Ollama providers (local or cloud)
            # Get the system prompt that was set during client creation
            system_prompt = getattr(self, '_system_prompt', None)
            return self.client.generate(
                prompt=message,
                system_prompt=system_prompt,
                **kwargs
            )
        else:
            raise Exception(f"Unsupported client type: {type(self.client)}")

    def start_session(self):
        """Start a coding assistant session."""
        console.clear()
        Header.draw(agent_name=self.agent_name)

        # Display coder mode information
        console.print(cyber_panel(
            f"🤖 [bold {COLOR_ACCENT}]Coding Assistant Mode Activated[/]\n\n"
            "🎯 [bold]Capabilities:[/]\n"
            "• Create detailed implementation plans\n"
            "• Generate and manage project files\n"
            "• Interactive progress tracking\n"
            "• Safe file system operations\n"
            "• AI-powered code generation\n\n"
            "💡 [bold]Commands:[/]\n"
            "• '<description>' - Just type what you want to build!\n"
            "• 'plan <description>' - Create detailed implementation plan\n"
            "• 'implement' - Execute current plan\n"
            "• 'create <file>' - Create/edit a specific file\n"
            "• 'read <file>' - Read file contents\n"
            "• 'list [dir]' - List directory contents\n"
            "• 'status' - Show current progress\n"
            "• 'help' - Show this help\n"
            "• 'exit' - End session",
            title="🎨 Coding Assistant",
            style=COLOR_SECONDARY
        ))

        self.session_active = True
        console.print(f"\n[dim]Working directory: {os.getcwd()}[/]")
        console.print(f"\n[dim]🚀 Just type what you want to build! (e.g., 'a website for selling cows')[/]")
        console.print(f"\n[dim]Type 'exit', 'quit', or 'q' to end the conversation.[/]")
        console.print()

    def process_command(self, command: str) -> bool:
        """Process a coding assistant command."""
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "exit" or cmd == "quit" or cmd == "q":
            return False
        elif cmd == "help" or cmd == "h":
            self.show_help()
        elif cmd == "plan":
            self.create_plan(" ".join(args))
        elif cmd == "implement":
            self.implement_plan()
        elif cmd == "create":
            if args:
                # Check if args look like a filename or a description
                arg_text = " ".join(args)
                if self._looks_like_filename(arg_text):
                    self.create_file(arg_text)
                else:
                    # Treat as code generation request
                    self.generate_code_for_description(arg_text)
            else:
                print_error("Usage: create <filename> or just describe what you want to create")
        elif cmd == "read":
            if args:
                self.read_file(" ".join(args))
            else:
                print_error("Usage: read <filename>")
        elif cmd == "list":
            path = " ".join(args) if args else "."
            self.list_directory(path)
        elif cmd == "status":
            self.show_status()
        else:
            # Check if the entire command looks like a filename
            if self._looks_like_filename(command.strip()):
                self.create_file(command.strip())
            else:
                # Treat as code generation request
                self.generate_code_for_description(command.strip())

        return True

    def show_help(self):
        """Show help information."""
        help_panel = Panel(
            "[bold]Available Commands:[/]\n\n"
            "🚀 [cyan]<description>[/] - Just type what you want to build! (e.g., 'a website for selling cows')\n"
            "🎯 [cyan]plan <description>[/] - Create a detailed implementation plan\n"
            "⚡ [cyan]implement[/] - Execute the current implementation plan\n"
            "📝 [cyan]create <file>[/] - Create or edit a specific file\n"
            "📖 [cyan]read <file>[/] - Read and display file contents\n"
            "📁 [cyan]list [directory][/]- List directory contents\n"
            "📊 [cyan]status[/] - Show current progress and plan status\n"
            "💬 [cyan]<message>[/] - Chat with AI assistant\n"
            "❌ [cyan]exit[/] - End coding session",
            title="🆘 Help - Coding Assistant Commands",
            border_style=COLOR_ACCENT,
            box=box.DOUBLE
        )
        console.print(help_panel)

    def create_plan(self, description: str):
        """Create an implementation plan for a project."""
        if not description:
            print_error("Please provide a project description")
            return

        console.print(f"\n[bold {COLOR_PRIMARY}]🎯 Creating Implementation Plan[/]")
        console.print(f"[dim]Project: {description}[/]")

        # Ask AI to create implementation plan
        plan_prompt = f"""
        Create a detailed implementation plan for the following project:

        {description}

        Return the plan as a JSON object with this exact structure:
        {{
            "title": "Project Title",
            "description": "Brief project description",
            "tasks": [
                {{
                    "title": "Task Title",
                    "description": "Detailed task description",
                    "files": ["file1.py", "file2.py"],
                    "dependencies": ["optional", "task", "names"],
                    "priority": "high|medium|low"
                }}
            ]
        }}

        Make the plan comprehensive but achievable. Include file paths, dependencies, and clear descriptions.
        """

        try:
            response = self.send_coding_message(plan_prompt)

            # Try to extract JSON from response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                json_str = json_match.group(1) if json_match else response

            try:
                plan_data = json.loads(json_str)
                self.current_plan = ImplementationPlan.from_dict(plan_data)
                self.show_plan_approval()
            except json.JSONDecodeError:
                print_error("Failed to parse plan JSON. AI response may be malformed.")
                console.print(Markdown(response))

        except Exception as e:
            print_error(f"Failed to create plan: {str(e)}")

    def show_plan_approval(self):
        """Show the implementation plan and ask for approval."""
        if not self.current_plan:
            return

        console.print(f"\n[bold {COLOR_PRIMARY}]📋 Implementation Plan Review[/]")

        # Plan overview
        console.print(cyber_panel(
            f"**Title:** {self.current_plan.title}\n\n"
            f"**Description:** {self.current_plan.description}\n\n"
            f"**Tasks:** {len(self.current_plan.tasks)} total",
            title="📋 Plan Overview",
            style=COLOR_SECONDARY
        ))

        # Tasks table
        table = Table(title="🎯 Implementation Tasks", box=box.ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("Task", style=f"bold {COLOR_ACCENT}")
        table.add_column("Files", style="cyan")
        table.add_column("Priority", style="yellow", width=8)

        for i, task in enumerate(self.current_plan.tasks, 1):
            files = ", ".join(task.get("files", []))
            priority = task.get("priority", "medium")
            table.add_row(
                str(i),
                task["title"],
                files[:50] + "..." if len(files) > 50 else files,
                priority
            )

        console.print(table)
        console.print()

        # Ask for approval
        if Confirm.ask(f"\n[bold {COLOR_ACCENT}]Do you approve this implementation plan?[/]"):
            print_success("✅ Plan approved! Use 'implement' to start execution.")
        else:
            self.current_plan = None
            console.print("[yellow]Plan discarded. Create a new plan with 'plan <description>'[/]")

    def implement_plan(self):
        """Execute the current implementation plan."""
        if not self.current_plan:
            print_error("No active implementation plan. Create one with 'plan <description>'")
            return

        console.print(f"\n[bold {COLOR_PRIMARY}]⚡ Starting Implementation[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            main_task = progress.add_task("Implementing plan...", total=len(self.current_plan.tasks))

            for i, task in enumerate(self.current_plan.tasks):
                if task.get("completed", False):
                    progress.update(main_task, advance=1)
                    continue

                progress.update(main_task, description=f"Working on: {task['title']}")

                # Show task details
                console.print(f"\n[bold {COLOR_ACCENT}]Task {i+1}/{len(self.current_plan.tasks)}: {task['title']}[/]")
                console.print(f"[dim]{task['description']}[/]")

                # Generate code for files in this task
                files = task.get("files", [])
                if files:
                    for file_path in files:
                        self.generate_file_for_task(file_path, task)

                # Mark task complete
                self.current_plan.mark_task_complete()
                progress.update(main_task, advance=1)

        print_success("🎉 Implementation complete!")
        self.show_status()

    def generate_file_for_task(self, file_path: str, task: Dict[str, Any]):
        """Generate code for a specific file in a task."""
        console.print(f"\n[bold {COLOR_SECONDARY}]Generating: {file_path}[/]")

        # Ask AI to generate the file content
        file_prompt = f"""
        Generate the complete code for file: {file_path}

        Task: {task['title']}
        Description: {task['description']}

        Project: {self.current_plan.title}
        Project Description: {self.current_plan.description}

        Create production-ready code with proper documentation, error handling, and following best practices.
        Include necessary imports and comments.
        """

        try:
            response = self.send_coding_message(file_prompt)

            # Extract code from response
            import re
            code_match = re.search(r'```(?:\w+)?\s*(.*?)\s*```', response, re.DOTALL)
            if code_match:
                code_content = code_match.group(1).strip()
                if self.fs_manager.write_file(file_path, code_content):
                    print_success(f"✓ Generated {file_path}")
                else:
                    print_error(f"✗ Failed to write {file_path}")
            else:
                print_error(f"No code found in AI response for {file_path}")
                console.print(Markdown(response))

        except Exception as e:
            print_error(f"Failed to generate {file_path}: {str(e)}")

    def create_file(self, file_path: str):
        """Create or edit a file interactively."""
        console.print(f"\n[bold {COLOR_ACCENT}]📝 File Editor: {file_path}[/]")

        # Check if file exists
        existing_content = self.fs_manager.read_file(file_path)
        if existing_content is not None:
            console.print(f"[dim]Existing content ({len(existing_content)} chars)[/]")
            if not Confirm.ask("Edit existing file?"):
                return

        # Get user input for file content
        console.print("Enter file content (press Ctrl+D or type 'END' on a new line to finish):")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            pass

        content = "\n".join(lines)
        if self.fs_manager.write_file(file_path, content, overwrite=True):
            print_success(f"File {file_path} saved successfully!")

    def read_file(self, file_path: str):
        """Read and display file contents."""
        content = self.fs_manager.read_file(file_path)
        if content is not None:
            console.print(f"\n[bold {COLOR_ACCENT}]📖 {file_path}[/]")
            console.print(Panel(content, box=box.ROUNDED, border_style=COLOR_SECONDARY))

    def list_directory(self, path: str = "."):
        """List directory contents."""
        items = self.fs_manager.list_directory(path)

        if not items:
            console.print(f"[dim]Directory {path} is empty or doesn't exist[/]")
            return

        table = Table(title=f"📁 Directory: {path}", box=box.ROUNDED)
        table.add_column("Type", style="bold", width=6)
        table.add_column("Name", style=f"bold {COLOR_ACCENT}")

        for item in items:
            item_path = Path(path) / item
            full_path = self.fs_manager.base_directory / item_path
            if full_path.is_dir():
                table.add_row("📁 DIR", item)
            else:
                table.add_row("📄 FILE", item)

        console.print(table)

    def show_status(self):
        """Show current progress and plan status."""
        if not self.current_plan:
            console.print("[yellow]No active implementation plan.[/]")
            console.print("Create one with: [cyan]plan <description>[/]")
            return

        progress_pct = self.current_plan.get_progress_percentage()

        # Progress bar
        console.print(f"\n[bold {COLOR_PRIMARY}]📊 Implementation Status[/]")

        status_panel = Panel(
            f"**Project:** {self.current_plan.title}\n\n"
            f"**Progress:** {progress_pct:.1f}%\n\n"
            f"**Tasks:** {sum(1 for t in self.current_plan.tasks if t.get('completed'))}/{len(self.current_plan.tasks)} completed",
            title="📈 Current Status",
            border_style=COLOR_ACCENT,
            box=box.DOUBLE
        )
        console.print(status_panel)

        # Current task
        current_task = self.current_plan.get_current_task()
        if current_task:
            console.print(f"\n[bold {COLOR_SECONDARY}]🎯 Next Task:[/] {current_task['title']}")
            console.print(f"[dim]{current_task['description']}[/]")
        else:
            console.print(f"\n[green]🎉 All tasks completed![/]")

    def chat_with_ai(self, message: str):
        """Chat with AI assistant."""
        try:
            response = self.send_coding_message(message)

            console.print(cyber_panel(
                Markdown(response),
                title=self.agent_name,
                style=COLOR_SECONDARY
            ))

            # Process any code blocks for clipboard
            from .code_utils import process_ai_response
            process_ai_response(response)

        except Exception as e:
            print_error(f"Chat failed: {str(e)}")

    def _looks_like_filename(self, text: str) -> bool:
        """Check if text looks like a filename (has extension or is a simple name)."""
        text = text.strip()
        # Check for file extensions
        if any(text.endswith(ext) for ext in ['.py', '.js', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml']):
            return True
        # Check if it's a simple filename without spaces
        if ' ' not in text and len(text) > 0 and text[0] not in ['.', '/', '\\']:
            return True
        return False

    def generate_code_for_description(self, description: str):
        """Generate code based on a description."""
        console.print(f"\n[bold {COLOR_ACCENT}]🎯 Generating code for:[/] {description}")

        # Ask AI to generate code based on the description
        code_prompt = f"""
        Generate complete, working code for: {description}

        Create a modern, production-ready implementation with multiple files.
        Format your response clearly with file sections like this:

        ## index.html
        ```html
        <!DOCTYPE html>
        <html>
        <!-- complete HTML code here -->
        </html>
        ```

        ## styles.css
        ```css
        /* complete CSS styles here */
        ```

        ## script.js
        ```javascript
        // complete JavaScript code here
        ```

        Include ALL necessary files, proper structure, and make it immediately runnable.
        Focus on creating a complete, working solution.
        """

        try:
            response = self.send_coding_message(code_prompt)

            console.print(f"\n[bold {COLOR_SECONDARY}]🤖 AI Generated Code:[/]")
            console.print(Markdown(response))

            # Process any code blocks for clipboard
            from .code_utils import process_ai_response
            process_ai_response(response)

            # Try to extract and save files automatically
            self._extract_and_save_files_from_response(response, description)

        except Exception as e:
            print_error(f"Failed to generate code: {str(e)}")

    def _extract_and_save_files_from_response(self, response: str, description: str):
        """Extract file code blocks from AI response and save them automatically."""
        import re

        saved_files = []

        # First, look for structured file headers like "## filename.ext"
        file_pattern = r'##\s*([^\n]+)\n.*?```(\w+)?\n(.*?)\n```'
        matches = re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE)

        if matches:
            console.print(f"\n[bold {COLOR_ACCENT}]📁 Creating {len(matches)} file(s) automatically:[/]")

            for filename, language, code in matches:
                filename = filename.strip()
                if self.fs_manager.write_file(filename, code.strip()):
                    print_success(f"✓ Created {filename}")
                    saved_files.append(filename)
                else:
                    print_error(f"✗ Failed to create {filename}")

        # If no structured files found, look for any code blocks and create appropriate files
        if not saved_files:
            # Look for any code blocks
            code_block_pattern = r'```(\w+)?\n(.*?)\n```'
            code_blocks = re.findall(code_block_pattern, response, re.DOTALL)

            if code_blocks:
                console.print(f"\n[bold {COLOR_ACCENT}]🔧 Found {len(code_blocks)} code block(s), creating files automatically:[/]")

                # Generate appropriate filenames based on description and code types
                base_name = self._generate_base_filename(description)

                for i, (language, code) in enumerate(code_blocks):
                    if language:
                        # Use language to determine extension
                        ext = self._get_extension_for_language(language)
                        if len(code_blocks) > 1:
                            filename = f"{base_name}_{i+1}.{ext}"
                        else:
                            filename = f"{base_name}.{ext}"
                    else:
                        # Generic code file
                        if len(code_blocks) > 1:
                            filename = f"{base_name}_{i+1}.txt"
                        else:
                            filename = f"{base_name}.txt"

                    if self.fs_manager.write_file(filename, code.strip()):
                        print_success(f"✓ Created {filename}")
                        saved_files.append(filename)
                    else:
                        print_error(f"✗ Failed to create {filename}")

        if saved_files:
            console.print(f"\n[bold {COLOR_ACCENT}]🎉 Successfully created {len(saved_files)} file(s)![/]")
            console.print(f"[dim]Files: {', '.join(saved_files)}[/]")

            # Try to identify main file and suggest how to run
            main_file = self._identify_main_file(saved_files)
            if main_file:
                console.print(f"\n[dim]💡 Main file: {main_file}[/]")
                if main_file.endswith('.html'):
                    console.print(f"[dim]🌐 Open {main_file} in your web browser to see the result![/]")
                elif main_file.endswith('.py'):
                    console.print(f"[dim]🐍 Run with: python {main_file}[/]")
                elif main_file.endswith('.js'):
                    console.print(f"[dim]📜 Run with: node {main_file}[/]")
        else:
            console.print(f"\n[bold {COLOR_ACCENT}]💡 No code blocks found to save as files.[/]")
            console.print("[dim]The AI response may not contain executable code, or you can try rephrasing your request.[/]")

    def _generate_base_filename(self, description: str) -> str:
        """Generate a base filename from description."""
        # Clean the description and create a filename
        import re
        # Remove common words and punctuation
        clean_desc = re.sub(r'[^\w\s-]', '', description.lower())
        words = clean_desc.split()[:3]  # Take first 3 words
        return '_'.join(words) if words else 'project'

    def _get_extension_for_language(self, language: str) -> str:
        """Get appropriate file extension for a programming language."""
        extensions = {
            'html': 'html',
            'css': 'css',
            'javascript': 'js',
            'js': 'js',
            'python': 'py',
            'py': 'py',
            'json': 'json',
            'xml': 'xml',
            'markdown': 'md',
            'md': 'md',
            'yaml': 'yml',
            'yml': 'yml',
            'bash': 'sh',
            'shell': 'sh',
            'sql': 'sql',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'c': 'c',
            'php': 'php',
            'ruby': 'rb',
            'rb': 'rb',
            'go': 'go',
            'rust': 'rs',
            'typescript': 'ts',
            'ts': 'ts',
            'r': 'r',
            'swift': 'swift',
            'kotlin': 'kt',
            'scala': 'scala',
            'dart': 'dart',
            'lua': 'lua',
            'perl': 'pl',
            'haskell': 'hs'
        }
        return extensions.get(language.lower(), 'txt')

    def _identify_main_file(self, files: list) -> str:
        """Identify the main/entry file from a list of files."""
        # Priority order for main files
        main_patterns = [
            r'^index\.html$',
            r'^main\.py$',
            r'^app\.py$',
            r'^server\.py$',
            r'^index\.js$',
            r'^main\.js$',
            r'^app\.js$',
            r'^script\.js$'
        ]

        for pattern in main_patterns:
            import re
            for file in files:
                if re.match(pattern, file, re.IGNORECASE):
                    return file

        # If no standard main file, return the first HTML file, then first Python, then first JS
        for file in files:
            if file.endswith('.html'):
                return file
        for file in files:
            if file.endswith('.py'):
                return file
        for file in files:
            if file.endswith('.js'):
                return file

        # Return first file as fallback
        return files[0] if files else None

def start_coder_mode(agent_name: str = "Code Assistant", provider: str = "auto",
                    model: str = None, local: bool = False, cloud: bool = False):
    """Start the coding assistant mode."""
    try:
        assistant = CodingAssistant(
            agent_name=agent_name,
            provider=provider,
            model=model,
            local=local,
            cloud=cloud
        )

        assistant.start_session()

        while assistant.session_active:
            try:
                user_input = Prompt.ask(f"[bold {COLOR_ACCENT}]You[/]").strip()
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/]")
                break

            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]👋 Goodbye![/]")
                break

            if not user_input:
                continue

            try:
                if not assistant.process_command(user_input):
                    break
            except Exception as e:
                print_error(f"Command failed: {str(e)}")
                continue

    except Exception as e:
        print_error(f"Coding assistant failed: {str(e)}")
        raise typer.Exit(1)
