*! fixture_bipartite_network.ado
*! Version 1.1.0, 2025-12-30
*! Creates a bipartite network (two distinct node types) for testing
*! Default structure: employer-employee (AKM-style)
*!
*! Syntax:
*!   fixture_bipartite_network [, n_workers(#) n_firms(#) n_periods(#) ///
*!                                 start_year(#) mobility(#) seed(#) Verbose]
*!
*! Options:
*!   n_workers(#)  - Number of workers (default: 500)
*!   n_firms(#)    - Number of firms (default: 50)
*!   n_periods(#)  - Number of time periods (default: 5)
*!   start_year(#) - Starting year (default: 2015)
*!   mobility(#)   - Job mobility rate 0-1 (default: 0.15)
*!   seed(#)       - Random seed (default: 12345)
*!   Verbose       - Display fixture creation details
*!
*! Creates variables:
*!   worker_id - Worker identifier (1 to n_workers)
*!   firm_id   - Firm identifier (1 to n_firms)
*!   year      - Time period
*!   wage      - Log wage (worker + firm effects + residual)
*!
*! Bipartite structure:
*!   - Two distinct node types: workers and firms
*!   - Edges only between workers and firms (not worker-worker or firm-firm)
*!   - Follows AKM (Abowd, Kramarz, Margolis 1999) wage decomposition
*!   - log(wage) = worker_effect + firm_effect + X'beta + residual

program define fixture_bipartite_network
    version 16
    
    syntax [, n_workers(integer 500) n_firms(integer 50) n_periods(integer 5) ///
              start_year(integer 2015) mobility(real 0.15) seed(integer 12345) Verbose]
    
    // Display creation message if verbose
    if "`verbose'" != "" {
        display as text "Creating bipartite network: n_workers=`n_workers', n_firms=`n_firms', n_periods=`n_periods', mobility=`mobility'"
    }
    
    clear
    set seed `seed'
    
    // Validate mobility rate
    if `mobility' < 0 | `mobility' > 1 {
        display as error "mobility() must be between 0 and 1"
        exit 198
    }
    
    // Generate worker fixed effects (permanent worker ability)
    // These capture time-invariant worker heterogeneity
    tempfile worker_effects
    clear
    set obs `n_workers'
    gen int worker_id = _n
    gen double worker_effect = rnormal(0, 0.3)
    save `worker_effects', replace
    
    // Generate firm fixed effects (firm wage premium)
    // These capture time-invariant firm pay policies
    tempfile firm_effects
    clear
    set obs `n_firms'
    gen int firm_id = _n
    gen double firm_effect = rnormal(0, 0.2)
    save `firm_effects', replace
    
    // Create worker-year panel with job mobility
    clear
    local n_obs = `n_workers' * `n_periods'
    set obs `n_obs'
    
    // Worker ID (repeated for each period)
    gen int worker_id = mod(_n - 1, `n_workers') + 1
    
    // Year
    gen int year = `start_year' + floor((_n - 1) / `n_workers')
    
    // Initial firm assignment (random)
    gen int firm_id = ceil(runiform() * `n_firms')
    
    // Apply job mobility
    // Workers have probability `mobility` of switching firms each year
    sort worker_id year
    by worker_id: replace firm_id = firm_id[_n-1] if _n > 1 & runiform() > `mobility'
    by worker_id: replace firm_id = ceil(runiform() * `n_firms') if _n > 1 & runiform() <= `mobility'
    
    // Merge worker effects
    merge m:1 worker_id using `worker_effects', nogen keep(match)
    
    // Merge firm effects
    merge m:1 firm_id using `firm_effects', nogen keep(match)
    
    // Generate log wages following AKM decomposition
    // log(wage) = worker_effect + firm_effect + experience + residual
    gen double experience = (year - `start_year') * 0.02  // 2% return to experience
    gen double residual = rnormal(0, 0.15)
    gen double log_wage = 10 + worker_effect + firm_effect + experience + residual
    gen double wage = exp(log_wage)
    
    // Clean up intermediate variables
    drop worker_effect firm_effect experience residual log_wage
    
    // Sort and label
    sort worker_id year
    
    label variable worker_id "Worker identifier"
    label variable firm_id "Firm identifier"
    label variable year "Year"
    label variable wage "Wage (AKM structure)"
    
    // Return info
    quietly count
    return scalar n_obs = r(N)
    return scalar n_workers = `n_workers'
    return scalar n_firms = `n_firms'
    return scalar n_periods = `n_periods'
    return scalar mobility = `mobility'
    
    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: bipartite_network"
    }
end

// Alias for employer-employee data
program define fixture_employer_employee
    fixture_bipartite_network `0'
end

// Alias for matched data
program define fixture_matched_panel
    fixture_bipartite_network `0'
end
