import click

from bodhiq.utils import get_index, wait_task


def delete_memory(memory_id_prefix, wait=True):
    """
    Delete memory by ID prefix (first N letters).
    If multiple documents match, print them and exit.
    """
    index = get_index(wait)

    # Search all documents and filter by prefix
    documents = index.get_documents({"limit": 1000}).results
    matching_docs = [
        dict(doc)
        for doc in documents
        if dict(doc).get("id", "").startswith(memory_id_prefix)
    ]

    if not matching_docs:
        click.echo(f"❌ No memory found with ID starting with '{memory_id_prefix}'")
        return

    if len(matching_docs) > 1:
        click.echo(f"⚠️ Multiple memories match the prefix '{memory_id_prefix}':")
        for doc in matching_docs:
            id_short = doc["id"][:12]
            text = doc.get("text", "")[:40]
            tags = ", ".join(doc.get("tags", []))[:20]
            click.echo(f"- [{id_short}] {text} ({tags})")
        click.echo("Please use a more specific ID to delete.")
        return

    # Only one match, safe to delete
    doc = matching_docs[0]
    task = index.delete_document(doc["id"])
    wait_task(task, wait)
    click.echo(f"🗑️ Deleted memory {doc['id'][:12]}")
