require 'json'

MAX_VALUE = 100

def factorial(n)
  return 1 if n <= 1
  n * factorial(n - 1)
end

class Calculator
  def initialize
    @value = 0
  end

  def add(x, y)
    x + y
  end
end

# Main execution
x = 5
result = factorial(x)
puts "Factorial of #{x} is #{result}"
