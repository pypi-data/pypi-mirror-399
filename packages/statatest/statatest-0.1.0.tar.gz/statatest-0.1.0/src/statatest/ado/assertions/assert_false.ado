*! assert_false v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a condition evaluates to false.
*!
*! Syntax:
*!   assert_false condition [, message(string) verbose]
*!
*! Example:
*!   assert_false missing(x)
*!   assert_false `x' < 0, message("x should not be negative")

program define assert_false, rclass
    version 16

    syntax anything(name=condition) [, Message(string) Verbose]

    // Use capture assert to test that condition is false (NOT condition is true)
    capture assert !(`condition')

    if _rc == 9 {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_false"
            display as error "  Condition: `condition'"
            display as error "  Evaluated: true (expected false)"
            if `"`message'"' != "" {
                display as error "  Message:   `message'"
            }
        }
        else {
            display as error "FAIL: assert_false: `condition' is true"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_false_:`condition' is true_END_"
        exit 9
    }
    else if _rc != 0 {
        error _rc
    }

    // Success: display only if verbose option
    if "`verbose'" != "" {
        display as text "PASS: assert_false"
    }

    return local passed "1"
end
