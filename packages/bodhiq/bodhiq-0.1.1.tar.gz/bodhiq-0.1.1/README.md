# Bodhiq

**Bodhiq** is a personal memory and search CLI tool that helps you **store, search, and manage your thoughts, notes, and memories**.  
  Bodhiq combines **fast search, TF-IDF semantic matching**, and **tags** to make finding your memories easy and intelligent.

---

## Features

- **Add memories:** Quickly save notes with optional tags.
- **Query memories:** Search your memories using keywords or semantic TF-IDF search.
- **Tag filtering:** Organize and filter your memories with tags.
- **Delete memories:** Remove memories by ID.
- **List memories:** View all stored memories in a clean table.
- **Reset index:** Clear all stored memories (with confirmation).
- **Optional TF-IDF search:** Find relevant results even if the query doesn't match exactly.
- **Debug mode:** See detailed logs and Meilisearch task info.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/amanshaw4511/bodhiq.git
cd bodhiq
```

2. Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Make sure you have **Meilisearch** running locally:

```bash
docker run -it --rm -p 7700:7700 getmeili/meilisearch
```

---

## Usage

```bash
# Add a memory
bodhiq add "My name is Aman" --tag personal --tag intro

# Query a memory
bodhiq q "what is my name"

# Query using TF-IDF
bodhiq q "my name" --tfidf

# Delete a memory
bodhiq rm <memory_id>

# List all memories
bodhiq ls

# Reset all memories
bodhiq reset
```

### Flags

- `--wait / --no-wait` : Wait for Meilisearch tasks to complete (default: wait)
- `--debug` : Enable debug output to see full task info
- `--tag` : Add tags or filter memories by tags
- `--tfidf` : Enable TF-IDF based semantic search

---

## CLI Command Examples

```bash
# Add memory
bodhiq add "Learn Python CLI tools" --tag coding

# Search memory
bodhiq q "python tools" --tag coding --tfidf

# List all memories
bodhiq ls

# Delete a memory
bodhiq rm a1b2c3d4e5f6
```

---

## Architecture

Bodhiq is split into modular components:

- `core/` : Core logic (add, query, delete, list, reset)
- `utils.py` : Utilities (Meilisearch client, logging, helper functions)
- `cli.py` : CLI entry point using Click
- `requirements.txt` : Python dependencies
- `README.md` : Project documentation

---

## License

Bodhiq is open-source under the **MIT License**.  

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

---

## Inspiration

The name **Bodhiq** comes from *Bodha* (knowledge/awareness) + IQ, representing a **smart, aware, and intelligent memory assistant**.

---

**Enjoy using Bodhiq, your personal memory companion!**

