*! assert_label_exists v1.1.0  statatest  2025-12-30
*! Assert that a variable has value labels attached.
*!
*! Syntax:
*!   assert_label_exists varname [, message(string)] [Verbose]
*!
*! Examples:
*!   sysuse auto, clear
*!   assert_label_exists foreign
*!   assert_label_exists rep78, message("rep78 should have labels")

program define assert_label_exists, rclass
    version 16
    
    syntax varname [, Message(string)] [Verbose]
    
    // Get the value label attached to the variable
    local label_name : value label `varlist'
    
    // Check if label is attached (empty means no label)
    if "`label_name'" == "" {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_label_exists"
            display as error "  Variable: `varlist'"
            display as error "  Expected: value label attached"
            display as error "  Actual:   no value label"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_label_exists: `varlist' has no value label"
        }
        noisily display "_STATATEST_FAIL_:assert_label_exists_:`varlist' has no label_END_"
        exit 9
    }
    
    if "`verbose'" != "" {
        display as text "PASS: assert_label_exists"
    }
    noisily display "_STATATEST_PASS_:assert_label_exists_"
    
    return local passed "1"
    return local label_name "`label_name'"
end
