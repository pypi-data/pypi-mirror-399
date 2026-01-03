"""Feature branch workflow commands for aiterm.

Provides rich visualization and automation for feature branch + worktree workflows.

Commands:
- status: Show feature pipeline visualization
- list: List features with worktree info
- start: Create feature branch + optional worktree + deps
- cleanup: Interactive cleanup of merged features
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

app = typer.Typer(
    help="Feature branch workflow commands.",
    no_args_is_help=True,
)

console = Console()


@dataclass
class FeatureBranch:
    """Represents a feature branch."""

    name: str
    full_name: str
    is_current: bool = False
    commits_ahead: int = 0
    worktree_path: Optional[Path] = None
    is_merged: bool = False
    is_new: bool = False  # True if 0 commits ahead (just created from dev)
    has_pr: bool = False
    pr_number: Optional[int] = None


@dataclass
class WorktreeInfo:
    """Represents a git worktree."""

    path: Path
    branch: str
    commit: str
    is_bare: bool = False
    is_main: bool = False


def _run_git(args: list[str], capture: bool = True) -> Optional[str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=capture,
            text=True,
            check=True,
        )
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError:
        return None


def _get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    return _run_git(["branch", "--show-current"])


def _get_repo_root() -> Optional[Path]:
    """Get the git repository root."""
    result = _run_git(["rev-parse", "--show-toplevel"])
    return Path(result) if result else None


def _get_feature_branches() -> list[FeatureBranch]:
    """Get all feature branches with info."""
    branches = []
    current = _get_current_branch()

    # Get local branches starting with 'feature/' or 'feat/'
    result = _run_git(["branch", "--list", "feature/*", "feat/*", "--format=%(refname:short)"])
    if not result:
        return branches

    for line in result.split("\n"):
        if not line.strip():
            continue

        branch_name = line.strip()
        short_name = branch_name.replace("feature/", "").replace("feat/", "")

        # Count commits ahead of dev
        commits_ahead = 0
        count_result = _run_git(["rev-list", "--count", f"dev..{branch_name}"])
        if count_result and count_result.isdigit():
            commits_ahead = int(count_result)

        # Check if merged into dev
        merged_result = _run_git(["branch", "--merged", "dev", "--list", branch_name])
        is_in_merged_list = bool(merged_result and merged_result.strip())

        # Distinguish "new" (0 commits, just created) from "merged" (had commits, now merged)
        # A branch is "new" if it has 0 commits ahead of dev
        # A branch is "merged" if it's in the merged list AND had commits (not new)
        is_new = commits_ahead == 0
        is_merged = is_in_merged_list and not is_new

        branches.append(
            FeatureBranch(
                name=short_name,
                full_name=branch_name,
                is_current=(branch_name == current),
                commits_ahead=commits_ahead,
                is_merged=is_merged,
                is_new=is_new,
            )
        )

    return branches


def _get_worktrees() -> list[WorktreeInfo]:
    """Get all git worktrees."""
    worktrees = []
    result = _run_git(["worktree", "list", "--porcelain"])
    if not result:
        return worktrees

    current_worktree: dict = {}
    for line in result.split("\n"):
        if line.startswith("worktree "):
            if current_worktree:
                worktrees.append(
                    WorktreeInfo(
                        path=Path(current_worktree.get("path", "")),
                        branch=current_worktree.get("branch", "").replace("refs/heads/", ""),
                        commit=current_worktree.get("HEAD", "")[:8],
                        is_bare=current_worktree.get("bare", False),
                    )
                )
            current_worktree = {"path": line.replace("worktree ", "")}
        elif line.startswith("HEAD "):
            current_worktree["HEAD"] = line.replace("HEAD ", "")
        elif line.startswith("branch "):
            current_worktree["branch"] = line.replace("branch ", "")
        elif line == "bare":
            current_worktree["bare"] = True

    # Add last worktree
    if current_worktree:
        worktrees.append(
            WorktreeInfo(
                path=Path(current_worktree.get("path", "")),
                branch=current_worktree.get("branch", "").replace("refs/heads/", ""),
                commit=current_worktree.get("HEAD", "")[:8],
                is_bare=current_worktree.get("bare", False),
            )
        )

    return worktrees


@app.command(
    "status",
    epilog="""
[bold]Examples:[/]
  ait feature status    # Show feature pipeline
