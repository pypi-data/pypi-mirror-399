*! assert_var_exists v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that a variable exists in the current dataset.
*!
*! Syntax:
*!   assert_var_exists varname [, type(string) message(string) Verbose]
*!
*! Options:
*!   type(string)    - Check variable has specified type
*!   message(string) - Custom error message
*!   Verbose         - Show detailed messages on success and failure
*!
*! Example:
*!   assert_var_exists mpg
*!   assert_var_exists price, type("double") verbose

program define assert_var_exists, rclass
    version 16

    syntax name(name=varname) [, Type(string) Message(string) Verbose]

    // Check if variable exists
    capture confirm variable `varname'

    if _rc != 0 {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_var_exists"
            display as error "  Variable: `varname'"
            display as error "  Status:   does not exist"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_var_exists: variable `varname' not found"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_var_exists_:`varname' not found_END_"
        exit 111
    }

    // If type specified, check type
    if `"`type'"' != "" {
        local actual_type : type `varname'
        if "`actual_type'" != "`type'" {
            if "`verbose'" != "" {
                display as error "ASSERTION FAILED: assert_var_exists"
                display as error "  Variable: `varname'"
                display as error "  Expected type: `type'"
                display as error "  Actual type:   `actual_type'"
                if `"`message'"' != "" {
                    display as error "  Message:  `message'"
                }
            }
            else {
                display as error "FAIL: assert_var_exists: variable `varname' type mismatch"
            }
            // Emit failure marker
            noisily display "_STATATEST_FAIL_:assert_var_exists_:type `actual_type' != `type'_END_"
            exit 9
        }
    }

    // Success
    if "`verbose'" != "" {
        display as text "PASS: assert_var_exists"
    }
    
    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_var_exists_"

    return local passed "1"
end
