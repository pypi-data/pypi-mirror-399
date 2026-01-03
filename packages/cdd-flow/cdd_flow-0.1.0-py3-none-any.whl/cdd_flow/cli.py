"""
cdd-flow: AI-Assisted Development Delivery System

Main CLI entry point.
"""

import click

from cdd_flow.commands import (
    abandon,
    checkpoint,
    complete,
    ctx,
    history,
    land,
    start,
    status,
    undo,
    verify,
)


@click.group()
@click.version_option(version="0.1.0", prog_name="cdd-flow")
@click.option("--project", "-p", type=click.Path(exists=True), help="Project directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.pass_context
def main(ctx, project, verbose, quiet):
    """AI-Assisted Development Delivery System.
    
    Orchestrates the artifact handoff loop for AI-assisted development.
    
    \b
    Core loop:
      ctx          Generate context for AI
      land         Integrate artifact from Downloads
      verify       Run verification gates
      checkpoint   Commit verified state
    
    \b
    Session management:
      start        Begin a tracked session
      status       Show current state
      complete     End session successfully
      abandon      Abort and revert to baseline
    
    \b
    Recovery:
      undo         Revert last landing
      history      Show iterations and checkpoints
    """
    ctx.ensure_object(dict)
    ctx.obj["project"] = project
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Core loop commands
main.add_command(ctx.ctx)
main.add_command(land.land)
main.add_command(verify.verify)
main.add_command(checkpoint.checkpoint)

# Session commands
main.add_command(start.start)
main.add_command(status.status)
main.add_command(complete.complete)
main.add_command(abandon.abandon)

# Recovery commands
main.add_command(undo.undo)
main.add_command(history.history)


if __name__ == "__main__":
    main()
