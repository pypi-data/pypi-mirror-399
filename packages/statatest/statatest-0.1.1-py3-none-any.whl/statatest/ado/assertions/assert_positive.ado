*! assert_positive.ado
*! Version 1.1.0, 2025-12-30
*! Assert that all values of a variable are positive
*!
*! Syntax:
*!   assert_positive varname [if] [, strict message(string) Verbose]
*!
*! Options:
*!   strict        - Require strictly positive (> 0), not just non-negative
*!   message(str)  - Custom error message
*!   Verbose       - Show detailed output (PASS on success, details on failure)
*!
*! Examples:
*!   assert_positive sales
*!   assert_positive wage, strict message("Wages must be positive")
*!   assert_positive revenue if year >= 2015
*!   assert_positive price, Verbose

program define assert_positive
    version 16
    
    syntax varname [if] [, strict message(string) Verbose]
    
    marksample touse
    
    // Check for missing values first
    quietly count if missing(`varlist') & `touse'
    if r(N) > 0 {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_positive"
            display as error "  Variable: `varlist'"
            display as error "  Found `r(N)' missing values"
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
        }
        else {
            display as error "FAIL: assert_positive: `varlist' has missing values"
        }
        exit 9
    }
    
    // Check for non-positive values
    if "`strict'" != "" {
        // Strictly positive: > 0
        quietly count if `varlist' <= 0 & `touse'
        local condition "<= 0"
    }
    else {
        // Non-negative by default: >= 0
        quietly count if `varlist' < 0 & `touse'
        local condition "< 0"
    }
    
    if r(N) > 0 {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_positive"
            display as error "  Variable: `varlist'"
            display as error "  Found `r(N)' values `condition'"
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
            
            // Show summary of problematic values
            display as error ""
            display as error "  Summary of non-positive values:"
            if "`strict'" != "" {
                summarize `varlist' if `varlist' <= 0 & `touse', detail
            }
            else {
                summarize `varlist' if `varlist' < 0 & `touse', detail
            }
        }
        else {
            display as error "FAIL: assert_positive: `varlist' has non-positive values"
        }
        exit 9
    }
    else {
        if "`verbose'" != "" {
            display as text "PASS: assert_positive: `varlist' has positive values"
        }
    }
end
