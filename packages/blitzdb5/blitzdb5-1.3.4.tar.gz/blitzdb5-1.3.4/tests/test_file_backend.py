import unittest
from tempfile import TemporaryDirectory

try:
    import orjson  # noqa: F401

    ORJSON_AVAILABLE = True
except ModuleNotFoundError:
    ORJSON_AVAILABLE = False

if ORJSON_AVAILABLE:
    from blitzdb.backends.file.backend import Backend
    from blitzdb.document import Document
else:  # pragma: no cover - dependency missing in minimal envs
    Backend = None
    Document = object


class User(Document):
    pass


@unittest.skipUnless(ORJSON_AVAILABLE, "orjson dependency is required for file backend tests")
class FileBackendTests(unittest.TestCase):
    def test_json_roundtrip(self):
        """Default JSON serializer should persist and load documents."""
        with TemporaryDirectory() as tmpdir:
            backend = Backend(tmpdir)
            backend.register(User)

            user = User({"name": "Alice", "age": 30})
            backend.save(user)
            backend.commit()

            fetched = backend.get(User, {"pk": user.pk})
            self.assertEqual(fetched["name"], "Alice")
            self.assertEqual(fetched.pk, user.pk)

    def test_pickle_serializer_persists_across_instances(self):
        """
        Pickle serializer choice is written to config and respected by
        subsequent Backend instances.
        """
        with TemporaryDirectory() as tmpdir:
            backend = Backend(tmpdir, serialize="pickle")
            backend.register(User)

            user = User({"name": "Bob"})
            backend.save(user)
            backend.commit()

            # Primary index should be created for the correct collection.
            collection = backend.get_collection_for_cls(User)
            self.assertIn(User.get_pk_name(), backend.indexes[collection])

            # New instance should read serializer from config and decode data.
            backend_reopen = Backend(tmpdir)
            backend_reopen.register(User)

            fetched = backend_reopen.get(User, {"pk": user.pk})
            self.assertEqual(fetched["name"], "Bob")
            self.assertEqual(fetched.pk, user.pk)


if __name__ == "__main__":
    unittest.main()

