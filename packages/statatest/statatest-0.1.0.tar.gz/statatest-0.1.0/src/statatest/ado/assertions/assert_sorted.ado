*! assert_sorted.ado
*! Version 1.1.0, 2025-12-30
*! Assert that data is sorted by specified variables
*!
*! Syntax:
*!   assert_sorted varlist [, message(string) Verbose]
*!
*! Options:
*!   message(str)  - Custom error message
*!   Verbose       - Show detailed output (PASS on success, details on failure)
*!
*! Examples:
*!   assert_sorted id year
*!   assert_sorted firm_id year, message("Data must be sorted by firm-year")
*!   assert_sorted id year, Verbose

program define assert_sorted
    version 16
    
    syntax varlist [, message(string) Verbose]
    
    // Check if data is sorted using hashsort verification if available
    capture which hashsort
    local use_gtools = (_rc == 0)
    
    // Store current sort order
    tempvar sortcheck
    gen long `sortcheck' = _n
    
    // Sort by specified variables and check if order changed
    if `use_gtools' {
        capture noisily hashsort `varlist', sortgen(_newsort)
        local sorted_var "_newsort"
    }
    else {
        sort `varlist'
        gen long _newsort = _n
        local sorted_var "_newsort"
    }
    
    // Compare original order with sorted order
    quietly count if `sortcheck' != `sorted_var'
    local n_changed = r(N)
    
    // Clean up
    capture drop _newsort
    
    // Restore original order
    sort `sortcheck'
    
    if `n_changed' > 0 {
        if "`verbose'" != "" {
            display as error ""
            display as error "ASSERTION FAILED: assert_sorted"
            display as error "  Variables: `varlist'"
            display as error "  Data is NOT sorted by these variables"
            display as error "  `n_changed' observations would change position"
            if "`message'" != "" {
                display as error "  Message: `message'"
            }
        }
        else {
            display as error "FAIL: assert_sorted: data not sorted by `varlist'"
        }
        exit 9
    }
    else {
        if "`verbose'" != "" {
            display as text "PASS: assert_sorted: data sorted by `varlist'"
        }
    }
end
