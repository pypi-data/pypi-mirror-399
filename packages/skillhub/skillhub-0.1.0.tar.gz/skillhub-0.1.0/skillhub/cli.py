"""Main CLI entry point."""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path

from skillhub.core.config import Config
from skillhub.core.registry import Registry
from skillhub.core.validator import validate_skill

console = Console()

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    SkillHub - Package manager for AI agent workflows.

    \b
    Examples:
      skillhub search "react setup"
      skillhub pull benchmark-qwen
      skillhub list
    """
    pass

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
@click.option('--category', '-c', help='Filter by category')
def search(query, limit, category):
    """Search for skills in the registry."""
    try:
        config = Config()
        registry = Registry(config)

        console.print(f"\n[bold blue]🔍 Searching for:[/bold blue] {query}")

        results = registry.search(query)

        # Filter by category if specified
        if category:
            results = [r for r in results if r.get('category') == category]

        if not results:
            console.print("[yellow]No skills found matching your query.[/yellow]")
            console.print("\n[dim]Try:")
            console.print("  • Using different search terms")
            console.print("  • Searching without category filter")
            console.print("  • Running 'skillhub list' to see all skills[/dim]")
            return

        # Display results in table
        table = Table(title=f"Found {len(results)} skill(s)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Tags", style="yellow")

        for skill in results[:limit]:
            table.add_row(
                skill.get('name', ''),
                skill.get('category', ''),
                (skill.get('description', '')[:60] + '...') if len(skill.get('description', '')) > 60 else skill.get('description', ''),
                ', '.join(skill.get('tags', [])[:3])
            )

        console.print(table)

        if len(results) > limit:
            console.print(f"\n[dim]Showing {limit} of {len(results)} results. Use --limit to see more.[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

@cli.command()
@click.argument('skill_name')
@click.option('--output', '-o', help='Output directory', default='.')
def pull(skill_name, output):
    """Download a skill to local directory."""
    try:
        config = Config()
        registry = Registry(config)

        console.print(f"\n[bold blue]📥 Pulling skill:[/bold blue] {skill_name}")

        # Check if skill exists
        skill = registry.get_skill(skill_name)
        if not skill:
            console.print(f"[bold red]Error:[/bold red] Skill '{skill_name}' not found")
            console.print("\n[dim]Try:[/dim]")
            console.print(f"  skillhub search \"{skill_name}\"")
            raise click.Abort()

        # Download skill
        dest_path = Path(output) / f"{skill_name}.md"
        downloaded_path = registry.download_skill(skill_name, str(dest_path))

        # Show success message
        console.print(f"[bold green]✓ Skill downloaded successfully![/bold green]")
        console.print(f"\n[bold]Location:[/bold] {downloaded_path}")
        console.print(f"[bold]Category:[/bold] {skill.get('category', 'unknown')}")
        console.print(f"[bold]Version:[/bold] {skill.get('version', 'unknown')}")

        if skill.get('description'):
            console.print(f"\n[bold]Description:[/bold]")
            console.print(f"  {skill['description']}")

        console.print(f"\n[dim]Next steps:[/dim]")
        console.print(f"  cat {downloaded_path}")
        console.print(f"  # Follow the steps in the skill file")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

@cli.command()
@click.option('--refresh', is_flag=True, help='Refresh index from registry')
@click.option('--category', '-c', help='Filter by category')
def list(refresh, category):
    """List all available skills."""
    try:
        config = Config()
        registry = Registry(config)

        if refresh:
            console.print("[dim]Refreshing index from registry...[/dim]")

        index = registry.fetch_index(force_refresh=refresh)
        skills = index.get('skills', [])

        if category:
            skills = [s for s in skills if s.get('category') == category]

        console.print(f"\n[bold blue]📚 Available Skills:[/bold blue] {len(skills)} total")

        # Group by category
        categories = {}
        for skill in skills:
            cat = skill.get('category', 'uncategorized')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill)

        # Display by category
        for cat_name, cat_skills in sorted(categories.items()):
            console.print(f"\n[bold magenta]{cat_name.upper()}[/bold magenta] ({len(cat_skills)} skills)")

            for skill in sorted(cat_skills, key=lambda x: x.get('name', '')):
                name = skill.get('name', '')
                desc = skill.get('description', '')
                version = skill.get('version', '')

                # Truncate description
                if len(desc) > 70:
                    desc = desc[:67] + '...'

                console.print(f"  [cyan]{name}[/cyan] [dim]v{version}[/dim]")
                console.print(f"    {desc}")

        console.print(f"\n[dim]Use 'skillhub pull <skill-name>' to download a skill[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

@cli.command()
@click.argument('skill_file')
def validate(skill_file):
    """Validate a skill file format."""
    try:
        console.print(f"\n[bold blue]🔍 Validating:[/bold blue] {skill_file}")

        errors, warnings = validate_skill(skill_file)

        if errors:
            console.print(f"\n[bold red]❌ Validation Failed[/bold red] ({len(errors)} errors)")
            for i, error in enumerate(errors, 1):
                console.print(f"  {i}. {error}")

        if warnings:
            console.print(f"\n[bold yellow]⚠️  Warnings[/bold yellow] ({len(warnings)} warnings)")
            for i, warning in enumerate(warnings, 1):
                console.print(f"  {i}. {warning}")

        if not errors and not warnings:
            console.print(f"\n[bold green]✅ Perfect! No issues found.[/bold green]")
        elif not errors:
            console.print(f"\n[bold green]✅ Skill is valid[/bold green] (with {len(warnings)} warning(s))")

        # Exit with appropriate code
        if errors:
            raise click.Abort()

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

@cli.command()
def info():
    """Show SkillHub configuration and stats."""
    try:
        config = Config()
        registry = Registry(config)

        # Get stats
        stats = registry.get_stats()

        # Configuration panel
        config_text = f"""
