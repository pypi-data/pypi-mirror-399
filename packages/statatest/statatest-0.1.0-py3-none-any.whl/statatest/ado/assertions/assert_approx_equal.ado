*! assert_approx_equal v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that two numeric values are approximately equal within tolerance.
*!
*! Syntax:
*!   assert_approx_equal actual, expected(number) [tol(number) message(string) verbose]
*!
*! Example:
*!   assert_approx_equal `r(mean)', expected(0.5) tol(0.01)
*!   assert_approx_equal 3.14159, expected(3.14) tol(0.01) verbose

program define assert_approx_equal, rclass
    version 16

    syntax anything(name=actual), Expected(real) [TOL(real 1e-6) Message(string) Verbose]

    // Calculate absolute difference
    local diff = abs(`actual' - `expected')

    if `diff' > `tol' {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_approx_equal"
            display as error "  Expected: `expected'"
            display as error "  Actual:   `actual'"
            display as error "  Diff:     `diff'"
            display as error "  Tol:      `tol'"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_approx_equal: `actual' !≈ `expected' (tol=`tol')"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_approx_equal_:diff `diff' > tol `tol'_END_"
        exit 9
    }

    if "`verbose'" != "" {
        display as text "PASS: assert_approx_equal"
    }

    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_approx_equal_"

    return local passed "1"
    return local diff "`diff'"
end
