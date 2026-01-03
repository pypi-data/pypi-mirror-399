package main

import (
	"fmt"
	"os"
)

const MaxSize = 100

var globalCounter int

func factorial(n int) int {
	if n <= 1 {
		return 1
	}
	return n * factorial(n - 1)
}

func processNumbers(numbers []int) []int {
	results := []int{}
	for _, num := range numbers {
		results = append(results, factorial(num))
	}
	return results
}

type Point struct {
	X int
	Y int
}

func main() {
	x := 5
	result := factorial(x)
	fmt.Printf("Factorial of %d is %d\n", x, result)
	globalCounter++
}
