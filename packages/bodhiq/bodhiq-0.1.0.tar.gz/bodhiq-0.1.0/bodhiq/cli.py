import logging

import click

from bodhiq.core.add import remember_memory
from bodhiq.core.ls import list_memories
from bodhiq.core.q import query_memory
from bodhiq.core.reset import reset_index
from bodhiq.core.rm import delete_memory
from bodhiq.utils import logger


@click.group()
@click.option("--debug", is_flag=True, default=False, help="Enable debug output")
@click.pass_context
def cli(ctx, debug):
    """Personal memory search CLI"""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")


# ---------------- COMMANDS ----------------
@click.command(name="add")
@click.argument("text")
@click.option("--tag", multiple=True, help="Add tags")
@click.option(
    "--wait/--no-wait", default=True, help="Wait for Meilisearch task to complete"
)
def add_cmd(text, tag, wait):
    remember_memory(text, tag, wait)


@click.command(name="q")
@click.argument("query")
@click.option("--tag", multiple=True, help="Filter by tags")
@click.option("--tfidf", is_flag=True, default=False, help="Use TF-IDF for query")
def query_cmd(query, tag, tfidf):
    """Search memories"""
    query_memory(query, tag, use_tfidf=tfidf)


@click.command(name="rm")
@click.argument("memory_id")
@click.option(
    "--wait/--no-wait", default=True, help="Wait for Meilisearch task to complete"
)
def delete_cmd(memory_id, wait):
    delete_memory(memory_id, wait)


@click.command(name="ls")
def list_cmd():
    """List all memories"""
    list_memories()


@click.command(name="reset")
@click.option(
    "--wait/--no-wait", default=True, help="Wait for Meilisearch task to complete"
)
@click.confirmation_option(prompt="⚠️ This will delete ALL memories. Continue?")
def reset_cmd(wait):
    reset_index(wait)


# Register commands
cli.add_command(add_cmd)
cli.add_command(query_cmd)
cli.add_command(delete_cmd)
cli.add_command(reset_cmd)
cli.add_command(list_cmd)


if __name__ == "__main__":
    cli(obj={})
