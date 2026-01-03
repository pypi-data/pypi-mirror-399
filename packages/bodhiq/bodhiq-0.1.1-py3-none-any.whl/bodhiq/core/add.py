import click

from bodhiq.utils import generate_id, get_index, utc_now_iso, wait_task


def remember_memory(text, tags, wait=True):
    """Add a memory, idempotent via SHA-256 hash."""
    index = get_index(wait)
    doc_id = generate_id(text, tags)
    doc = {
        "id": doc_id,
        "text": text,
        "tags": list(tags),
        "created_at": utc_now_iso(),
    }
    task = index.add_documents([doc])
    wait_task(task, wait)
    click.echo(f"✅ Remembered (id={doc_id[:12]})")
