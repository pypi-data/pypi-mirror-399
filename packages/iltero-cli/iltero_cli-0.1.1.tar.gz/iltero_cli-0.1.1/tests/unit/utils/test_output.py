"""Tests for output utilities module."""

from unittest.mock import Mock, patch

from iltero.utils.output import (
    OutputFormat,
    format_cell_value,
    format_output,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
    print_warning,
    print_yaml,
)


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_output_format_values(self):
        """Test OutputFormat enum has expected values."""
        assert OutputFormat.TABLE.value == "table"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.YAML.value == "yaml"

    def test_output_format_is_string(self):
        """Test OutputFormat is a string enum."""
        assert isinstance(OutputFormat.TABLE, str)
        assert OutputFormat.TABLE == "table"


class TestFormatCellValue:
    """Tests for format_cell_value function."""

    def test_none_value(self):
        """Test None value formatting."""
        result = format_cell_value(None)
        assert "—" in result  # em dash for None

    def test_bool_true(self):
        """Test True value formatting."""
        result = format_cell_value(True)
        assert "✓" in result

    def test_bool_false(self):
        """Test False value formatting."""
        result = format_cell_value(False)
        assert "✗" in result

    def test_list_value(self):
        """Test list value formatting."""
        result = format_cell_value(["a", "b", "c"])
        assert "a" in result
        assert "b" in result
        assert "c" in result

    def test_empty_list(self):
        """Test empty list formatting."""
        result = format_cell_value([])
        assert "—" in result

    def test_dict_value(self):
        """Test dict value formatting."""
        result = format_cell_value({"key": "value"})
        assert "key" in result
        assert "value" in result

    def test_string_value(self):
        """Test string value formatting."""
        result = format_cell_value("hello world")
        assert result == "hello world"

    def test_int_value(self):
        """Test integer value formatting."""
        result = format_cell_value(42)
        assert result == "42"


class TestPrintJson:
    """Tests for print_json function."""

    def test_print_json_dict(self, capsys):
        """Test printing dict as JSON."""
        with patch("iltero.utils.output.console") as mock_console:
            print_json({"name": "test", "value": 123})
            mock_console.print_json.assert_called_once()

    def test_print_json_list(self, capsys):
        """Test printing list as JSON."""
        with patch("iltero.utils.output.console") as mock_console:
            print_json([{"id": 1}, {"id": 2}])
            mock_console.print_json.assert_called_once()

    def test_print_json_with_to_dict(self):
        """Test printing object with to_dict method."""
        mock_obj = Mock()
        mock_obj.to_dict.return_value = {"key": "value"}

        with patch("iltero.utils.output.console") as mock_console:
            print_json(mock_obj)
            mock_console.print_json.assert_called_once()
            mock_obj.to_dict.assert_called_once()


class TestPrintYaml:
    """Tests for print_yaml function."""

    def test_print_yaml_dict(self):
        """Test printing dict as YAML."""
        with patch("iltero.utils.output.console") as mock_console:
            print_yaml({"name": "test"})
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "name:" in call_args
            assert "test" in call_args

    def test_print_yaml_with_to_dict(self):
        """Test printing object with to_dict method."""
        mock_obj = Mock()
        mock_obj.to_dict.return_value = {"key": "value"}

        with patch("iltero.utils.output.console"):
            print_yaml(mock_obj)
            mock_obj.to_dict.assert_called_once()


class TestPrintTable:
    """Tests for print_table function."""

    def test_print_table_empty_data(self):
        """Test printing empty data."""
        with patch("iltero.utils.output.console") as mock_console:
            print_table([])
            mock_console.print.assert_called_once()
            assert "No data" in str(mock_console.print.call_args)

    def test_print_table_single_dict(self):
        """Test printing single dict as table."""
        with patch("iltero.utils.output.console") as mock_console:
            print_table({"name": "test", "id": 1})
            mock_console.print.assert_called()

    def test_print_table_list_of_dicts(self):
        """Test printing list of dicts as table."""
        data = [
            {"name": "first", "id": 1},
            {"name": "second", "id": 2},
        ]
        with patch("iltero.utils.output.console") as mock_console:
            print_table(data, title="Test Table")
            mock_console.print.assert_called()

    def test_print_table_with_columns(self):
        """Test printing table with custom columns."""
        data = [{"name": "test", "description": "desc", "extra": "ignored"}]
        columns = [("name", "Name"), ("description", "Description")]

        with patch("iltero.utils.output.console") as mock_console:
            print_table(data, columns=columns)
            mock_console.print.assert_called()


class TestFormatOutput:
    """Tests for format_output function."""

    def test_format_output_table(self):
        """Test format_output with table format."""
        with patch("iltero.utils.output.print_table") as mock_print:
            format_output(
                [{"id": 1}],
                format_type=OutputFormat.TABLE,
                title="Test",
            )
            mock_print.assert_called_once()

    def test_format_output_json(self):
        """Test format_output with json format."""
        with patch("iltero.utils.output.print_json") as mock_print:
            format_output({"id": 1}, format_type=OutputFormat.JSON)
            mock_print.assert_called_once()

    def test_format_output_yaml(self):
        """Test format_output with yaml format."""
        with patch("iltero.utils.output.print_yaml") as mock_print:
            format_output({"id": 1}, format_type=OutputFormat.YAML)
            mock_print.assert_called_once()


class TestMessagePrinting:
    """Tests for message printing functions."""

    def test_print_success(self):
        """Test print_success output."""
        with patch("iltero.utils.output.console") as mock_console:
            print_success("Operation completed")
            mock_console.print.assert_called_once()
            call_args = str(mock_console.print.call_args)
            assert "✓" in call_args
            assert "Operation completed" in call_args

    def test_print_error(self):
        """Test print_error output."""
        with patch("iltero.utils.output.console") as mock_console:
            print_error("Something failed")
            mock_console.print.assert_called_once()
            call_args = str(mock_console.print.call_args)
            assert "✗" in call_args
            assert "Something failed" in call_args

    def test_print_warning(self):
        """Test print_warning output."""
        with patch("iltero.utils.output.console") as mock_console:
            print_warning("Caution advised")
            mock_console.print.assert_called_once()
            call_args = str(mock_console.print.call_args)
            assert "⚠" in call_args
            assert "Caution advised" in call_args

    def test_print_info(self):
        """Test print_info output."""
        with patch("iltero.utils.output.console") as mock_console:
            print_info("Information message")
            mock_console.print.assert_called_once()
            call_args = str(mock_console.print.call_args)
            assert "ℹ" in call_args
            assert "Information message" in call_args
