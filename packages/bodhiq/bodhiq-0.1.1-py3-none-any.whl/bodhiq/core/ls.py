import click

from bodhiq.utils import get_index


def list_memories():
    """
    List all memories in the index with ID, text, tags, and creation date.
    """
    index = get_index(wait=True)
    # get_documents returns a dict with 'results' key
    response = index.get_documents({"limit": 1000})

    documents = response.results
    if not documents:
        click.echo("❌ No memories found.")
        return

    click.echo(f"{'ID':<12}  {'Text':<40}  {'Tags':<20}  {'Created At'}")
    click.echo("-" * 90)
    for doc in documents:
        doc = dict(doc)
        id_short = doc.get("id", "")[:8]
        text = doc.get("text", "")[:40]
        tags = ", ".join(doc.get("tags", []))[:20]
        created = doc.get("created_at", "")
        click.echo(f"{id_short:<12}  {text:<40}  {tags:<20}  {created}")
