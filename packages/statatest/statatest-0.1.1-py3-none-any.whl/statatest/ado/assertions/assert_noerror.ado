*! assert_noerror v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a command succeeds without error.
*!
*! Syntax:
*!   assert_noerror "command" [, message(string) verbose]
*!
*! Example:
*!   assert_noerror "gen x = 1"
*!   assert_noerror "regress y x", message("Regression should succeed") verbose

program define assert_noerror, rclass
    version 16

    syntax anything(name=command) [, Message(string) Verbose]

    // Execute the command and capture the return code
    capture `command'
    local actual_rc = _rc

    if `actual_rc' != 0 {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_noerror"
            display as error "  Command:  `command'"
            display as error "  Expected: success (rc=0)"
            display as error "  Actual:   rc=`actual_rc'"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_noerror: command failed with rc=`actual_rc'"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_noerror_:rc=`actual_rc'_END_"
        exit 9
    }

    if "`verbose'" != "" {
        display as text "PASS: assert_noerror"
    }

    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_noerror_"

    return local passed "1"
end
