import os
import sys
from typing import List

GLOBAL_CONSTANT = 42

def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def process_numbers(numbers: List[int]) -> List[int]:
    """Process a list of numbers."""
    results = []
    for num in numbers:
        results.append(factorial(num))
    return results

class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.value = 0

    def add(self, x: int, y: int) -> int:
        return x + y

def main():
    x = 5
    result = factorial(x)
    print(f"Factorial of {x} is {result}")
    test_var = GLOBAL_CONSTANT

if __name__ == "__main__":
    main()
