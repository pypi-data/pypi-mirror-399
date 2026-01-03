import { Logger } from './logger';

const MAX_SIZE = 100;

function factorial(n: number): number {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

class Calculator {
    private value: number = 0;

    add(x: number, y: number): number {
        return x + y;
    }
}

const result = factorial(5);
console.log(`Result: ${result}`);
