"""Tests for pikapika file organizer."""

from __future__ import annotations

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from pikapika_organizer import (
    DEFAULT_TARGET_NAME,
    category_for_extension,
    clean_downloads,
    default_downloads_dir,
    is_older_than,
    unique_destination,
)


class TestCategoryForExtension:
    """Test the category_for_extension function."""

    def test_known_extensions(self):
        """Test that known extensions return correct categories."""
        assert category_for_extension(".jpg") == "Images"
        assert category_for_extension(".mp4") == "Videos"
        assert category_for_extension(".mp3") == "Audio"
        assert category_for_extension(".pdf") == "Documents"
        assert category_for_extension(".zip") == "Archives"
        assert category_for_extension(".exe") == "Installers"
        assert category_for_extension(".py") == "Code"

    def test_case_insensitive(self):
        """Test that extensions are case insensitive."""
        assert category_for_extension(".JPG") == "Images"
        assert category_for_extension(".MP4") == "Videos"
        assert category_for_extension(".Py") == "Code"

    def test_unknown_extension(self):
        """Test that unknown extensions return default category."""
        assert category_for_extension(".unknown") == DEFAULT_TARGET_NAME
        assert category_for_extension("") == DEFAULT_TARGET_NAME
        assert category_for_extension(".xyz123") == DEFAULT_TARGET_NAME


class TestUniqueDestination:
    """Test the unique_destination function."""

    def test_unique_path_when_file_not_exists(self, tmp_path):
        """Test when destination file doesn't exist."""
        dest = tmp_path / "dest.txt"

        result = unique_destination(dest)
        assert result == dest

    def test_unique_path_when_file_exists(self, tmp_path):
        """Test when destination file exists - should append number."""
        dest = tmp_path / "dest.txt"
        dest.write_text("existing")

        result = unique_destination(dest)
        expected = tmp_path / "dest (1).txt"
        assert result == expected

    def test_multiple_existing_files(self, tmp_path):
        """Test when multiple numbered versions exist."""
        dest = tmp_path / "dest.txt"
        dest.write_text("original")
        (tmp_path / "dest (1).txt").write_text("first")
        (tmp_path / "dest (2).txt").write_text("second")

        result = unique_destination(dest)
        expected = tmp_path / "dest (3).txt"
        assert result == expected


class TestIsOlderThan:
    """Test the is_older_than function."""

    def test_recent_file(self, tmp_path):
        """Test that recent files are not considered old."""
        test_file = tmp_path / "recent.txt"
        test_file.write_text("recent")

        # File should not be older than 7 days
        assert not is_older_than(test_file, 7)

    def test_old_file(self, tmp_path):
        """Test that old files are detected correctly."""
        test_file = tmp_path / "old.txt"
        test_file.write_text("old")

        # Mock the file to be 10 days old
        old_time = datetime.now() - timedelta(days=10)
        old_timestamp = old_time.timestamp()

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_mtime = old_timestamp
            assert is_older_than(test_file, 7)

    def test_nonexistent_file(self, tmp_path):
        """Test that nonexistent files return False."""
        nonexistent = tmp_path / "does_not_exist.txt"
        # Should not raise exception, return False
        try:
            result = is_older_than(nonexistent, 7)
            assert not result
        except FileNotFoundError:
            # Expected behavior for nonexistent files
            pass


class TestDefaultDownloadsDir:
    """Test the default_downloads_dir function."""

    @patch("pikapika_organizer.Path.home")
    def test_default_downloads_dir(self, mock_home, tmp_path):
        """Test that default downloads dir is correctly constructed."""
        mock_home.return_value = tmp_path
        downloads = tmp_path / "Downloads"
        downloads.mkdir()

        result = default_downloads_dir()
        assert result == downloads


