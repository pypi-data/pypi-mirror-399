import click

from bodhiq.utils import INDEX_NAME, client, wait_task


def reset_index(wait=True):
    """Delete the entire index."""
    task = client.delete_index(INDEX_NAME)
    wait_task(task, wait)
    click.echo("🧹 All memories deleted.")