""",
)
def feature_status() -> None:
    """Show feature pipeline visualization."""
    repo_root = _get_repo_root()
    if not repo_root:
        console.print("[red]Error:[/] Not in a git repository")
        raise typer.Exit(1)

    project_name = repo_root.name
    current_branch = _get_current_branch()
    features = _get_feature_branches()
    worktrees = _get_worktrees()

    # Map worktrees to branches
    worktree_map = {wt.branch: wt for wt in worktrees if wt.branch}

    # Build pipeline visualization
    console.print(
        Panel(
            f"[bold]{project_name}[/] - Feature Pipeline",
            border_style="cyan",
        )
    )

    # Show branch hierarchy
    tree = Tree("[bold cyan]main[/]")
    dev_node = tree.add("[bold green]dev[/]")

    if not features:
        dev_node.add("[dim]No feature branches[/]")
    else:
        for feature in sorted(features, key=lambda f: f.name):
            # Build feature label
            icon = "[green]●[/]" if feature.is_current else "[dim]○[/]"
            if feature.is_merged:
                status_badge = " [yellow](merged)[/]"
            elif feature.is_new:
                status_badge = " [cyan](new)[/]"
            else:
                status_badge = ""
            commits = f" [dim]+{feature.commits_ahead}[/]" if feature.commits_ahead else ""

            # Check for worktree
            worktree = worktree_map.get(feature.full_name)
            wt_badge = ""
            if worktree:
                wt_badge = f" [blue]📁 {worktree.path}[/]"

            label = f"{icon} {feature.full_name}{commits}{status_badge}{wt_badge}"
            dev_node.add(label)

    console.print(tree)

    # Summary stats
    total = len(features)
    merged = sum(1 for f in features if f.is_merged)
    new_count = sum(1 for f in features if f.is_new)
    in_progress = total - merged - new_count

    console.print()
    stats = f"[bold]Summary:[/] {total} features ({in_progress} in progress"
    if new_count > 0:
        stats += f", {new_count} new"
    if merged > 0:
        stats += f", {merged} merged"
    stats += ")"
    console.print(stats)

    if merged > 0:
        console.print("[yellow]Tip:[/] Run 'ait feature cleanup' to remove merged branches")


@app.command(
    "list",
    epilog="""
[bold]Examples:[/]
  ait feature list         # List all features
  ait feature list --all   # Include merged
""",
)
def feature_list(
    all_branches: bool = typer.Option(
        False, "--all", "-a", help="Include merged branches."
    ),
) -> None:
    """List feature branches with details."""
    repo_root = _get_repo_root()
    if not repo_root:
        console.print("[red]Error:[/] Not in a git repository")
        raise typer.Exit(1)

    features = _get_feature_branches()
    worktrees = _get_worktrees()
    worktree_map = {wt.branch: wt for wt in worktrees if wt.branch}

    if not all_branches:
        features = [f for f in features if not f.is_merged]

    if not features:
        console.print("[dim]No feature branches found.[/]")
        if not all_branches:
            console.print("[dim]Use --all to include merged branches.[/]")
        return

    table = Table(title="Feature Branches", border_style="cyan")
    table.add_column("", width=2)
    table.add_column("Branch", style="bold")
    table.add_column("Commits", justify="right")
    table.add_column("Status")
    table.add_column("Worktree")

    for feature in sorted(features, key=lambda f: f.name):
        icon = "[green]●[/]" if feature.is_current else "[dim]○[/]"

        if feature.is_merged:
            status = "[yellow]merged[/]"
        elif feature.is_new:
            status = "[cyan]new[/]"
        else:
            status = "[green]active[/]"

        worktree = worktree_map.get(feature.full_name)
        wt_path = str(worktree.path) if worktree else "[dim]-[/]"

        table.add_row(
            icon,
            feature.full_name,
            str(feature.commits_ahead) if feature.commits_ahead else "-",
            status,
            wt_path,
        )

    console.print(table)


@app.command(
    "start",
    epilog="""
[bold]Examples:[/]
  ait feature start my-feature           # Create feature/my-feature
  ait feature start auth --worktree      # Create with worktree
  ait feature start fix --no-install     # Skip dependency install