[bold]Registry URL:[/bold] {config.get('registry_url')}
[bold]Cache Directory:[/bold] {config.get('cache_dir')}
[bold]Skills Directory:[/bold] {config.get('skills_dir')}
[bold]Index URL:[/bold] {config.get('index_url')}
        """

        console.print(Panel(config_text.strip(), title="[bold blue]SkillHub Configuration[/bold blue]", border_style="blue"))

        # Stats panel
        stats_text = f"""
[bold]Total Skills:[/bold] {stats['total_skills']}
[bold]Categories:[/bold] {stats['total_categories']}
[bold]Index Version:[/bold] {stats['version']}
[bold]Last Updated:[/bold] {stats['generated']}
        """

        console.print(Panel(stats_text.strip(), title="[bold green]Registry Statistics[/bold green]", border_style="green"))

        # Category breakdown
        console.print("\n[bold magenta]Skills by Category:[/bold magenta]")
        for cat, count in sorted(stats['categories'].items()):
            console.print(f"  • {cat}: {count}")

        console.print(f"\n[dim]Run 'skillhub list' to see all skills[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

@cli.command()
@click.argument('skill_name')
def show(skill_name):
    """Show detailed information about a skill."""
    try:
        config = Config()
        registry = Registry(config)

        skill = registry.get_skill(skill_name)

        if not skill:
            console.print(f"[bold red]Error:[/bold red] Skill '{skill_name}' not found")
            raise click.Abort()

        # Display skill details
        console.print(f"\n[bold blue]📋 Skill: {skill['name']}[/bold blue]")
        console.print(f"[dim]Version: {skill.get('version', 'unknown')}[/dim]\n")

        console.print(f"[bold]Description:[/bold]")
        console.print(f"  {skill.get('description', 'No description')}\n")

        console.print(f"[bold]Category:[/bold] {skill.get('category', 'unknown')}")
        console.print(f"[bold]Author:[/bold] {skill.get('author', 'unknown')}")

        if skill.get('difficulty'):
            console.print(f"[bold]Difficulty:[/bold] {skill['difficulty']}")

        if skill.get('estimated_time'):
            console.print(f"[bold]Estimated Time:[/bold] {skill['estimated_time']}")

        if skill.get('tags'):
            console.print(f"\n[bold]Tags:[/bold] {', '.join(skill['tags'])}")

        console.print(f"\n[bold]Download:[/bold]")
        console.print(f"  skillhub pull {skill['name']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()

if __name__ == '__main__':
    cli()
