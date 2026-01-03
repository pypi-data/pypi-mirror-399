import hashlib
import logging
from datetime import datetime, timezone

import meilisearch

# ---------------- CONFIG ----------------
MEILI_URL = "http://meilisearch.localhost"
MEILI_API_KEY = None
INDEX_NAME = "memories"

# ---------------- LOGGER ----------------
logger = logging.getLogger("mem_cli")
logger.setLevel(logging.INFO)  # default
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# ---------------- CLIENT ----------------
client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)


# ---------------- HELPERS ----------------
def wait_task(task, wait=True):
    """
    Wait for a Meilisearch TaskInfo object to complete.
    If logger level is DEBUG, print full task info.
    """
    if not wait:
        return task
    task_info = client.wait_for_task(task.task_uid)
    if logger.level <= logging.DEBUG:
        logger.debug(f"Full TaskInfo: {task_info}")
    return task_info


def generate_id(text, tags):
    """
    Generate SHA-256 hash for a memory based on text + tags.
    Ensures idempotency.
    """
    hash_input = text + "|" + "|".join(sorted(tags))
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


def utc_now_iso():
    """Return current UTC datetime with timezone info as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def get_index(wait=True):
    """
    Get or create the Meilisearch index with proper settings.
    Configures searchable and filterable attributes.
    """
    try:
        index = client.get_index(INDEX_NAME)
        logger.debug("Index found.")
    except meilisearch.errors.MeilisearchApiError:
        logger.debug("Index not found, creating...")
        index = client.create_index(INDEX_NAME, {"primaryKey": "id"})
        wait_task(index, wait)

    # Apply searchable attributes
    task = index.update_searchable_attributes(["text", "tags"])
    wait_task(task, wait)

    # Apply filterable attributes
    task = index.update_filterable_attributes(["tags"])
    wait_task(task, wait)

    return client.get_index(INDEX_NAME)
