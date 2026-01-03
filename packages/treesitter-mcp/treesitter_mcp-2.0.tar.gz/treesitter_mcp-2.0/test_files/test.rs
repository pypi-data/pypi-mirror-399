use std::fmt;

const MAX_SIZE: usize = 100;

fn factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1;
    }
    n * factorial(n - 1)
}

struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn new(x: i32, y: i32) -> Self {
        Point { x, y }
    }
}

fn main() {
    let x = 5;
    let result = factorial(x);
    println!("Factorial of {} is {}", x, result);
}
