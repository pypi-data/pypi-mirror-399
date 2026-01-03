*! assert_sum_equals.ado
*! Version 1.1.0  2025-12-30
*! Assert that sum of a variable equals expected value
*!
*! Syntax:
*!   assert_sum_equals varname [if], expected(#) [tol(#) by(varlist) message(string) verbose]
*!
*! Options:
*!   expected(#)   - Expected sum value (required)
*!   tol(#)        - Tolerance for comparison (default: 1e-10)
*!   by(varlist)   - Check sum within each group
*!   message(str)  - Custom error message
*!   verbose       - Show detailed output (PASS on success, full details on failure)
*!
*! Examples:
*!   assert_sum_equals share, expected(1)                  // Shares sum to 1
*!   assert_sum_equals weight, expected(100) tol(0.01)    // Allow small error
*!   assert_sum_equals detail, expected(total) by(group)  // By group

program define assert_sum_equals
    version 16
    
    syntax varname [if], expected(real) [tol(real 1e-10) by(varlist) message(string) Verbose]
    
    marksample touse
    
    if "`by'" != "" {
        // Check sum within each group
        tempvar group_sum group_diff
        
        gegen double `group_sum' = total(`varlist') if `touse', by(`by')
        gen double `group_diff' = abs(`group_sum' - `expected')
        
        quietly count if `group_diff' > `tol' & `touse' & !missing(`group_diff')
        local n_fail = r(N)
        
        if `n_fail' > 0 {
            if "`verbose'" != "" {
                display as error ""
                display as error "ASSERTION FAILED: assert_sum_equals"
                display as error "  Variable: `varlist'"
                display as error "  By groups: `by'"
                display as error "  Expected sum: `expected'"
                display as error "  Tolerance: `tol'"
                display as error "  `n_fail' observations in groups with incorrect sum"
                if "`message'" != "" {
                    display as error "  Message: `message'"
                }
                
                // Show failing groups
                display as error ""
                display as error "  Groups with incorrect sum:"
                list `by' `group_sum' if `group_diff' > `tol' & `touse', noobs sepby(`by')
            }
            else {
                quietly summarize `group_sum' if `group_diff' > `tol' & `touse'
                local actual = r(mean)
                display as error "FAIL: assert_sum_equals: sum(`varlist')=`actual' != `expected'"
            }
            
            exit 9
        }
    }
    else {
        // Check overall sum
        quietly summarize `varlist' if `touse'
        local actual_sum = r(sum)
        local diff = abs(`actual_sum' - `expected')
        
        if `diff' > `tol' {
            if "`verbose'" != "" {
                display as error ""
                display as error "ASSERTION FAILED: assert_sum_equals"
                display as error "  Variable: `varlist'"
                display as error "  Expected sum: `expected'"
                display as error "  Actual sum: `actual_sum'"
                display as error "  Difference: `diff'"
                display as error "  Tolerance: `tol'"
                if "`message'" != "" {
                    display as error "  Message: `message'"
                }
            }
            else {
                display as error "FAIL: assert_sum_equals: sum(`varlist')=`actual_sum' != `expected'"
            }
            exit 9
        }
    }
    
    // Success message (only if verbose)
    if "`verbose'" != "" {
        display as text "PASS: assert_sum_equals"
    }
end
