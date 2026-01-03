*! fixture_multilevel_panel.ado
*! Version 1.1.0, 2025-12-30
*! Creates a multilevel/hierarchical panel dataset for testing
*!
*! Syntax:
*!   fixture_multilevel_panel [, n_groups(#) n_units(#) n_periods(#) ///
*!                               start_year(#) seed(#) Verbose]
*!
*! Options:
*!   n_groups(#)   - Number of top-level groups (default: 5)
*!   n_units(#)    - Units per group (default: 10)
*!   n_periods(#)  - Number of time periods (default: 5)
*!   start_year(#) - Starting year (default: 2015)
*!   seed(#)       - Random seed (default: 12345)
*!   Verbose       - Display fixture creation details
*!
*! Creates variables:
*!   group_id  - Top-level group identifier (e.g., country, industry)
*!   unit_id   - Unit within group (e.g., firm within country)
*!   year      - Time period
*!   value     - Random value with group and unit effects
*!
*! Structure:
*!   - Hierarchical: groups contain units
*!   - Panel: units observed over time
*!   - Example: country × firm × year

program define fixture_multilevel_panel
    version 16
    
    syntax [, n_groups(integer 5) n_units(integer 10) n_periods(integer 5) ///
              start_year(integer 2015) seed(integer 12345) Verbose]
    
    // Display creation message if verbose
    if "`verbose'" != "" {
        display as text "Creating multilevel panel: n_groups=`n_groups', n_units=`n_units', n_periods=`n_periods'"
    }
    
    clear
    set seed `seed'
    
    // Total observations
    local total_units = `n_groups' * `n_units'
    local n_obs = `total_units' * `n_periods'
    set obs `n_obs'
    
    // Create hierarchical structure
    // group_id: 1, 1, ..., 1, 2, 2, ..., 2, ...
    gen int group_id = floor((_n - 1) / (`n_units' * `n_periods')) + 1
    
    // unit_id: 1, 2, ..., n_units (within each group-year)
    gen int unit_id = mod(floor((_n - 1) / `n_periods'), `n_units') + 1
    
    // year
    gen int year = `start_year' + mod(_n - 1, `n_periods')
    
    // Create unique panel identifier (group-unit combination)
    gen long panel_id = (group_id - 1) * `n_units' + unit_id
    
    // Generate group effects (e.g., country-level differences)
    tempvar group_effect
    gen double `group_effect' = 0
    forvalues g = 1/`n_groups' {
        local ge = rnormal(0, 10)
        replace `group_effect' = `ge' if group_id == `g'
    }
    
    // Generate unit effects (e.g., firm-level differences within country)
    tempvar unit_effect
    gen double `unit_effect' = rnormal(0, 15)
    bysort group_id unit_id: replace `unit_effect' = `unit_effect'[1]
    
    // Generate value with hierarchical structure
    gen double value = 100 + `group_effect' + `unit_effect' + rnormal(0, 5)
    
    // Sort and set panel
    sort group_id unit_id year
    xtset panel_id year
    
    // Labels
    label variable group_id "Group identifier (e.g., country)"
    label variable unit_id "Unit within group (e.g., firm)"
    label variable year "Time period"
    label variable panel_id "Unique panel identifier"
    label variable value "Value with group and unit effects"
    
    // Return info
    return scalar n_groups = `n_groups'
    return scalar n_units = `n_units'
    return scalar n_periods = `n_periods'
    return scalar n_obs = `n_obs'
    
    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: multilevel_panel"
    }
end

// Aliases for common multilevel structures
program define fixture_country_firm_panel
    fixture_multilevel_panel `0'
end

program define fixture_industry_firm_panel
    fixture_multilevel_panel `0'
end
