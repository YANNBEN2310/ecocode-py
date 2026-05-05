from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ecocode import carbon_profiler, eco_compare, eco_report


@carbon_profiler(carbon_intensity=55)
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

    comparison = eco_compare(sum_loop, sum_builtin, data, carbon_intensity=55)
    print(comparison.summary())
    print()
    print(eco_report(sum_loop, data, carbon_intensity=55))


if __name__ == "__main__":
    main()