*! assert_true v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a condition evaluates to true.
*!
*! Syntax:
*!   assert_true condition [, message(string) verbose]
*!
*! Options:
*!   verbose: Display detailed output on success/failure
*!
*! Example:
*!   assert_true _N > 0
*!   assert_true `x' > 5, message("x should be greater than 5")
*!   assert_true _N > 0, verbose

program define assert_true, rclass
    version 16

    syntax anything(name=condition) [, Message(string) verbose]

    // Use capture assert to test condition
    capture assert `condition'

    if _rc == 9 {
        // Minimal output by default
        if "`verbose'" == "" {
            display as error "FAIL: assert_true: condition is false"
        }
        else {
            // Verbose: detailed output
            display as error "ASSERTION FAILED: assert_true"
            display as error "  Condition: `condition'"
            display as error "  Evaluated: false"
        }
        if `"`message'"' != "" {
            display as error "  Message:  `message'"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_true_:`condition' is false_END_"
        exit 9
    }
    else if _rc != 0 {
        error _rc
    }

    // Success
    if "`verbose'" != "" {
        display as text "PASS: assert_true"
    }

    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_true_"

    return local passed "1"
end
