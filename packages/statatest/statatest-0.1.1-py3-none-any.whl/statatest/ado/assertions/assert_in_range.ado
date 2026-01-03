*! assert_in_range v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a value is within a specified range.
*!
*! Syntax:
*!   assert_in_range value, min(number) max(number) [message(string)] [verbose]
*!
*! Example:
*!   assert_in_range `r(mean)', min(0) max(100)
*!   assert_in_range `x', min(-1) max(1) message("x should be between -1 and 1")

program define assert_in_range, rclass
    version 16

    syntax anything(name=value), MIN(real) MAX(real) [Message(string) Verbose]

    if `value' < `min' | `value' > `max' {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_in_range"
            display as error "  Value:    `value'"
            display as error "  Min:      `min'"
            display as error "  Max:      `max'"
            if `value' < `min' {
                display as error "  Status:   value < min"
            }
            else {
                display as error "  Status:   value > max"
            }
            if `\"`message'\"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_in_range: `value' not in [`min', `max']"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_in_range_:`value' not in [`min', `max']_END_"
        exit 9
    }

    // Emit success marker
    if "`verbose'" != "" {
        noisily display "_STATATEST_PASS_:assert_in_range_"
        display as text "PASS: assert_in_range"
    }
    else {
        noisily display "_STATATEST_PASS_:assert_in_range_"
    }

    return local passed "1"
end
