<?php
require_once 'utils.php';

const MAX_SIZE = 100;

function factorial($n) {
    if ($n <= 1) {
        return 1;
    }
    return $n * factorial($n - 1);
}

class Calculator {
    public $value = 0;

    public function add($x, $y) {
        return $x + $y;
    }
}

$result = factorial(5);
echo "Result: $result\n";
?>
