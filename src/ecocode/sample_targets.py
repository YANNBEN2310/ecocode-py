"""Small packaged CLI targets used by examples and tests."""


def sum_loop(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def sum_builtin(values):
    return sum(values)