""",
)
def feature_start(
    name: str = typer.Argument(..., help="Feature name (without 'feature/' prefix)."),
    worktree: bool = typer.Option(
        False, "--worktree", "-w", help="Create in a worktree."
    ),
    no_install: bool = typer.Option(
        False, "--no-install", help="Skip dependency installation."
    ),
    base: str = typer.Option(
        "dev", "--base", "-b", help="Base branch to start from."
    ),
) -> None:
    """Start a new feature branch with optional worktree."""
    repo_root = _get_repo_root()
    if not repo_root:
        console.print("[red]Error:[/] Not in a git repository")
        raise typer.Exit(1)

    project_name = repo_root.name
    branch_name = f"feature/{name}"

    console.print(f"[bold cyan]Starting feature:[/] {branch_name}")

    # Step 1: Ensure we have latest base branch
    console.print(f"[dim]Fetching {base}...[/]")
    _run_git(["fetch", "origin", base])

    # Step 2: Check if branch already exists
    existing = _run_git(["branch", "--list", branch_name])
    if existing:
        console.print(f"[yellow]Branch already exists:[/] {branch_name}")
        raise typer.Exit(1)

    if worktree:
        # Create worktree
        worktree_base = Path.home() / ".git-worktrees" / project_name
        worktree_base.mkdir(parents=True, exist_ok=True)
        worktree_path = worktree_base / name

        console.print(f"[dim]Creating worktree at {worktree_path}...[/]")

        # Create branch and worktree together
        result = _run_git(["worktree", "add", "-b", branch_name, str(worktree_path), f"origin/{base}"])
        if result is None:
            # worktree add doesn't output on success, check if path exists
            if not worktree_path.exists():
                console.print("[red]Failed to create worktree[/]")
                raise typer.Exit(1)

        console.print(f"[green]✓[/] Created worktree: {worktree_path}")

        if not no_install:
            _install_deps(worktree_path)

        console.print()
        console.print(f"[bold green]Feature ready![/]")
        console.print(f"  cd {worktree_path}")
    else:
        # Regular branch creation
        console.print(f"[dim]Creating branch from {base}...[/]")

        _run_git(["checkout", base])
        _run_git(["pull", "origin", base])
        _run_git(["checkout", "-b", branch_name])

        console.print(f"[green]✓[/] Created branch: {branch_name}")

        if not no_install:
            _install_deps(repo_root)

        console.print()
        console.print("[bold green]Feature ready![/] You're now on the feature branch.")


def _install_deps(path: Path) -> None:
    """Install dependencies based on project type."""
    console.print("[dim]Checking for dependencies...[/]")

    # Python (pyproject.toml or requirements.txt)
    if (path / "pyproject.toml").exists():
        console.print("[dim]Installing Python deps (uv)...[/]")
        subprocess.run(["uv", "sync"], cwd=path, capture_output=True)
        console.print("[green]✓[/] Python dependencies installed")
    elif (path / "requirements.txt").exists():
        console.print("[dim]Installing Python deps (pip)...[/]")
        subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=path, capture_output=True)
        console.print("[green]✓[/] Python dependencies installed")

    # Node (package.json)
    elif (path / "package.json").exists():
        if (path / "bun.lockb").exists():
            console.print("[dim]Installing Node deps (bun)...[/]")
            subprocess.run(["bun", "install"], cwd=path, capture_output=True)
        elif (path / "pnpm-lock.yaml").exists():
            console.print("[dim]Installing Node deps (pnpm)...[/]")
            subprocess.run(["pnpm", "install"], cwd=path, capture_output=True)
        else:
            console.print("[dim]Installing Node deps (npm)...[/]")
            subprocess.run(["npm", "install"], cwd=path, capture_output=True)
        console.print("[green]✓[/] Node dependencies installed")

    # R package
    elif (path / "DESCRIPTION").exists():
        console.print("[dim]R package detected (deps managed by renv/pak)[/]")


@app.command(
    "cleanup",
    epilog="""
[bold]Examples:[/]
  ait feature cleanup           # Interactive cleanup
  ait feature cleanup --dry-run # Preview what would be deleted
  ait feature cleanup --force   # Delete without confirmation
""",
)
def feature_cleanup(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be deleted."
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Delete without confirmation."
    ),
) -> None:
    """Clean up merged feature branches and their worktrees."""
    repo_root = _get_repo_root()
    if not repo_root:
        console.print("[red]Error:[/] Not in a git repository")
        raise typer.Exit(1)

    features = _get_feature_branches()
    merged = [f for f in features if f.is_merged]

    if not merged:
        console.print("[green]No merged feature branches to clean up.[/]")
        return

    worktrees = _get_worktrees()
    worktree_map = {wt.branch: wt for wt in worktrees if wt.branch}

    console.print(f"[bold]Found {len(merged)} merged feature branches:[/]\n")

    table = Table(border_style="yellow")
    table.add_column("Branch", style="bold")
    table.add_column("Worktree")

    for feature in merged:
        worktree = worktree_map.get(feature.full_name)
        wt_path = str(worktree.path) if worktree else "[dim]-[/]"
        table.add_row(feature.full_name, wt_path)

    console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/]")
        return

    if not force:
        console.print()
        confirm = typer.confirm("Delete these branches?")
        if not confirm:
            console.print("[dim]Cancelled.[/]")
            return

    # Delete branches and worktrees
    for feature in merged:
        worktree = worktree_map.get(feature.full_name)

        # Remove worktree first if exists
        if worktree:
            console.print(f"[dim]Removing worktree: {worktree.path}[/]")
            _run_git(["worktree", "remove", str(worktree.path)])

        # Delete branch
        console.print(f"[dim]Deleting branch: {feature.full_name}[/]")
        _run_git(["branch", "-d", feature.full_name])

    console.print(f"\n[green]✓[/] Cleaned up {len(merged)} merged branches.")
