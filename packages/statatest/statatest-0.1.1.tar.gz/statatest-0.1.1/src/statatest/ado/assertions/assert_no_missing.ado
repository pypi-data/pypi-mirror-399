*! assert_no_missing.ado
*! Version 1.1.0, 2025-12-30
*! Assert that variables have no missing values
*!
*! Syntax:
*!   assert_no_missing varlist [if] [, message(string) Verbose]
*!
*! Options:
*!   message(str)  - Custom error message
*!   Verbose       - Show detailed output (PASS on success, details on failure)
*!
*! Examples:
*!   assert_no_missing id year value
*!   assert_no_missing sales if year >= 2015
*!   assert_no_missing id year, Verbose

program define assert_no_missing
    version 16
    
    syntax varlist [if] [, message(string) Verbose]
    
    marksample touse, novarlist
    
    local has_missing = 0
    local missing_vars ""
    
    foreach var of varlist `varlist' {
        quietly count if missing(`var') & `touse'
        if r(N) > 0 {
            local has_missing = 1
            local missing_vars "`missing_vars' `var'(`r(N)')"
        }
    }
    
    if `has_missing' {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_no_missing"
            display as error "  Variables with missing values:"
            display as error "   `missing_vars'"
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
        }
        else {
            display as error "FAIL: assert_no_missing: `varlist' has missing values"
        }
        exit 9
    }
    else {
        if "`verbose'" != "" {
            display as text "PASS: assert_no_missing: `varlist' has no missing values"
        }
    }
end
