from pathlib import Path

import click

from . import __version__
from .config import Config
from .sync import SyncEngine
from .git_handler import GitHandler





def get_config() -> Config:
    """Load config from ~/.config/ob-sync/config.yaml with proper error handling."""
    # Config file location
    CONFIG_DIR = Path.home() / ".config" / "ob-sync"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    if not CONFIG_FILE.exists():
        raise click.ClickException(
            f"Config file not found at: {CONFIG_FILE}\n\n"
            f"Please create the config file with the following steps:\n"
            f"  1. Create the config directory:\n"
            f"     mkdir -p {CONFIG_DIR}\n\n"
            f"  2. Create the config file:\n"
            f"     touch {CONFIG_FILE}\n\n"
            f"  3. Add your configuration (see README for details)"
        )
    return Config.from_file(CONFIG_FILE)


@click.group()
@click.version_option(version=__version__, prog_name="ob-sync")
def main():
    pass


@main.command()
@click.option("--no-push", is_flag=True, help="Sync files but don't push to GitHub")
@click.option("--message", "-m", help="Custom commit message")
def sync(no_push, message):
    """Sync Obsidian vault to GitHub repository."""
    cfg = get_config()
    
    click.echo(f"📂 Vault: {cfg.vault_path}")
    click.echo(f"📤 Output: {cfg.output_path}")
    click.echo()
    
    if not cfg.vault_path.exists():
        raise click.ClickException(f"Vault not found: {cfg.vault_path}")
    
    engine = SyncEngine(cfg)
    stats = engine.sync()
    
    click.echo(f"✅ Synced {stats['files']} files")
    click.echo(f"🖼️  Copied {stats['images']} images")
    if stats['skipped'] > 0:
        click.echo(f"⏭️  Skipped {stats['skipped']} unchanged files")
    
    # Push if requested
    if not no_push and stats['files'] > 0:
        click.echo()
        click.echo("📤 Pushing to GitHub...")
        
        git = GitHandler(cfg.output_path)
        if git.commit_and_push(message):
            click.echo("✅ Pushed successfully!")
        else:
            click.echo("ℹ️  Nothing to push")


@main.command()
@click.option("--param", "-p", help="Test param")
def check(param):
    """Test command."""
    click.echo(param)


@main.command()
def status():
    """Show current sync status."""
    cfg = get_config()
    
    click.echo(f"📂 Vault: {cfg.vault_path}")
    click.echo(f"   Exists: {'✅' if cfg.vault_path.exists() else '❌'}")
    
    click.echo(f"📤 Output: {cfg.output_path}")
    click.echo(f"   Exists: {'✅' if cfg.output_path.exists() else '❌'}")
    
    if cfg.output_path.exists():
        try:
            git = GitHandler(cfg.output_path)
            git_status = git.status()
            click.echo(f"   Branch: {git_status['branch']}")
            click.echo(f"   Uncommitted: {'Yes' if git_status['dirty'] else 'No'}")
            click.echo(f"   Untracked: {git_status['untracked']}")
        except ValueError:
            click.echo("   Git: Not initialized")
    
    click.echo(f"🌐 GitHub: {cfg.github.username}/{cfg.github.repo}")


if __name__ == "__main__":
    main()
