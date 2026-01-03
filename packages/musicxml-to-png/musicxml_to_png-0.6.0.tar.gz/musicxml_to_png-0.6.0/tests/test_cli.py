"""Unit tests for CLI interface."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from music21 import stream, note, instrument

from musicxml_to_png.cli import main


@pytest.fixture
def sample_musicxml_file(tmp_path):
    """Create a sample MusicXML file for testing."""
    score = stream.Score()
    part = stream.Part()
    part.append(instrument.Violin())
    n = note.Note("C4")
    n.quarterLength = 1.0
    part.append(n)
    score.append(part)
    
    input_path = tmp_path / "test.mxl"
    score.write("musicxml", input_path)
    return input_path


class TestCLIArguments:
    """Test CLI argument parsing and handling."""

    def test_basic_conversion(self, sample_musicxml_file, tmp_path, capsys):
        """Test basic conversion with required arguments."""
        with patch("sys.argv", ["musicxml-to-png", str(sample_musicxml_file)]):
            main()
        
        # Check that output file was created
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()
        
        # Check success message
        captured = capsys.readouterr()
        assert "Successfully created visualization" in captured.out

    def test_custom_output_path(self, sample_musicxml_file, tmp_path, capsys):
        """Test conversion with custom output path."""
        output_path = tmp_path / "custom.png"
        
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "-o", str(output_path),
        ]):
            main()
        
        assert output_path.exists()

    def test_custom_title(self, sample_musicxml_file, tmp_path, capsys):
        """Test conversion with custom title."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--title", "My Test Composition",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_no_grid_option(self, sample_musicxml_file, tmp_path, capsys):
        """Test --no-grid option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--no-grid",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_minimal_mode(self, sample_musicxml_file, tmp_path, capsys):
        """Test --minimal option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--minimal",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_no_rehearsal_marks_flag(self, sample_musicxml_file, tmp_path, capsys):
        """Test --no-rehearsal-marks option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--no-rehearsal-marks",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_no_rehearsal_marks_flag_bigband_fixture(self, tmp_path, capsys):
        """Bigband fixture should convert with rehearsal marks suppressed."""
        fixture_path = Path(__file__).parent / "fixtures" / "test-bigband-1.mxl"
        if not fixture_path.exists():
            pytest.skip("test-bigband-1.mxl fixture missing")

        output_path = tmp_path / "bigband.png"

        with patch("sys.argv", [
            "musicxml-to-png",
            str(fixture_path),
            "--no-rehearsal-marks",
            "-o",
            str(output_path),
        ]):
            main()

    def test_connection_tuning_flags(self, sample_musicxml_file, tmp_path, monkeypatch):
        """Advanced connection tuning flags should pass through to converter."""
        captured = {}

        def fake_convert_musicxml_to_png(**kwargs):
            captured.update(kwargs)

            class DummyPath(Path):
                _flavour = Path(".")._flavour

            out = tmp_path / "out.png"
            out.touch()
            return DummyPath(str(out))

        monkeypatch.setattr("musicxml_to_png.cli.convert_musicxml_to_png", fake_convert_musicxml_to_png)

        argv = [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--show-connections",
            "--connection-max-gap",
            "2.5",
            "--connection-alpha",
            "0.5",
            "--connection-min-alpha",
            "0.2",
            "--connection-fade-start",
            "3",
            "--connection-fade-end",
            "6",
            "--connection-linewidth",
            "1.5",
            "--connection-curve-height-factor",
            "3.0",
        ]
        with patch("sys.argv", argv):
            main()

        assert captured.get("show_connections") is True
        assert captured.get("connection_max_gap") == 2.5
        assert captured.get("connection_alpha") == 0.5
        assert captured.get("connection_min_alpha") == 0.2
        assert captured.get("connection_fade_start") == 3
        assert captured.get("connection_fade_end") == 6
        assert captured.get("connection_linewidth") == 1.5
        assert captured.get("connection_curve_height_factor") == 3.0
        assert (tmp_path / "out.png").exists()

    def test_no_legend_flag(self, sample_musicxml_file, tmp_path, capsys):
        """Test --no-legend option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--no-legend",
        ]):
            main()

        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_no_title_flag(self, sample_musicxml_file, tmp_path, capsys):
        """Test --no-title option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--no-title",
        ]):
            main()

        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_time_stretch_option(self, sample_musicxml_file, tmp_path, capsys):
        """Test --time-stretch option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--time-stretch",
            "1.2",
        ]):
            main()

        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_fig_width_option(self, sample_musicxml_file, tmp_path, capsys):
        """Test --fig-width option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--fig-width",
            "20",
        ]):
            main()

        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_dpi_option(self, sample_musicxml_file, tmp_path, capsys):
        """Test --dpi option."""
        output_path = sample_musicxml_file.with_suffix(".png")
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--dpi",
            "180",
            "-o",
            str(output_path),
        ]):
            main()

        assert output_path.exists()
        from PIL import Image
        dpi_info = Image.open(output_path).info.get("dpi")
        assert dpi_info is not None
        assert abs(dpi_info[0] - 180) < 1 and abs(dpi_info[1] - 180) < 1

    def test_ensemble_option(self, sample_musicxml_file, tmp_path, capsys):
        """Test --ensemble option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--ensemble", "bigband",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_verbose_mode(self, sample_musicxml_file, tmp_path, capsys):
        """Test --verbose option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--verbose",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_short_verbose_flag(self, sample_musicxml_file, tmp_path, capsys):
        """Test -v short flag for verbose."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "-v",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_version_flag(self, capsys):
        """--version should print version and exit cleanly."""
        with patch("sys.argv", ["musicxml-to-png", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "musicxml-to-png" in captured.out
        assert any(char.isdigit() for char in captured.out)


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_file_not_found_error(self, tmp_path, capsys):
        """Test error handling for missing file."""
        non_existent = tmp_path / "nonexistent.mxl"
        
        with patch("sys.argv", ["musicxml-to-png", str(non_existent)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower()

    def test_invalid_file_extension_warning(self, tmp_path, capsys):
        """Test warning for non-standard file extension."""
        # Create a file with non-standard extension
        test_file = tmp_path / "test.txt"
        test_file.write_text("not musicxml")
        
        # Create a valid MusicXML file with .xml extension for comparison
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        xml_file = tmp_path / "test.xml"
        score.write("musicxml", xml_file)
        
        with patch("sys.argv", ["musicxml-to-png", str(xml_file)]):
            main()
        
        # Should still work, but might show warning
        output_file = xml_file.with_suffix(".png")
        assert output_file.exists()

    def test_invalid_musicxml_error(self, tmp_path, capsys):
        """Test error handling for invalid MusicXML."""
        invalid_file = tmp_path / "invalid.mxl"
        invalid_file.write_text("This is not valid MusicXML")
        
        with patch("sys.argv", ["musicxml-to-png", str(invalid_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "failed" in captured.err.lower()

    def test_empty_musicxml_error(self, tmp_path, capsys):
        """Test error handling for empty MusicXML (no notes)."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        # No notes
        score.append(part)
        
        empty_file = tmp_path / "empty.mxl"
        score.write("musicxml", empty_file)
        
        with patch("sys.argv", ["musicxml-to-png", str(empty_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "no notes" in captured.err.lower()

    def test_minimal_mode_overrides_title(self, sample_musicxml_file, tmp_path, capsys):
        """Test that --minimal mode ignores title."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--minimal",
            "--title", "This should be ignored",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()

    def test_transparent_flag(self, sample_musicxml_file, tmp_path, capsys):
        """Test --transparent option."""
        with patch("sys.argv", [
            "musicxml-to-png",
            str(sample_musicxml_file),
            "--transparent",
        ]):
            main()
        
        output_file = sample_musicxml_file.with_suffix(".png")
        assert output_file.exists()
