

### Blitzdb ported to newer Python3 with some minor changes (see diff)

Orignal source/license info and acknowelegement(s) at https://github.com/adewes/blitzdb and https://github.com/abilian/blitzdb3


# BlitzDB5

A modernized Python 3 port of **BlitzDB**, a lightweight document‑oriented database originally created by Andreas Dewes. BlitzDB5 preserves the original file‑based architecture, transactional indexing, and MongoDB‑style query API while updating the codebase for modern Python and performance.

> This project is a continuation/port of:
>
> * [https://github.com/adewes/blitzdb](https://github.com/adewes/blitzdb)
> * [https://github.com/abilian/blitzdb3](https://github.com/abilian/blitzdb3)

---

## ✨ Key Features

* ✅ Pure Python document database
* ✅ File‑based persistent storage
* ✅ Transactional writes with commit & rollback
* ✅ Automatic and manual indexing
* ✅ MongoDB‑style query language
* ✅ JSON / Pickle serialization
* ✅ Optional CJSON support
* ✅ Automatic primary‑key indexing
* ✅ Ephemeral (in‑memory) indexes for fast queries
* ✅ Configurable autocommit
* ✅ Optional in‑memory caching

---

## 📦 Installation

Install from source:

```bash
git clone https://gitlab.com/sunsolution/blitzdb5.git
cd blitzdb5
pip install .
```

Dependencies are managed via `pyproject.toml`:

* Python 3.9+
* `orjson`

---

## 🚀 Quick Start

```python
from blitzdb.backends.file.backend import Backend
from blitzdb.document import Document

class User(Document):
    pass

backend = Backend("./database")
backend.register(User)

user = User({"name": "Alice", "age": 30})
backend.save(user)

found = backend.get(User, {"name": "Alice"})
print(found)
```

---

## 🗄️ Supported Backends

BlitzDB5 supports multiple storage backends, allowing you to choose the right engine depending on your deployment needs:

### 1. File Backend (Default)

* ✅ Fully implemented and production‑ready
* ✅ Pure file‑based storage (no external services required)
* ✅ Transactional with persistent indexes
* ✅ JSON / Pickle / CJSON serialization
* ✅ Best choice for embedded and offline use

### 2. MongoDB Backend

* ✅ Uses MongoDB as the storage engine
* ✅ Supports native MongoDB querying and indexing
* ✅ Ideal for distributed and scalable deployments
* ⚠️ Requires a running MongoDB instance

### 3. SQL Backend (SQLAlchemy)

* ✅ Enables SQL database support via SQLAlchemy
* ✅ Works with PostgreSQL, MySQL, SQLite, etc.
* ✅ Allows structured relational storage with document interface
* ⚠️ Marked as experimental in some parts of the codebase

---

## ⚙️ Backend Setup & Example Commands

This section shows **exact setup patterns and usage examples** for each supported backend.

---

### ✅ File Backend (Default – No External Dependencies)

#### Setup

```python
from blitzdb.backends.file.backend import Backend
from blitzdb.document import Document

class User(Document):
    pass

backend = Backend("./database", serialize="json")
backend.register(User)
```

#### Save Data

```python
user = User({"name": "Alice", "age": 30})
backend.save(user)
backend.commit()
```

#### Query

```python
users = backend.filter(User, {"age": {"$gt": 18}})
```

#### Folder Created on Disk

```
./database/
├── config.json
├── user/
│   ├── objects/
│   └── indexes/
```

✅ **Best for:** Embedded apps, offline storage, local services, desktop software

---

### ✅ MongoDB Backend

#### Requirements

```bash
pip install pymongo
```

MongoDB must be running:

```bash
mongod --dbpath /data/db
```

#### Setup

```python
from blitzdb.backends.mongo.backend import Backend
from blitzdb.document import Document

class User(Document):
    pass

backend = Backend(
    db="blitzdb",
    host="localhost",
    port=27017
)

backend.register(User)
```

#### Save

```python
user = User({"name": "Alice"})
backend.save(user)
```

✅ **Best for:** Web apps, horizontal scaling, shared environments
⚠️ Requires external service

---

### ✅ SQL Backend (SQLAlchemy)

#### Requirements

```bash
pip install sqlalchemy psycopg2-binary
```

#### Setup (PostgreSQL Example)

```python
from blitzdb.backends.sql.backend import Backend
from blitzdb.document import Document

class User(Document):
    pass

backend = Backend(
    url="postgresql://user:password@localhost:5432/blitzdb"
)

backend.register(User)
```

#### Setup (SQLite Example)

```python
backend = Backend(url="sqlite:///blitzdb.sqlite")
```

✅ **Best for:** Data analysis, reporting, ACID‑strict systems
⚠️ Slower than Mongo for document workloads
⚠️ Schema translation overhead

---

## 📊 Backend Comparison Table

| Feature          | File Backend   | MongoDB Backend | SQL Backend |
| ---------------- | -------------- | --------------- | ----------- |
| External Server  | ❌ No           | ✅ Yes           | ✅ Yes       |
| Setup Complexity | ⭐ Very Low     | ⭐⭐ Medium       | ⭐⭐ Medium   |
| Performance      | ⭐⭐⭐ Fast Local | ⭐⭐⭐⭐ High       | ⭐⭐ Moderate |
| Scalability      | ⭐ Low‑Medium   | ⭐⭐⭐⭐ High       | ⭐⭐⭐ High    |
| Transactions     | ✅ Yes          | ✅ Yes           | ✅ Yes       |
| Index Support    | ✅ Native       | ✅ Native        | ✅ Native    |
| Offline Use      | ✅ Perfect      | ❌ No            | ❌ No        |
| Embedded Use     | ✅ Best         | ❌ No            | ⚠️ Limited  |
| Cloud‑Native     | ❌ No           | ✅ Yes           | ✅ Yes       |
| Operational Cost | ✅ None         | ❌ High          | ❌ Medium    |

---

## 🧠 Practical Opinions & Recommendations

### ✅ Choose **File Backend** when:

* You are building:

  * Desktop apps
  * Offline‑first systems
  * Embedded devices
  * CLI tools
* You want:

  * Zero dependencies
  * Maximum simplicity
  * Full control of disk layout

➡️ **This is the strongest and most "BlitzDB‑native" backend.**

---

### ✅ Choose **MongoDB Backend** when:

* You are building:

  * Web APIs
  * SaaS platforms
  * Multi‑instance deployments
* You need:

  * Horizontal scaling
  * Shared multi‑process access
  * Native cloud compatibility

➡️ **Best production backend for high‑traffic systems.**

---

### ✅ Choose **SQL Backend** when:

* You need:

  * Strong relational constraints
  * Heavy reporting
  * Existing SQL infrastructure
* You already depend on:

  * PostgreSQL / MySQL / SQLite

➡️ **Best for hybrid document + relational systems.**

⚠️ **Not ideal** for high‑frequency document writes.

---

## 🧠 Architecture Overview

| Component      | Purpose                         |
| -------------- | ------------------------------- |
| `Backend`      | Core database engine            |
| `Store`        | Object blob storage             |
| `Index`        | Persistent & ephemeral indexing |
| `QuerySet`     | Lazy query execution            |
| `Serializer`   | JSON / Pickle encoding          |
| `CacheManager` | Optional in‑memory caching      |

---

## 🗄 Storage Layout

```
database/
├── config.json
├── users/
│   ├── objects/
│   └── indexes/
│       ├── email/
│       └── pk/
```

---

## 🔁 Transactions

```python
backend.begin()
backend.save(user)
backend.commit()
```

Rollback:

```python
backend.rollback()
```

⚠️ Indexes created during a failed transaction are automatically rebuilt.

---

## 💾 Saving & Updating Documents

### Save

```python
backend.save(obj)
```

### Update

```python
backend.update(obj, set_fields={"age": 31})
```

---

## ❌ Deleting Documents

```python
backend.delete(obj)
```

---

## 🔍 Querying

```python
results = backend.filter(User, {"age": {"$gt": 18}})
```

Get exactly one:

```python
user = backend.get(User, {"name": "Alice"})
```

---

## 📊 Sorting

```python
backend.sort(User, keys, "age")
```

Supports multi‑field sorting and ascending/descending order.

---

## 📇 Indexing

### Create Index

```python
backend.create_index(User, "email", unique=True)
```

### Ephemeral Index

```python
backend.create_index(User, "last_login", ephemeral=True)
```

### Rebuild Index

```python
backend.rebuild_index("users", "email")
```

---

## ⚙️ Configuration (`config.json`)

Default configuration:

```json
{
  "indexes": {},
  "store_class": "transactional",
  "index_class": "transactional",
  "index_store_class": "basic",
  "serializer_class": "json",
  "autocommit": false
}
```

Set autocommit:

```python
backend.autocommit = True
```

⚠️ Autocommit forces a full index rebuild after every write.

---

## 🧬 Serialization

Supported formats:

* `json` (default)
* `pickle`
* `cjson` (if installed)

```python
backend = Backend("./db", serialize="pickle")
```

---

## 🧠 Caching

Enable caching:

```python
backend = Backend("./db", enable_caching=True)
```

FIFO cache with automatic eviction (default 1000 entries).

---

## ⚠️ Error Handling

### `DatabaseIndexError`

Raised if an index becomes corrupted. Recover using:

```python
backend.rebuild_index("collection", "field")
```

---

## 📜 License

MIT License

Original copyright © 2014 Andreas Dewes

---

## ✅ Project Status

* ✅ Fully functional file backend
* ✅ Python 3 modernized port
* ⚠️ Batch operations are partially implemented
* ⚠️ SQLAlchemy engine support is experimental

---

## 🧭 Summary

BlitzDB5 is ideal for:

* Embedded databases
* Local desktop apps
* Lightweight document storage
* Offline‑first systems

It provides a clean, Pythonic document store with strong indexing and transaction guarantees without requiring a server.
