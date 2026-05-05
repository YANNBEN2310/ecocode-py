from ecocode import eco_compare, eco_report, profile_callable
from ecocode.cli import main as cli_main
from ecocode.static_analysis import analyze_callable


def loop_sum(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def builtin_sum(values):
    return sum(values)


def test_profile_callable_returns_value_and_metrics() -> None:
    values = list(range(1000))

    result_value, result_metrics = profile_callable(loop_sum, values, carbon_intensity=55)

    assert result_value == sum(values)
    assert result_metrics.function_name == "loop_sum"
    assert result_metrics.execution_time_s >= 0
    assert result_metrics.cpu_time_s >= 0
    assert result_metrics.estimated_emissions_gco2 >= 0


def test_static_analysis_flags_range_len_loop() -> None:
    suggestions = analyze_callable(loop_sum)

    assert any(suggestion.rule_id == "loop-range-len" for suggestion in suggestions)


def test_eco_compare_returns_a_named_winner() -> None:
    comparison = eco_compare(loop_sum, builtin_sum, list(range(5000)), carbon_intensity=55)

    assert comparison.better_function_name in {"loop_sum", "builtin_sum"}
    assert isinstance(comparison.summary(), str)


def test_eco_report_contains_key_sections() -> None:
    report = eco_report(loop_sum, list(range(1000)), carbon_intensity=55)

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
            "55",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "EcoCode execution report" in captured.out
    assert "Function: sum_loop" in captured.out