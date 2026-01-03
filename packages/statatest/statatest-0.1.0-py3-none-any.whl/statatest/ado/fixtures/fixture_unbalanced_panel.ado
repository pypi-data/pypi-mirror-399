*! fixture_unbalanced_panel.ado
*! Version 1.1.0, 2025-12-30
*! Creates an unbalanced panel dataset with gaps for testing
*!
*! Syntax:
*!   fixture_unbalanced_panel [, n_units(#) n_periods(#) start_year(#) ///
*!                               attrition(#) entry(#) seed(#) Verbose]
*!
*! Options:
*!   n_units(#)    - Number of panel units (default: 20)
*!   n_periods(#)  - Number of time periods (default: 10)
*!   start_year(#) - Starting year (default: 2010)
*!   attrition(#)  - Annual attrition rate 0-1 (default: 0.1)
*!   entry(#)      - Annual entry rate 0-1 (default: 0.05)
*!   seed(#)       - Random seed (default: 12345)
*!   Verbose       - Display fixture creation details
*!
*! Creates variables:
*!   id    - Panel unit identifier
*!   year  - Time period
*!   value - Random normal value
*!
*! Structure:
*!   - Units may enter after start_year
*!   - Units may exit before end_year
*!   - Creates realistic unbalanced structure

program define fixture_unbalanced_panel
    version 16
    
    syntax [, n_units(integer 20) n_periods(integer 10) start_year(integer 2010) ///
              attrition(real 0.1) entry(real 0.05) seed(integer 12345) Verbose]
    
    // Display creation message if verbose
    if "`verbose'" != "" {
        display as text "Creating unbalanced panel: n_units=`n_units', n_periods=`n_periods', attrition=`attrition', entry=`entry'"
    }
    
    clear
    set seed `seed'
    
    // Validate rates
    if `attrition' < 0 | `attrition' > 1 {
        display as error "attrition() must be between 0 and 1"
        exit 198
    }
    if `entry' < 0 | `entry' > 1 {
        display as error "entry() must be between 0 and 1"
        exit 198
    }
    
    // Start with balanced panel
    local n_obs = `n_units' * `n_periods'
    set obs `n_obs'
    
    gen int id = mod(_n - 1, `n_units') + 1
    gen int year = `start_year' + floor((_n - 1) / `n_units')
    
    // Generate entry year for each unit (some enter late)
    tempvar entry_year exit_year
    gen int `entry_year' = `start_year'
    gen int `exit_year' = `start_year' + `n_periods' - 1
    
    // Assign random entry years (some units enter after start)
    forvalues i = 1/`n_units' {
        if runiform() < `entry' * `n_periods' / 2 {
            local delay = ceil(runiform() * (`n_periods' / 2))
            replace `entry_year' = `start_year' + `delay' if id == `i'
        }
    }
    
    // Assign random exit years (some units exit early - attrition)
    forvalues i = 1/`n_units' {
        if runiform() < `attrition' * `n_periods' / 2 {
            local early_exit = ceil(runiform() * (`n_periods' / 2))
            replace `exit_year' = `start_year' + `n_periods' - 1 - `early_exit' if id == `i'
        }
    }
    
    // Keep only observations within entry-exit window
    drop if year < `entry_year' | year > `exit_year'
    
    // Add some random gaps (intermittent missingness)
    gen byte _drop = runiform() < 0.05
    drop if _drop
    drop _drop
    
    // Generate value
    gen double value = rnormal(100, 20)
    
    // Sort and set panel (will have gaps)
    sort id year
    xtset id year
    
    // Labels
    label variable id "Panel unit identifier"
    label variable year "Time period"
    label variable value "Random value"
    
    // Return info
    quietly count
    return scalar n_obs = r(N)
    quietly distinct id
    return scalar n_units = r(ndistinct)
    return scalar n_periods = `n_periods'
    
    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: unbalanced_panel"
    }
end

// Alias
program define fixture_unbalanced_firm_panel
    fixture_unbalanced_panel `0'
end
