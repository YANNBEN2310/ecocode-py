import json
from pathlib import Path

from ecocode import CARBON_INTENSITY_ENV_VAR, eco_compare, eco_report, profile_callable
from ecocode.cli import main as cli_main
from ecocode.profiler import profile_callable as run_profile_callable
from ecocode.report import render_html_report
from ecocode.static_analysis import analyze_callable


TEST_CARBON_INTENSITY = 55.0


def loop_sum(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def builtin_sum(values):
    return sum(values)


def test_profile_callable_returns_value_and_metrics() -> None:
    values = list(range(1000))

    result_value, result_metrics = profile_callable(
        loop_sum,
        values,
        carbon_intensity=TEST_CARBON_INTENSITY,
    )

    assert result_value == sum(values)
    assert result_metrics.function_name == "loop_sum"
    assert result_metrics.execution_time_s >= 0
    assert result_metrics.cpu_time_s >= 0
    assert result_metrics.estimated_emissions_gco2 >= 0


def test_static_analysis_flags_range_len_loop() -> None:
    suggestions = analyze_callable(loop_sum)

    assert any(suggestion.rule_id == "loop-range-len" for suggestion in suggestions)


def test_eco_compare_returns_a_named_winner() -> None:
    comparison = eco_compare(
        loop_sum,
        builtin_sum,
        list(range(5000)),
        carbon_intensity=TEST_CARBON_INTENSITY,
    )

    assert comparison.better_function_name in {"loop_sum", "builtin_sum"}
    assert isinstance(comparison.summary(), str)


def test_eco_report_contains_key_sections() -> None:
    report = eco_report(loop_sum, list(range(1000)), carbon_intensity=TEST_CARBON_INTENSITY)

    assert "EcoCode execution report" in report
    assert "Function: loop_sum" in report
    assert "Suggestions:" in report


def test_cli_report_command_prints_a_report(capsys) -> None:
    exit_code = cli_main(
        [
            "report",
            "ecocode.sample_targets:sum_loop",
            "--arg",
            "[1, 2, 3]",
            "--carbon-intensity",
            str(TEST_CARBON_INTENSITY),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "EcoCode execution report" in captured.out
    assert "Function: sum_loop" in captured.out


def test_cli_compare_command_prints_a_summary(capsys) -> None:
    exit_code = cli_main(
        [
            "compare",
            "ecocode.sample_targets:sum_loop",
            "ecocode.sample_targets:sum_builtin",
            "--arg",
            "[1, 2, 3]",
            "--carbon-intensity",
            str(TEST_CARBON_INTENSITY),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Best implementation:" in captured.out
    assert "sum_loop vs sum_builtin" in captured.out


def test_cli_report_command_supports_json_output(capsys) -> None:
    exit_code = cli_main(
        [
            "report",
            "ecocode.sample_targets:sum_loop",
            "--arg",
            "[1, 2, 3]",
            "--carbon-intensity",
            str(TEST_CARBON_INTENSITY),
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["function_name"] == "sum_loop"
    assert payload["suggestions"][0]["rule_id"] == "loop-range-len"


def test_cli_compare_command_supports_json_output(capsys) -> None:
    exit_code = cli_main(
        [
            "compare",
            "ecocode.sample_targets:sum_loop",
            "ecocode.sample_targets:sum_builtin",
            "--arg",
            "[1, 2, 3]",
            "--carbon-intensity",
            str(TEST_CARBON_INTENSITY),
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["baseline"]["function_name"] == "sum_loop"
    assert payload["candidate"]["function_name"] == "sum_builtin"
    assert "better_function_name" in payload


def test_render_html_report_contains_key_sections() -> None:
    _, result = run_profile_callable(
        loop_sum,
        [1, 2, 3],
        carbon_intensity=TEST_CARBON_INTENSITY,
    )

    html_report = render_html_report(result)
    assert "<html" in html_report
    assert "EcoCode execution report" in html_report
    assert "Function: loop_sum" in html_report


def test_cli_report_command_writes_html_file(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "ecocode-report.html"

    exit_code = cli_main(
        [
            "report",
            "ecocode.sample_targets:sum_loop",
            "--arg",
            "[1, 2, 3]",
            "--carbon-intensity",
            str(TEST_CARBON_INTENSITY),
            "--format",
            "html",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert output_path.exists()
    assert "Wrote report to" in captured.out
    assert "EcoCode execution report" in output_path.read_text(encoding="utf-8")


def test_profile_callable_uses_environment_carbon_intensity(monkeypatch) -> None:
    monkeypatch.setenv(CARBON_INTENSITY_ENV_VAR, "123")

    _, result = profile_callable(loop_sum, [1, 2, 3])

    assert result.carbon_intensity_gco2_per_kwh == 123.0