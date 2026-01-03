*! assert_identity.ado
*! Version 1.1.0  2025-12-30
*! Assert that an accounting identity holds (row-wise equality)
*!
*! Syntax:
*!   assert_identity exp1 == exp2 [if] [, tol(#) message(string) verbose]
*!
*! Options:
*!   tol(#)        - Tolerance for numeric comparison (default: 1e-10)
*!   message(str)  - Custom error message
*!   verbose       - Show detailed output (PASS on success, full details on failure)
*!
*! Examples:
*!   assert_identity assets == liabilities + equity
*!   assert_identity fob + freight + insurance == cif, tol(0.01)
*!   assert_identity revenue - costs == profit if year == 2020, verbose

program define assert_identity
    version 16
    
    // Parse the equality expression
    gettoken lhs rest : 0, parse("==")
    gettoken eq rest : rest, parse("==")
    
    if "`eq'" != "==" {
        display as error "Syntax: assert_identity exp1 == exp2 [if] [, options]"
        exit 198
    }
    
    // Parse RHS and options
    local 0 `rest'
    syntax anything [if] [, tol(real 1e-10) message(string) Verbose]
    local rhs `anything'
    
    marksample touse, novarlist
    
    // Calculate both sides
    tempvar lhs_val rhs_val diff
    
    capture gen double `lhs_val' = `lhs' if `touse'
    if _rc != 0 {
        display as error "Error evaluating LHS expression: `lhs'"
        exit _rc
    }
    
    capture gen double `rhs_val' = `rhs' if `touse'
    if _rc != 0 {
        display as error "Error evaluating RHS expression: `rhs'"
        exit _rc
    }
    
    gen double `diff' = abs(`lhs_val' - `rhs_val')
    
    // Count violations
    quietly count if `diff' > `tol' & `touse' & !missing(`diff')
    local n_fail = r(N)
    
    if `n_fail' > 0 {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_identity"
            display as error "  Identity: `lhs' == `rhs'"
            display as error "  Tolerance: `tol'"
            display as error "  `n_fail' observations violate the identity"
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
            
            // Show summary of differences
            display as error ""
            display as error "  Summary of differences:"
            summarize `diff' if `diff' > `tol' & `touse', detail
            
            // Show first few violations
            display as error ""
            display as error "  First 5 violations:"
            gen double _lhs = `lhs_val'
            gen double _rhs = `rhs_val'
            gen double _diff = `diff'
            list _lhs _rhs _diff if `diff' > `tol' & `touse' in 1/5, noobs
            drop _lhs _rhs _diff
        }
        else {
            display as error "FAIL: assert_identity: identity check failed"
        }
        
        exit 9
    }
    
    // Success message (only if verbose)
    if "`verbose'" != "" {
        display as text "PASS: assert_identity"
    }
end
