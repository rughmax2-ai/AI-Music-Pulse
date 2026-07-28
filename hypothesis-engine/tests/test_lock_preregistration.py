from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "lock_preregistration.py"
SPEC = importlib.util.spec_from_file_location("lock_preregistration", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
LOCKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOCKER)


class LockPreregistrationTests(unittest.TestCase):
    def test_lock_then_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prereg = Path(directory) / "test.yaml"
            prereg.write_text("experiment_id: exp_example\n", encoding="utf-8")

            digest = LOCKER.lock(prereg)

            self.assertEqual(len(digest), 64)
            self.assertEqual(LOCKER.verify(prereg), digest)

    def test_edit_invalidates_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prereg = Path(directory) / "test.yaml"
            prereg.write_text("threshold: 0.35\n", encoding="utf-8")
            LOCKER.lock(prereg)
            prereg.write_text("threshold: 0.20\n", encoding="utf-8")

            with self.assertRaises(LOCKER.LockError):
                LOCKER.verify(prereg)

    def test_existing_lock_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prereg = Path(directory) / "test.yaml"
            prereg.write_text("cycle_type: existence\n", encoding="utf-8")
            LOCKER.lock(prereg)

            with self.assertRaises(LOCKER.LockError):
                LOCKER.lock(prereg)

    def test_malformed_lock_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prereg = Path(directory) / "test.yaml"
            prereg.write_text("cycle_type: existence\n", encoding="utf-8")
            LOCKER.sidecar_path(prereg).write_text("not-a-digest\n", encoding="utf-8")

            with self.assertRaises(LOCKER.LockError):
                LOCKER.verify(prereg)

    def test_symlink_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.yaml"
            target.write_text("cycle_type: existence\n", encoding="utf-8")
            symlink = root / "link.yaml"
            symlink.symlink_to(target)

            with self.assertRaises(LOCKER.LockError):
                LOCKER.sha256_file(symlink)


if __name__ == "__main__":
    unittest.main()