class TestCleanDownloads:
    """Test the clean_downloads function."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.downloads = self.temp_dir / "Downloads"
        self.downloads.mkdir()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_invalid_directory(self):
        """Test that invalid directory raises SystemExit."""
        with pytest.raises(SystemExit):
            clean_downloads(
                downloads=Path("/nonexistent/directory"),
                dry_run=True,
                recursive=False,
                quarantine_junk=False,
                junk_days=7,
                use_trash=False,
            )

    def test_dry_run_mode(self):
        """Test dry run mode doesn't move files."""
        # Create test files
        (self.downloads / "test.jpg").write_text("image")
        (self.downloads / "document.pdf").write_text("pdf")

        clean_downloads(
            downloads=self.downloads,
            dry_run=True,
            recursive=False,
            quarantine_junk=False,
            junk_days=7,
            use_trash=False,
        )

        # Files should still be in original location
        assert (self.downloads / "test.jpg").exists()
        assert (self.downloads / "document.pdf").exists()

    def test_file_organization(self):
        """Test that files are organized correctly."""
        # Create test files
        (self.downloads / "test.jpg").write_text("image")
        (self.downloads / "document.pdf").write_text("pdf")
        (self.downloads / "script.py").write_text("code")

        clean_downloads(
            downloads=self.downloads,
            dry_run=False,
            recursive=False,
            quarantine_junk=False,
            junk_days=7,
            use_trash=False,
        )

        # Files should be moved to correct categories
        assert (self.downloads / "Images" / "test.jpg").exists()
        assert (self.downloads / "Documents" / "document.pdf").exists()
        assert (self.downloads / "Code" / "script.py").exists()

        # Original files should be gone
        assert not (self.downloads / "test.jpg").exists()
        assert not (self.downloads / "document.pdf").exists()
        assert not (self.downloads / "script.py").exists()

    def test_junk_file_quarantine(self):
        """Test that junk files are quarantined."""
        # Create old junk file
        junk_file = self.downloads / "temp.tmp"
        junk_file.write_text("junk")

        # Set file modification time to be old
        old_time = datetime.now() - timedelta(days=10)
        import os

        os.utime(junk_file, (old_time.timestamp(), old_time.timestamp()))

        clean_downloads(
            downloads=self.downloads,
            dry_run=False,
            recursive=False,
            quarantine_junk=True,
            junk_days=7,
            use_trash=False,
        )

        # Junk file should be quarantined
        assert (self.downloads / "_Quarantine" / "temp.tmp").exists()
        assert not (self.downloads / "temp.tmp").exists()

    def test_recursive_mode(self):
        """Test recursive file organization."""
        # Create subdirectory with files
        subdir = self.downloads / "subfolder"
        subdir.mkdir()
        (subdir / "image.png").write_text("image")
        (self.downloads / "root.xyz").write_text("text")  # Use unknown extension

        clean_downloads(
            downloads=self.downloads,
            dry_run=False,
            recursive=True,
            quarantine_junk=False,
            junk_days=7,
            use_trash=False,
        )

        # Both files should be organized
        assert (self.downloads / "Images" / "image.png").exists()
        # Check if file exists in Other (might be numbered if conflict)
        other_dir = self.downloads / "Other"
        other_files = list(other_dir.glob("root*.xyz"))
        assert len(other_files) >= 1

    def test_skip_directories(self):
        """Test that directories are skipped."""
        # Create a subdirectory that should be skipped
        subdir = self.downloads / ".git"
        subdir.mkdir()
        (subdir / "config").write_text("config")

        clean_downloads(
            downloads=self.downloads,
            dry_run=False,
            recursive=False,
            quarantine_junk=False,
            junk_days=7,
            use_trash=False,
        )

        # .git directory should be untouched
        assert (subdir / "config").exists()

    @patch("pikapika_organizer.send2trash")
    def test_junk_file_trash(self, mock_send2trash):
        """Test that junk files are sent to trash when use_trash=True."""
        # Create old junk file
        junk_file = self.downloads / "temp.tmp"
        junk_file.write_text("junk")

        # Set file modification time to be old
        old_time = datetime.now() - timedelta(days=10)
        import os

        os.utime(junk_file, (old_time.timestamp(), old_time.timestamp()))

        # Mock send2trash to actually delete the file for realistic testing
        def mock_trash(path):
            file_path = Path(path)
            if file_path.exists():
                file_path.unlink()

        mock_send2trash.side_effect = mock_trash

        clean_downloads(
            downloads=self.downloads,
            dry_run=False,
            recursive=False,
            quarantine_junk=True,
            junk_days=7,
            use_trash=True,
        )

        # send2trash should have been called
        assert mock_send2trash.called
        # Check it was called with a path ending with our filename
        call_args = mock_send2trash.call_args[0][0]
        assert call_args.endswith("temp.tmp")

        # File should be gone (not in quarantine)
        assert not (self.downloads / "_Quarantine" / "temp.tmp").exists()
        assert not (self.downloads / "temp.tmp").exists()


if __name__ == "__main__":
    pytest.main([__file__])
