*! fixture_balanced_panel.ado
*! Version 1.1.0, 2025-12-30
*! Creates a balanced panel dataset for testing
*!
*! Syntax:
*!   fixture_balanced_panel [, n_units(#) n_periods(#) start_year(#) seed(#) Verbose]
*!
*! Options:
*!   n_units(#)     - Number of panel units (default: 10)
*!   n_periods(#)   - Number of time periods (default: 5)
*!   start_year(#)  - Starting year (default: 2015)
*!   seed(#)        - Random seed for reproducibility (default: 12345)
*!   Verbose        - Display fixture creation details
*!
*! Creates variables:
*!   id    - Numeric panel unit identifier (1 to n_units)
*!   year  - Time period (start_year to start_year + n_periods - 1)
*!   value - Random normal value (mean=100, sd=20)
*!
*! Also sets: xtset id year

program define fixture_balanced_panel
    version 16
    
    syntax [, n_units(integer 10) n_periods(integer 5) ///
              start_year(integer 2015) seed(integer 12345) Verbose]
    
    // Display creation message if verbose
    if "`verbose'" != "" {
        display as text "Creating balanced panel: n_units=`n_units', n_periods=`n_periods', start_year=`start_year'"
    }
    
    // Clear existing data
    clear
    
    // Set seed for reproducibility
    set seed `seed'
    
    // Calculate total observations
    local n_obs = `n_units' * `n_periods'
    set obs `n_obs'
    
    // Create panel structure
    // id cycles 1, 2, ..., n_units, 1, 2, ..., n_units, ...
    gen int id = mod(_n - 1, `n_units') + 1
    
    // year increments every n_units observations
    gen int year = `start_year' + floor((_n - 1) / `n_units')
    
    // Create value variable (random normal)
    gen double value = rnormal(100, 20)
    
    // Sort and set panel structure
    sort id year
    xtset id year
    
    // Labels
    label variable id "Panel unit identifier"
    label variable year "Time period"
    label variable value "Random value (mean=100, sd=20)"
    
    // Return info
    return scalar n_units = `n_units'
    return scalar n_periods = `n_periods'
    return scalar n_obs = `n_obs'
    return scalar start_year = `start_year'
    return scalar end_year = `start_year' + `n_periods' - 1
    
    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: balanced_panel"
    }
end

// Alias for economic naming
program define fixture_firm_panel
    fixture_balanced_panel `0'
end
