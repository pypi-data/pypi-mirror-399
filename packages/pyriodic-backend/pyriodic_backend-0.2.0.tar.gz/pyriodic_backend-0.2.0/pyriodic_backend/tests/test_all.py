import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
from freezegun import freeze_time

from pyriodic_backend.backend import FileJSONBackend, InMemoryJSONBackend
from pyriodic_backend.entities import HTMLFile, RegisteredMethod
from pyriodic_backend.pyriodic_backend import PyriodicBackend


@pytest.fixture
def test_html_file(tmp_path):
    template_file_path = f"{Path(__file__).cwd()}/pyriodic_backend/tests/test.html"
    with open(template_file_path, "r") as template_file:
        html_template = template_file.read()

    tmp_file_path = tmp_path / "test.html"
    with open(tmp_file_path, "w") as test_file:
        test_file.write(html_template)
    return HTMLFile(str(tmp_file_path))


@pytest.fixture
def another_test_html_file(tmp_path):
    template_file_path = f"{Path(__file__).cwd()}/pyriodic_backend/tests/test.html"
    with open(template_file_path, "r") as template_file:
        html_template = template_file.read()

    tmp_file_path = tmp_path / "second.html"
    with open(tmp_file_path, "w") as test_file:
        test_file.write(html_template)
    return HTMLFile(str(tmp_file_path))


class TestMethodRegistration:
    def test_function_signature(self):
        test_file = HTMLFile("file/path")

        def some_func():
            return "ok"

        registered_method = RegisteredMethod(
            html_file=test_file, tag_id="tag1", func=some_func, interval=1
        )
        expected_signature = "file/path;;;tag1;;;some_func"
        hash = hashlib.new("sha256")
        hash.update(expected_signature.encode())
        expected_signature_hash = hash.hexdigest()
        assert registered_method.signature() == expected_signature_hash

    def test_registering_method(self):
        test_file = HTMLFile("file/path")
        pyriodic_backend = PyriodicBackend(backend=InMemoryJSONBackend())
        tag_id = "tag1"

        def func():
            return "ok"

        pyriodic_backend.register(html_file=test_file, tag_id=tag_id, func=func)

        assert pyriodic_backend.registered_methods is not None
        assert pyriodic_backend.registered_methods[0].html_file == test_file
        assert pyriodic_backend.registered_methods[0].tag_id == "tag1"
        assert pyriodic_backend.registered_methods[0].func == func
        assert pyriodic_backend.registered_methods[0].interval == 1

    def test_changing_tag_value(self, test_html_file):
        pyriodic_backend = PyriodicBackend(backend=InMemoryJSONBackend())
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            assert "CHANGED" in test_file.read()

    def test_no_change_if_tag_not_found(self, test_html_file):
        pyriodic_backend = PyriodicBackend(backend=InMemoryJSONBackend())
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="nonexistent", func=lambda: "CHANGED"
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            assert "CHANGED" not in test_file.read()

    def test_registering_multiple_files(self, test_html_file, another_test_html_file):
        pyriodic_backend = PyriodicBackend(backend=InMemoryJSONBackend())
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="nonexistent",
            func=lambda: "CHANGED",
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            assert "CHANGED" in test_file.read()
        with open(another_test_html_file.abs_file_path, "r") as test_file:
            assert "CHANGED" not in test_file.read()

    def test_gracefully_handling_missing_html_file(self):
        pyriodic_backend = PyriodicBackend(backend=InMemoryJSONBackend())
        pyriodic_backend.register(
            html_file=HTMLFile("/nonexistent"),
            tag_id="change_me",
            func=lambda: "CHANGED",
        )
        pyriodic_backend.run()


