*! assert_unique v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that variable combination uniquely identifies observations
*! Uses gisid internally for performance on large datasets
*!
*! Syntax:
*!   assert_unique varlist [if] [, by(varlist) message(string) Verbose]
*!
*! Options:
*!   by(varlist)     - Check uniqueness within groups
*!   message(string) - Custom error message
*!   Verbose         - Show detailed messages on success and failure
*!
*! Examples:
*!   assert_unique id year                    // Check id-year is unique
*!   assert_unique id year, by(country)       // Unique within country
*!   assert_unique seller buyer, by(year) verbose

program define assert_unique, rclass
    version 16
    
    syntax varlist [if] [, by(varlist) message(string) Verbose]
    
    // Try gisid first (fast), fall back to isid
    capture which gisid
    local use_gtools = (_rc == 0)
    
    if `use_gtools' {
        // Use gtools for performance
        if "`by'" != "" {
            capture noisily gisid `varlist' `if', by(`by')
        }
        else {
            capture noisily gisid `varlist' `if'
        }
    }
    else {
        // Fall back to standard isid
        if "`by'" != "" {
            // isid doesn't have by(), so we need to work around
            tempvar group_check
            marksample touse
            
            if "`if'" != "" {
                local ifcond "if `touse'"
            }
            
            // Check uniqueness within each by-group
            capture {
                bysort `by' (`varlist'): gen byte `group_check' = 1 `ifcond'
                by `by' `varlist': assert _N == 1 `ifcond'
            }
        }
        else {
            capture noisily isid `varlist' `if'
        }
    }
    
    local rc = _rc
    
    if `rc' != 0 {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_unique"
            display as error "  Variables: `varlist'"
            if "`by'" != "" {
                display as error "  By groups: `by'"
            }
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
            
            // Show duplicates for debugging
            display as error ""
            display as error "  Duplicate observations found. First 5:"
            if "`by'" != "" {
                duplicates list `by' `varlist' `if' in 1/5, sepby(`by')
            }
            else {
                duplicates list `varlist' `if' in 1/5
            }
        }
        else {
            display as error "FAIL: assert_unique: `varlist' has duplicates"
        }
        
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_unique_:`varlist' has duplicates_END_"
        
        exit 9
    }
    
    // Success
    if "`verbose'" != "" {
        display as text "PASS: assert_unique"
    }
    
    // Emit success marker
    noisily display "_STATATEST_PASS_:assert_unique_"
    
    return local passed "1"
end
