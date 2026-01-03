*! assert_file_exists v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a file exists at the specified path.
*!
*! Syntax:
*!   assert_file_exists "path" [, message(string) Verbose]
*!
*! Options:
*!   message(string) - Custom error message
*!   Verbose         - Show detailed messages on success and failure
*!
*! Example:
*!   assert_file_exists "data/input.dta"
*!   assert_file_exists "`c(sysdir_plus)'ado/base/r/regress.ado", verbose

program define assert_file_exists, rclass
    version 16

    syntax anything(name=filepath) [, Message(string) Verbose]

    // Remove quotes if present
    local filepath = subinstr(`"`filepath'"', `""""', "", .)

    // Check if file exists
    capture confirm file `"`filepath'"'

    if _rc != 0 {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_file_exists"
            display as error "  File:    `filepath'"
            display as error "  Status:  does not exist"
            if `"`message'"' != "" {
                display as error "  Message: `message'"
            }
        }
        else {
            display as error "FAIL: assert_file_exists: `filepath' not found"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_file_exists_:`filepath' not found_END_"
        exit 601
    }

    // Success
    if "`verbose'" != "" {
        display as text "PASS: assert_file_exists"
    }
    
    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_file_exists_"

    return local passed "1"
end
