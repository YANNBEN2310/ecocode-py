import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ecocode import CARBON_INTENSITY_ENV_VAR, carbon_profiler, eco_compare, eco_report


SAMPLE_CARBON_INTENSITY = float(os.getenv(CARBON_INTENSITY_ENV_VAR, "55"))


@carbon_profiler(carbon_intensity=SAMPLE_CARBON_INTENSITY)
def sum_loop(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def sum_builtin(values):
    return sum(values)


def main() -> None:
    data = list(range(50_000))
    sum_loop(data)

    comparison = eco_compare(
        sum_loop,
        sum_builtin,
        data,
        carbon_intensity=SAMPLE_CARBON_INTENSITY,
    )
    print(comparison.summary())
    print()
    print(eco_report(sum_loop, data, carbon_intensity=SAMPLE_CARBON_INTENSITY))


if __name__ == "__main__":
    main()