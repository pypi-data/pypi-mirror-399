const fs = require('fs');
const path = require('path');

const MAX_SIZE = 100;

function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

function processArray(arr) {
    return arr.map(x => factorial(x));
}

class Calculator {
    constructor() {
        this.value = 0;
    }

    add(x, y) {
        return x + y;
    }
}

// Main execution
const x = 5;
const result = factorial(x);
console.log(`Factorial of ${x} is ${result}`);
