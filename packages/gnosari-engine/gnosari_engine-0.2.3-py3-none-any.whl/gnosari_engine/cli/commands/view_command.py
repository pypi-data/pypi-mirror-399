"""
View Command - Displays comprehensive team configuration details
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import json
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.rule import Rule
from rich.box import ROUNDED

from .base_command import BaseCommand
from ..interfaces import (
    ConfigurationLoaderInterface,
    DisplayServiceInterface,
    DomainFactoryInterface
)


class ViewCommand(BaseCommand):
    """
    Single Responsibility: Display comprehensive team configuration details
    Open/Closed: Extensible for new display formats
    Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        display_service: DisplayServiceInterface,
        domain_factory: DomainFactoryInterface
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._domain_factory = domain_factory
    
    async def execute(
        self,
        team_config: Path,
        format: str = "tree",
        show_raw: bool = False,
        verbose: bool = False
    ) -> None:
        """Execute the view command with comprehensive team details"""
        
        operation = "view team configuration"
        self._log_execution_start(operation)
        
        try:
            # Load and build team configuration
            team = self._config_loader.load_team_configuration(team_config)
            
            # Display based on format
            if format == "tree":
                self._display_tree_view(team, verbose)
            elif format == "json":
                self._display_json_view(team, show_raw)
            elif format == "table":
                self._display_table_view(team, verbose)
            elif format == "chart":
                self._display_chart_view(team, verbose)
            else:
                self._display_tree_view(team, verbose)  # Default to tree
            
            self._log_execution_end(operation)
            
        except Exception as e:
            self._handle_error(e, operation)
            raise
    
    def _display_tree_view(self, team: Any, verbose: bool) -> None:
        """Display team configuration as an interactive tree"""
        
        # Create main tree
        tree = Tree(
            f"[bold magenta]Team: {team.name}[/bold magenta]",
            guide_style="bright_blue"
        )
        
        # Add team metadata
        metadata_branch = tree.add("[bold cyan]Metadata[/bold cyan]")
        self._add_team_metadata(metadata_branch, team, verbose)
        
        # Add agents
        agents_branch = tree.add(f"[bold cyan]Agents ({len(team.agents)})[/bold cyan]")
        for agent in team.agents:
            self._add_agent_details(agents_branch, agent, verbose)
        
        # Add delegations/handoffs
        if hasattr(team, 'delegations') and team.delegations:
            delegations_branch = tree.add(
                f"[bold cyan]Delegations/Handoffs ({len(team.delegations)})[/bold cyan]"
            )
            self._add_delegation_details(delegations_branch, team.delegations, verbose)
        
        # Add tools
        if hasattr(team, 'tools') and team.tools:
            tools_branch = tree.add(f"[bold cyan]Tools ({len(team.tools)})[/bold cyan]")
            self._add_tools_details(tools_branch, team.tools, verbose)
        
        # Add knowledge bases
        if hasattr(team, 'knowledge') and team.knowledge:
            knowledge_branch = tree.add(
                f"[bold cyan]Knowledge Bases ({len(team.knowledge)})[/bold cyan]"
            )
            self._add_knowledge_details(knowledge_branch, team.knowledge, verbose)
        
        # Display the tree
        self._display_service.console.print(Panel(tree, title="Team Configuration Details"))
    
    def _add_team_metadata(self, branch: Tree, team: Any, verbose: bool) -> None:
        """Add team metadata to tree branch"""
        
        metadata_items = [
            f"ID: [yellow]{team.id}[/yellow]",
            f"Name: [green]{team.name}[/green]",
            f"Description: {team.description or 'N/A'}",
            f"Version: {getattr(team, 'version', 'N/A')}",
            f"Tags: {', '.join(getattr(team, 'tags', [])) or 'None'}",
            f"Account ID: {getattr(team, 'account_id', 'N/A')}",
            f"Created: {getattr(team, 'created_at', 'N/A')}",
        ]
        
        # Add team configuration details
        if team.config:
            config_branch = branch.add("[cyan]Team Configuration[/cyan]")
            config_branch.add(f"Max Turns: {team.config.max_turns or 'N/A'}")
            config_branch.add(f"Timeout: {team.config.timeout or 'N/A'} seconds")
            config_branch.add(f"Log Level: {team.config.log_level}")
            config_branch.add(f"Enable Memory: {team.config.enable_memory}")
            config_branch.add(f"Debug Mode: {team.config.debug}")
        
        if verbose:
            # Add additional metadata in verbose mode
            if team.overrides:
                overrides_branch = branch.add(f"[cyan]Overrides ({len(team.overrides)})[/cyan]")
                for component_type, overrides_data in team.overrides.items():
                    comp_branch = overrides_branch.add(f"{component_type}")
                    for component_id, override_data in overrides_data.items():
                        comp_branch.add(f"  {component_id}: {override_data}")
            
            if team.components:
                components_branch = branch.add(f"[cyan]Component Filters ({len(team.components)})[/cyan]")
                for filter_type, filter_data in team.components.items():
                    components_branch.add(f"{filter_type}: {filter_data}")
            
        
        for item in metadata_items:
            branch.add(item)
    
    def _add_agent_details(self, branch: Tree, agent: Any, verbose: bool) -> None:
        """Add agent details to tree branch"""
        
        # Create agent branch with role indicator
        role_indicator = "🎯" if agent.is_orchestrator else "⚡"
        agent_role = "Orchestrator" if agent.is_orchestrator else "Worker"
        if agent.role:
            agent_role = f"{agent_role} ({agent.role})"
        
        agent_branch = branch.add(
            f"{role_indicator} [bold green]{agent.name}[/bold green] [{agent_role}]"
        )
        
        # Basic properties
        properties = agent_branch.add("[cyan]Core Properties[/cyan]")
        properties.add(f"ID: [yellow]{agent.id}[/yellow]")
        properties.add(f"Model: [blue]{agent.model}[/blue]")
        properties.add(f"Temperature: {agent.temperature}")
        properties.add(f"Reasoning Effort: {agent.reasoning_effort}")
        properties.add(f"Is Orchestrator: {agent.is_orchestrator}")
        properties.add(f"Role: {agent.role or 'N/A'}")
        properties.add(f"Max Turns: {agent.max_turns or 'N/A'}")
        properties.add(f"Debug Mode: {agent.debug}")
        
        # Instructions
        instructions_branch = agent_branch.add("[cyan]Instructions[/cyan]")
        instructions_branch.add(f"Base: {self._truncate_text(agent.instructions, 100)}")
        if agent.processed_instructions:
            instructions_branch.add(f"Processed: {self._truncate_text(agent.processed_instructions, 100)}")
        
        if verbose:
            # Add full instructions in verbose mode
            if agent.instructions and len(agent.instructions) > 100:
                instructions_branch.add(f"Full Base Instructions: {agent.instructions}")
            if agent.processed_instructions and len(agent.processed_instructions) > 100:
                instructions_branch.add(f"Full Processed Instructions: {agent.processed_instructions}")
        
        # Tools
        if agent.tools:
            tools = agent_branch.add(f"[cyan]Tools ({len(agent.tools)})[/cyan]")
            for tool in agent.tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                tools.add(f"🔧 {tool_name}")
        
        # Knowledge bases
        if agent.knowledge:
            knowledge = agent_branch.add(f"[cyan]Knowledge ({len(agent.knowledge)})[/cyan]")
            for kb in agent.knowledge:
                kb_name = kb.name if hasattr(kb, 'name') else str(kb)
                kb_type = f" ({kb.type})" if hasattr(kb, 'type') and kb.type else ""
                knowledge.add(f"📚 {kb_name}{kb_type}")
        
        # Traits
        if agent.traits:
            traits = agent_branch.add(f"[cyan]Traits ({len(agent.traits)})[/cyan]")
            for trait in agent.traits:
                trait_text = f"✨ {trait.name} (weight: {trait.weight})"
                if trait.category:
                    trait_text += f" - {trait.category}"
                traits.add(trait_text)
                if verbose:
                    traits.add(f"   Instructions: {trait.instructions}")
        
        # Handoffs (AgentHandoff objects)
        if agent.handoffs:
            handoffs = agent_branch.add(f"[cyan]Handoffs ({len(agent.handoffs)})[/cyan]")
            for handoff in agent.handoffs:
                target_name = handoff.target_agent_id
                handoff_text = f"→ {target_name}"
                if handoff.condition:
                    handoff_text += f" (when: {handoff.condition})"
                if handoff.message:
                    handoff_text += f" - {handoff.message}"
                handoffs.add(handoff_text)
        
        # Delegations (AgentDelegation objects)
        if agent.delegations:
            delegations = agent_branch.add(f"[cyan]Delegations ({len(agent.delegations)})[/cyan]")
            for delegation in agent.delegations:
                target_name = delegation.target_agent_id
                mode = delegation.mode
                delegation_text = f"⚡ {target_name} ({mode})"
                if delegation.timeout:
                    delegation_text += f" - {delegation.timeout}s timeout"
                if delegation.retry_attempts > 1:
                    delegation_text += f" - {delegation.retry_attempts} retries"
                delegations.add(delegation_text)
        
        # Learning objectives
        if agent.learning_objectives:
            learning = agent_branch.add(f"[cyan]Learning Objectives ({len(agent.learning_objectives)})[/cyan]")
            for objective in agent.learning_objectives:
                priority = objective.priority
                learning.add(f"🎯 [{priority.upper()}] {objective.objective}")
                if verbose and objective.success_criteria:
                    for criteria in objective.success_criteria:
                        learning.add(f"  ✓ {criteria}")
        
        # Memory
        if agent.memory:
            memory_branch = agent_branch.add("[cyan]Memory[/cyan]")
            memory_branch.add(f"Content: {self._truncate_text(agent.memory, 100)}")
            if verbose and len(agent.memory) > 100:
                memory_branch.add(f"Full Memory: {agent.memory}")
        
        # Event system
        if agent.listen:
            listeners = agent_branch.add(f"[cyan]Event Listeners ({len(agent.listen)})[/cyan]")
            for listener in agent.listen:
                listeners.add(f"👂 {listener}")
        
        if agent.trigger:
            triggers = agent_branch.add(f"[cyan]Event Triggers ({len(agent.trigger)})[/cyan]")
            for trigger in agent.trigger:
                triggers.add(f"🔥 {trigger}")
    
    def _add_delegation_details(self, branch: Tree, delegations: List[Any], verbose: bool) -> None:
        """Add delegation/handoff details to tree branch"""
        
        # Group delegations by source
        delegation_map: Dict[str, List[str]] = {}
        
        for delegation in delegations:
            source = getattr(delegation, 'source', 'unknown')
            target = getattr(delegation, 'target', 'unknown')
            
            if source not in delegation_map:
                delegation_map[source] = []
            delegation_map[source].append(target)
        
        for source, targets in delegation_map.items():
            source_branch = branch.add(f"[green]{source}[/green]")
            for target in targets:
                source_branch.add(f"→ [yellow]{target}[/yellow]")
                
                if verbose:
                    # Add delegation conditions if available
                    for delegation in delegations:
                        if getattr(delegation, 'source', '') == source and getattr(delegation, 'target', '') == target:
                            if hasattr(delegation, 'conditions'):
                                source_branch.add(f"  Conditions: {delegation.conditions}")
    
    def _add_tools_details(self, branch: Tree, tools: List[Any], verbose: bool) -> None:
        """Add tool details to tree branch"""
        
        for tool in tools:
            if isinstance(tool, dict):
                tool_name = tool.get('name', 'unknown')
                tool_branch = branch.add(f"🔧 [green]{tool_name}[/green]")
                
                if verbose:
                    if 'module' in tool:
                        tool_branch.add(f"Module: {tool['module']}")
                    if 'class_name' in tool:
                        tool_branch.add(f"Class: {tool['class_name']}")
                    if 'args' in tool:
                        tool_branch.add(f"Args: {tool['args']}")
                    if 'url' in tool:
                        tool_branch.add(f"URL: {tool['url']}")
            else:
                tool_name = getattr(tool, 'name', str(tool))
                tool_branch = branch.add(f"🔧 [green]{tool_name}[/green]")
                
                if verbose and hasattr(tool, '__dict__'):
                    for key, value in tool.__dict__.items():
                        if not key.startswith('_'):
                            tool_branch.add(f"{key}: {value}")
    
    def _add_knowledge_details(self, branch: Tree, knowledge_bases: List[Any], verbose: bool) -> None:
        """Add knowledge base details to tree branch"""
        
        for kb in knowledge_bases:
            if isinstance(kb, dict):
                kb_name = kb.get('name', 'unknown')
                kb_branch = branch.add(f"📚 [green]{kb_name}[/green]")
                kb_branch.add(f"Type: {kb.get('type', 'N/A')}")
                
                if 'data' in kb:
                    data_branch = kb_branch.add("Data Sources:")
                    for source in kb['data'][:5]:  # Show first 5
                        data_branch.add(f"• {source}")
                    if len(kb['data']) > 5:
                        data_branch.add(f"... and {len(kb['data']) - 5} more")
                
                if verbose:
                    if 'config' in kb:
                        kb_branch.add(f"Config: {kb['config']}")
            else:
                kb_name = getattr(kb, 'name', str(kb))
                kb_branch = branch.add(f"📚 [green]{kb_name}[/green]")
                
                if verbose and hasattr(kb, '__dict__'):
                    for key, value in kb.__dict__.items():
                        if not key.startswith('_'):
                            kb_branch.add(f"{key}: {value}")
    
    def _display_json_view(self, team: Any, show_raw: bool) -> None:
        """Display team configuration as JSON"""
        
        if show_raw:
            # Show raw object representation
            team_dict = self._serialize_team(team)
        else:
            # Show structured JSON
            team_dict = self._create_structured_json(team)
        
        json_str = json.dumps(team_dict, indent=2, default=str)
        
        # Use syntax highlighting for JSON
        from rich.syntax import Syntax
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        
        self._display_service.console.print(
            Panel(syntax, title="Team Configuration (JSON)")
        )
    
    def _display_table_view(self, team: Any, verbose: bool) -> None:
        """Display team configuration in table format"""
        
        # Create team overview table
        overview_table = Table(title=f"Team: {team.name}", show_header=True)
        overview_table.add_column("Property", style="cyan")
        overview_table.add_column("Value", style="green")
        
        overview_table.add_row("ID", str(team.id))
        overview_table.add_row("Name", team.name)
        overview_table.add_row("Description", team.description or "N/A")
        overview_table.add_row("Version", team.version)
        overview_table.add_row("Tags", ", ".join(team.tags) or "None")
        overview_table.add_row("Account ID", str(team.account_id) if team.account_id else "N/A")
        overview_table.add_row("Total Agents", str(len(team.agents)))
        overview_table.add_row("Orchestrator", self._get_orchestrator_name(team))
        
        if team.config:
            overview_table.add_row("Max Turns", str(team.config.max_turns) if team.config.max_turns else "N/A")
            overview_table.add_row("Timeout", f"{team.config.timeout}s" if team.config.timeout else "N/A")
            overview_table.add_row("Debug Mode", str(team.config.debug))
        
        # Create agents table
        agents_table = Table(title="Agents", show_header=True)
        agents_table.add_column("Name", style="green")
        agents_table.add_column("Role", style="yellow")
        agents_table.add_column("Model", style="blue")
        agents_table.add_column("Temperature", style="cyan")
        agents_table.add_column("Tools", style="cyan")
        agents_table.add_column("Knowledge", style="magenta")
        agents_table.add_column("Handoffs", style="red")
        agents_table.add_column("Delegations", style="bright_yellow")
        
        for agent in team.agents:
            role = "Orchestrator" if agent.is_orchestrator else "Worker"
            if agent.role:
                role = f"{role} ({agent.role})"
            
            tools = ", ".join([
                tool.name if hasattr(tool, 'name') else str(tool)
                for tool in agent.tools
            ]) or "None"
            
            knowledge = ", ".join([
                kb.name if hasattr(kb, 'name') else str(kb)
                for kb in agent.knowledge
            ]) or "None"
            
            handoffs = ", ".join([
                handoff.target_agent_id
                for handoff in agent.handoffs
            ]) or "None"
            
            delegations = ", ".join([
                f"{delegation.target_agent_id}({delegation.mode})"
                for delegation in agent.delegations
            ]) or "None"
            
            agents_table.add_row(
                agent.name, 
                role, 
                agent.model, 
                str(agent.temperature),
                tools, 
                knowledge,
                handoffs,
                delegations
            )
        
        # Display all tables
        group = Group(overview_table, agents_table)
        
        if verbose:
            # Add additional tables in verbose mode
            tables = [overview_table, agents_table]
            
            if team.tools:
                tools_table = self._create_tools_table(team.tools)
                tables.append(tools_table)
            
            if team.knowledge:
                knowledge_table = self._create_knowledge_table(team.knowledge)
                tables.append(knowledge_table)
            
            if team.traits:
                traits_table = self._create_traits_table(team.traits)
                tables.append(traits_table)
            
            # Add handoffs/delegations summary table
            if any(agent.handoffs or agent.delegations for agent in team.agents):
                handoffs_table = self._create_handoffs_delegations_table(team.agents)
                tables.append(handoffs_table)
            
            group = Group(*tables)
        
        self._display_service.console.print(
            Panel(group, title="Team Configuration Details")
        )
    
    def _display_chart_view(self, team: Any, verbose: bool) -> None:
        """Display team configuration as a flow chart"""
        
        # Create components
        header_content = self._create_team_header(team)
        chart_content = self._create_flow_chart(team, verbose)
        legend_content = self._create_chart_legend(team, verbose)
        
        # Display sequentially for better terminal compatibility
        self._display_service.console.print(header_content)
        self._display_service.console.print(chart_content)
        self._display_service.console.print(legend_content)
    
    def _create_team_header(self, team: Any) -> Panel:
        """Create team header for chart view"""
        
        header_text = Text()
        header_text.append(f"🏢 {team.name}", style="bold bright_blue")
        header_text.append(f" (v{team.version})", style="dim")
        header_text.append("\n")
        header_text.append(f"{team.description or 'No description'}", style="italic")
        header_text.append("\n")
        header_text.append(f"👥 {len(team.agents)} agents • ", style="cyan")
        header_text.append(f"🔧 {len(team.tools)} tools • ", style="yellow")
        header_text.append(f"📚 {len(team.knowledge)} knowledge bases", style="magenta")
        
        return Panel(
            Align.center(header_text),
            title="Team Overview",
            box=ROUNDED,
            style="bright_blue"
        )
    
    def _create_flow_chart(self, team: Any, verbose: bool) -> Panel:
        """Create the main flow chart showing agents and connections"""
        
        # Get orchestrator and workers
        orchestrator = team.get_orchestrator()
        workers = team.get_worker_agents()
        
        # Build chart content using simpler ASCII art
        chart_content = Text()
        
        # Title
        chart_content.append("🎯 TEAM STRUCTURE\n\n", style="bold bright_blue")
        
        # Orchestrator
        chart_content.append("┌─── ORCHESTRATOR ───┐\n", style="bright_blue")
        chart_content.append(f"│ 🎯 {orchestrator.name[:16]:<16} │\n", style="bright_blue")
        chart_content.append(f"│ {orchestrator.model[:18]:<18} │\n", style="cyan")
        chart_content.append(f"│ Temp: {orchestrator.temperature:<12} │\n", style="yellow")
        chart_content.append(f"│ Tools: {len(orchestrator.tools):<11} │\n", style="green")
        chart_content.append("└─────────────────────┘\n", style="bright_blue")
        
        # Connection line
        if workers:
            chart_content.append("          │\n", style="white")
            chart_content.append("    ┌─────┼─────┐\n", style="white")
            chart_content.append("    │     │     │\n", style="white")
            chart_content.append("    ▼     ▼     ▼\n\n", style="white")
        
        # Workers in a single row
        if workers:
            # Create worker boxes side by side (max 3)
            worker_display = workers[:3]  # Show only first 3 workers
            
            # Create compact worker boxes
            worker_lines = [[] for _ in range(6)]  # 6 lines per worker box
            
            for worker in worker_display:
                worker_lines[0].append("┌─── WORKER ────┐")
                worker_lines[1].append(f"│ ⚡ {worker.name[:12]:<12} │")
                worker_lines[2].append(f"│ {worker.model[:13]:<13} │")
                worker_lines[3].append(f"│ T:{worker.temperature:<11} │")
                worker_lines[4].append(f"│ 🔧:{len(worker.tools):<10} │")
                worker_lines[5].append("└───────────────┘")
            
            # Add padding for missing workers
            while len(worker_display) < 3:
                for i in range(6):
                    worker_lines[i].append(" " * 17)
                worker_display.append(None)
            
            # Display worker lines
            for line_parts in worker_lines:
                line_text = "  ".join(line_parts)
                chart_content.append(f"{line_text}\n", style="yellow")
            
            # Show if there are more workers
            if len(workers) > 3:
                chart_content.append(f"\n... and {len(workers) - 3} more workers\n", style="dim")
        
        # Connections section
        chart_content.append("\n")
        chart_content.append("=" * 60 + "\n", style="bright_white")
        chart_content.append("🔄 CONNECTIONS\n", style="bold bright_white")
        chart_content.append("=" * 60 + "\n", style="bright_white")
        
        # Show handoffs
        handoff_lines = self._create_connection_lines(team.agents, "handoffs", "→")
        if handoff_lines:
            chart_content.append("\n🤝 HANDOFFS:\n", style="bold green")
            for line in handoff_lines:
                chart_content.append(f"{line}\n", style="green")
        
        # Show delegations
        delegation_lines = self._create_connection_lines(team.agents, "delegations", "⚡")
        if delegation_lines:
            chart_content.append("\n⚡ DELEGATIONS:\n", style="bold red")
            for line in delegation_lines:
                chart_content.append(f"{line}\n", style="red")
        
        if not handoff_lines and not delegation_lines:
            chart_content.append("\n(No handoffs or delegations configured)\n", style="dim")
        
        return Panel(
            chart_content,
            title="Team Flow Chart",
            box=ROUNDED,
            style="green"
        )
    
    def _create_agent_box(self, agent: Any, role_type: str, verbose: bool, compact: bool = False) -> List[str]:
        """Create a visual box for an agent"""
        
        if compact:
            # Compact version for workers
            lines = [
                "┌──────────────────┐",
                f"│ ⚡ {agent.name[:14]:<14} │",
                f"│ {agent.model[:16]:<16} │",
                f"│ 🔧 {len(agent.tools)} tools      │",
                "└──────────────────┘"
            ]
        else:
            # Full version for orchestrator
            lines = [
                "┌─────────────────────────────────────┐",
                f"│ 🎯 {agent.name:<30} │",
                f"│ Model: {agent.model:<26} │",
                f"│ Temp: {agent.temperature:<27} │",
                f"│ 🔧 Tools: {len(agent.tools):<23} │",
                f"│ 📚 Knowledge: {len(agent.knowledge):<19} │"
            ]
            
            if verbose:
                lines.append(f"│ Role: {(agent.role or 'N/A'):<27} │")
                lines.append(f"│ Debug: {str(agent.debug):<26} │")
            
            lines.append("└─────────────────────────────────────┘")
        
        return lines
    
    def _create_connection_lines(self, agents: List[Any], connection_type: str, symbol: str) -> List[str]:
        """Create lines showing connections between agents"""
        
        lines = []
        
        for agent in agents:
            connections = getattr(agent, connection_type, [])
            if connections:
                for connection in connections:
                    if connection_type == "handoffs":
                        target = connection.target_agent_id
                        condition = f" (when: {connection.condition})" if connection.condition else ""
                        lines.append(f"  {agent.name} {symbol} {target}{condition}")
                    elif connection_type == "delegations":
                        target = connection.target_agent_id
                        mode = f"({connection.mode})"
                        timeout = f" [timeout: {connection.timeout}s]" if connection.timeout else ""
                        lines.append(f"  {agent.name} {symbol} {target} {mode}{timeout}")
        
        return lines
    
    def _create_chart_legend(self, team: Any, verbose: bool) -> Panel:
        """Create legend for the chart"""
        
        # Connection counts
        total_handoffs = sum(len(agent.handoffs) for agent in team.agents)
        total_delegations = sum(len(agent.delegations) for agent in team.agents)
        
        legend_text = Text()
        
        # Compact stats in a single line
        legend_text.append("📊 TEAM STATS: ", style="bold bright_white")
        legend_text.append(f"👥 {len(team.agents)} agents • ", style="cyan")
        legend_text.append(f"🔧 {len(team.tools)} tools • ", style="yellow")
        legend_text.append(f"📚 {len(team.knowledge)} knowledge • ", style="magenta")
        legend_text.append(f"✨ {len(team.traits)} traits • ", style="green")
        legend_text.append(f"🤝 {total_handoffs} handoffs • ", style="bright_green")
        legend_text.append(f"⚡ {total_delegations} delegations", style="bright_red")
        
        if verbose and team.config:
            legend_text.append("\n\n⚙️ CONFIG: ", style="bold bright_white")
            legend_text.append(f"Max Turns: {team.config.max_turns or 'N/A'} • ", style="dim")
            legend_text.append(f"Timeout: {team.config.timeout or 'N/A'}s • ", style="dim")
            legend_text.append(f"Debug: {team.config.debug}", style="dim")
        
        return Panel(
            Align.center(legend_text),
            title="Team Statistics",
            box=ROUNDED,
            style="bright_yellow"
        )
    
    def _create_tools_table(self, tools: List[Any]) -> Table:
        """Create a table for tools display"""
        
        table = Table(title="Tools", show_header=True)
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Configuration", style="cyan")
        
        for tool in tools:
            if isinstance(tool, dict):
                name = tool.get('name', 'unknown')
                tool_type = "MCP" if 'url' in tool else "Built-in"
                config = tool.get('url') or tool.get('module', 'N/A')
            else:
                name = getattr(tool, 'name', str(tool))
                tool_type = "Object"
                config = tool.__class__.__name__
            
            table.add_row(name, tool_type, config)
        
        return table
    
    def _create_knowledge_table(self, knowledge_bases: List[Any]) -> Table:
        """Create a table for knowledge bases display"""
        
        table = Table(title="Knowledge Bases", show_header=True)
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Sources Count", style="cyan")
        table.add_column("Sample Sources", style="white")
        
        for kb in knowledge_bases:
            name = kb.name
            kb_type = kb.type
            sources_count = str(len(kb.data))
            
            # Show first 2 sources, truncated
            sample_sources = []
            for i, source in enumerate(kb.data[:2]):
                truncated = self._truncate_text(source, 40)
                sample_sources.append(truncated)
            
            if len(kb.data) > 2:
                sample_sources.append(f"... +{len(kb.data) - 2} more")
            
            sample_text = "; ".join(sample_sources) if sample_sources else "None"
            
            table.add_row(name, kb_type, sources_count, sample_text)
        
        return table
    
    def _create_traits_table(self, traits: List[Any]) -> Table:
        """Create a table for traits display"""
        
        table = Table(title="Traits", show_header=True)
        table.add_column("Name", style="green")
        table.add_column("ID", style="yellow")
        table.add_column("Weight", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Instructions", style="white")
        
        for trait in traits:
            name = trait.name
            trait_id = trait.id
            weight = f"{trait.weight} ({trait.get_weight_description()})"
            category = trait.category or "N/A"
            instructions = self._truncate_text(trait.instructions, 50)
            
            table.add_row(name, trait_id, weight, category, instructions)
        
        return table
    
    def _create_handoffs_delegations_table(self, agents: List[Any]) -> Table:
        """Create a table for handoffs and delegations display"""
        
        table = Table(title="Handoffs & Delegations", show_header=True)
        table.add_column("Source Agent", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Target Agent", style="blue")
        table.add_column("Details", style="cyan")
        
        for agent in agents:
            # Add handoffs
            for handoff in agent.handoffs:
                details = []
                if handoff.condition:
                    details.append(f"Condition: {handoff.condition}")
                if handoff.message:
                    details.append(f"Message: {handoff.message}")
                
                table.add_row(
                    agent.name,
                    "Handoff",
                    handoff.target_agent_id,
                    "; ".join(details) or "N/A"
                )
            
            # Add delegations
            for delegation in agent.delegations:
                details = [f"Mode: {delegation.mode}"]
                if delegation.timeout:
                    details.append(f"Timeout: {delegation.timeout}s")
                if delegation.retry_attempts > 1:
                    details.append(f"Retries: {delegation.retry_attempts}")
                if delegation.instructions:
                    details.append(f"Instructions: {delegation.instructions}")
                
                table.add_row(
                    agent.name,
                    "Delegation",
                    delegation.target_agent_id,
                    "; ".join(details)
                )
        
        return table
    
    def _get_orchestrator_name(self, team: Any) -> str:
        """Get the name of the orchestrator agent"""
        
        for agent in team.agents:
            if agent.is_orchestrator:
                return agent.name
        return "None"
    
    def _serialize_team(self, team: Any) -> Dict[str, Any]:
        """Serialize team object to dictionary"""
        
        def serialize_obj(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if not key.startswith('_'):
                        if isinstance(value, list):
                            result[key] = [serialize_obj(item) for item in value]
                        elif isinstance(value, dict):
                            result[key] = {k: serialize_obj(v) for k, v in value.items()}
                        elif hasattr(value, '__dict__'):
                            result[key] = serialize_obj(value)
                        else:
                            result[key] = str(value)
                return result
            return str(obj)
        
        return serialize_obj(team)
    
    def _create_structured_json(self, team: Any) -> Dict[str, Any]:
        """Create a structured JSON representation of the team"""
        
        return {
            "team": {
                "id": str(team.id),
                "name": team.name,
                "description": team.description,
                "version": team.version,
                "tags": team.tags,
                "account_id": team.account_id,
                "config": {
                    "max_turns": team.config.max_turns,
                    "timeout": team.config.timeout,
                    "log_level": team.config.log_level,
                    "enable_memory": team.config.enable_memory,
                    "debug": team.config.debug
                } if team.config else None,
                "overrides": team.overrides,
                "components": team.components,
                "agents": [
                    {
                        "id": str(agent.id),
                        "name": agent.name,
                        "is_orchestrator": agent.is_orchestrator,
                        "role": agent.role,
                        "model": agent.model,
                        "temperature": agent.temperature,
                        "reasoning_effort": agent.reasoning_effort,
                        "max_turns": agent.max_turns,
                        "debug": agent.debug,
                        "instructions": agent.instructions,
                        "processed_instructions": agent.processed_instructions,
                        "tools": [
                            tool.name if hasattr(tool, 'name') else str(tool)
                            for tool in agent.tools
                        ],
                        "knowledge": [
                            {
                                "name": kb.name if hasattr(kb, 'name') else str(kb),
                                "type": kb.type if hasattr(kb, 'type') else None
                            }
                            for kb in agent.knowledge
                        ],
                        "traits": [
                            {
                                "id": trait.id,
                                "name": trait.name,
                                "instructions": trait.instructions,
                                "weight": trait.weight,
                                "weight_description": trait.get_weight_description(),
                                "category": trait.category,
                                "tags": trait.tags
                            }
                            for trait in agent.traits
                        ],
                        "handoffs": [
                            {
                                "target_agent_id": handoff.target_agent_id,
                                "condition": handoff.condition,
                                "message": handoff.message
                            }
                            for handoff in agent.handoffs
                        ],
                        "delegations": [
                            {
                                "target_agent_id": delegation.target_agent_id,
                                "mode": delegation.mode,
                                "timeout": delegation.timeout,
                                "retry_attempts": delegation.retry_attempts,
                                "instructions": delegation.instructions
                            }
                            for delegation in agent.delegations
                        ],
                        "learning_objectives": [
                            {
                                "objective": obj.objective,
                                "priority": obj.priority,
                                "success_criteria": obj.success_criteria
                            }
                            for obj in agent.learning_objectives
                        ],
                        "memory": agent.memory,
                        "listen": agent.listen,
                        "trigger": agent.trigger
                    }
                    for agent in team.agents
                ],
                "tools": [
                    {
                        "name": tool.name if hasattr(tool, 'name') else str(tool),
                        "id": tool.id if hasattr(tool, 'id') else None,
                        "type": tool.type if hasattr(tool, 'type') else None
                    }
                    for tool in team.tools
                ],
                "knowledge": [
                    {
                        "name": kb.name if hasattr(kb, 'name') else str(kb),
                        "id": kb.id if hasattr(kb, 'id') else None,
                        "type": kb.type if hasattr(kb, 'type') else None
                    }
                    for kb in team.knowledge
                ],
                "traits": [
                    {
                        "id": trait.id,
                        "name": trait.name,
                        "instructions": trait.instructions,
                        "weight": trait.weight,
                        "weight_description": trait.get_weight_description(),
                        "category": trait.category,
                        "tags": trait.tags
                    }
                    for trait in team.traits
                ]
            }
        }
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        
        if not text:
            return "N/A"
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."