class TestFileJSONBackend:
    @freeze_time("2025-01-01 10:00:00", tz_offset=0)
    def test_recording_backend(self, test_html_file, tmp_path):
        def change_tag():
            return "CHANGED"

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=change_tag
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            assert "CHANGED" in test_file.read()

        _, backend_value = list(backend._load_db().items())[0]

        assert backend_value == "2025-01-01T10:00:00+00:00"

    def test_recording_backend_and_updating(self, test_html_file, tmp_path):
        def change_tag():
            return "CHANGED"

        with freeze_time("2025-01-01 10:00:00", tz_offset=0):
            backend = FileJSONBackend(tmp_path / "db.json")
            pyriodic_backend = PyriodicBackend(backend)
            method = pyriodic_backend.register(
                html_file=test_html_file, tag_id="change_me", func=change_tag
            )
            pyriodic_backend.run()

        with freeze_time("2025-01-01 10:01:00", tz_offset=0):
            pyriodic_backend.run()
            backend_key, backend_value = list(backend._load_db().items())[0]
            assert backend_key == method.signature()
            assert backend_value == "2025-01-01T10:01:00+00:00"

    @freeze_time("2025-01-01 10:00:00", tz_offset=0)
    def test_getting_last_run_time(self, test_html_file, tmp_path):
        def change_tag():
            return "CHANGED"

        backend = FileJSONBackend()
        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        registered_method = pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=change_tag
        )
        pyriodic_backend.run()

        last_run_time = backend._get_last_run_time(registered_method)
        assert last_run_time == datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

    @freeze_time("2025-01-01 10:00:00", tz_offset=0)
    def test_getting_relative_last_run_time(self, test_html_file, tmp_path):
        def change_tag():
            return "CHANGED"

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        registered_method = pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=change_tag
        )
        pyriodic_backend.run()

        with freeze_time("2025-01-01 10:01:00", tz_offset=0):
            last_run_time = backend.get_minutes_since_last_run(registered_method)
            assert last_run_time == 1

    @freeze_time("2025-01-01 10:00:00", tz_offset=0)
    def test_getting_relative_last_run_time_after_multiple_seconds(
        self, test_html_file, tmp_path
    ):
        def change_tag():
            return "CHANGED"

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        registered_method = pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=change_tag, interval=10
        )
        pyriodic_backend.run()

        with freeze_time("2025-01-01 10:07:00", tz_offset=0):
            last_run_time = backend.get_minutes_since_last_run(registered_method)
            assert last_run_time == 7


class TestUpdatingTags:
    def test_changing_tag_value(self, test_html_file, tmp_path):
        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=lambda: "NEXT"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" in file_content
            assert "FINAL" in file_content

    def test_changing_tag_value_for_multiple_files(
        self, test_html_file, another_test_html_file, tmp_path
    ):
        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=lambda: "NEXT"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )

        pyriodic_backend.register(
            html_file=another_test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_second",
            func=lambda: "NEXT",
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_third",
            func=lambda: "FINAL",
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" in file_content
            assert "FINAL" in file_content
        with open(another_test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" in file_content
            assert "FINAL" in file_content

    def test_error_during_update_stops_all_changes(self, test_html_file, tmp_path):
        def broken_method():
            raise ValueError

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=broken_method
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" not in file_content
            assert "NEXT" not in file_content
            assert "FINAL" not in file_content

    def test_error_during_update_with_allowing_partial_updates(
        self, test_html_file, tmp_path
    ):
        def broken_method():
            raise ValueError

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend, allow_partial=True)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=broken_method
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "FINAL" in file_content

    def test_changing_tag_value_for_multiple_files_with_update_error(
        self, test_html_file, another_test_html_file, tmp_path
    ):
        def broken_method():
            raise ValueError

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=broken_method
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )

        pyriodic_backend.register(
            html_file=another_test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_second",
            func=lambda: "NEXT",
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_third",
            func=lambda: "FINAL",
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" not in file_content
            assert "NEXT" not in file_content
            assert "FINAL" not in file_content
        with open(another_test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" in file_content
            assert "FINAL" in file_content

    def test_changing_tag_value_for_multiple_files_with_update_error_and_partial_updates(
        self, test_html_file, another_test_html_file, tmp_path
    ):
        def broken_method():
            raise ValueError

        backend = FileJSONBackend(tmp_path / "db.json")
        pyriodic_backend = PyriodicBackend(backend, allow_partial=True)
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_second", func=broken_method
        )
        pyriodic_backend.register(
            html_file=test_html_file, tag_id="change_me_third", func=lambda: "FINAL"
        )

        pyriodic_backend.register(
            html_file=another_test_html_file, tag_id="change_me", func=lambda: "CHANGED"
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_second",
            func=lambda: "NEXT",
        )
        pyriodic_backend.register(
            html_file=another_test_html_file,
            tag_id="change_me_third",
            func=lambda: "FINAL",
        )
        pyriodic_backend.run()

        with open(test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" not in file_content
            assert "FINAL" in file_content
        with open(another_test_html_file.abs_file_path, "r") as test_file:
            file_content = test_file.read()
            assert "CHANGED" in file_content
            assert "NEXT" in file_content
            assert "FINAL" in file_content
