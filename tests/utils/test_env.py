"""Tests for environment file utilities."""

from pathlib import Path


from dh.utils.env import get_env_var, read_env_file, update_env_var, write_env_file


class TestReadEnvFile:
    """Test suite for read_env_file function."""

    def test_read_existing_env_file(self, tmp_path: Path):
        """Test reading an existing .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\nKEY2=value2\n")

        result = read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_comments(self, tmp_path: Path):
        """Test reading .env file with comments."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# This is a comment\nKEY1=value1\n# Another comment\nKEY2=value2\n"
        )

        result = read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_empty_lines(self, tmp_path: Path):
        """Test reading .env file with empty lines."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\n\nKEY2=value2\n\n")

        result = read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_spaces(self, tmp_path: Path):
        """Test reading .env file with spaces around equals sign."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1 = value1\nKEY2= value2 \n")

        result = read_env_file(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_read_env_file_with_equals_in_value(self, tmp_path: Path):
        """Test reading .env file where value contains equals sign."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DATABASE_URL=postgresql://user:pass@localhost:5432/db?key=value\n"
        )

        result = read_env_file(env_file)

        assert result == {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db?key=value"
        }

    def test_read_nonexistent_env_file(self, tmp_path: Path):
        """Test reading a non-existent .env file."""
        env_file = tmp_path / ".env"

        result = read_env_file(env_file)

        assert result == {}


class TestWriteEnvFile:
    """Test suite for write_env_file function."""

    def test_write_env_file_new_file(self, tmp_path: Path):
        """Test writing to a new .env file."""
        env_file = tmp_path / ".env"
        env_vars = {"KEY1": "value1", "KEY2": "value2"}

        write_env_file(env_file, env_vars)

        assert env_file.exists()
        content = env_file.read_text()
        assert "KEY1=value1" in content
        assert "KEY2=value2" in content

    def test_write_env_file_overwrite(self, tmp_path: Path):
        """Test overwriting an existing .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("OLD_KEY=old_value\n")

        env_vars = {"NEW_KEY": "new_value"}
        write_env_file(env_file, env_vars, append=False)

        content = env_file.read_text()
        assert "NEW_KEY=new_value" in content
        assert "OLD_KEY" not in content

    def test_write_env_file_append(self, tmp_path: Path):
        """Test appending to an existing .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\n")

        env_vars = {"KEY2": "value2"}
        write_env_file(env_file, env_vars, append=True)

        content = env_file.read_text()
        assert "KEY1=value1" in content
        assert "KEY2=value2" in content


class TestUpdateEnvVar:
    """Test suite for update_env_var function."""

    def test_update_existing_key(self, tmp_path: Path):
        """Test updating an existing key in .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=old_value\nKEY2=value2\n")

        update_env_var(env_file, "KEY1", "new_value")

        result = read_env_file(env_file)
        assert result["KEY1"] == "new_value"
        assert result["KEY2"] == "value2"

    def test_update_nonexistent_key(self, tmp_path: Path):
        """Test adding a new key via update_env_var."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\n")

        update_env_var(env_file, "KEY2", "value2")

        result = read_env_file(env_file)
        assert result["KEY1"] == "value1"
        assert result["KEY2"] == "value2"

    def test_update_empty_file(self, tmp_path: Path):
        """Test updating when .env file doesn't exist."""
        env_file = tmp_path / ".env"

        update_env_var(env_file, "KEY1", "value1")

        result = read_env_file(env_file)
        assert result["KEY1"] == "value1"


class TestGetEnvVar:
    """Test suite for get_env_var function."""

    def test_get_existing_var(self, tmp_path: Path):
        """Test getting an existing environment variable."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\nKEY2=value2\n")

        result = get_env_var(env_file, "KEY1")

        assert result == "value1"

    def test_get_nonexistent_var(self, tmp_path: Path):
        """Test getting a non-existent environment variable."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\n")

        result = get_env_var(env_file, "KEY2")

        assert result is None

    def test_get_var_from_nonexistent_file(self, tmp_path: Path):
        """Test getting variable from non-existent file."""
        env_file = tmp_path / ".env"

        result = get_env_var(env_file, "KEY1")

        assert result is None
