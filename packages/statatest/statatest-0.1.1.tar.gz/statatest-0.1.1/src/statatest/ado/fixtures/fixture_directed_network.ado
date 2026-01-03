*! fixture_directed_network.ado
*! Version 1.1.0, 2025-12-30
*! Creates a sparse directed weighted network for testing
*!
*! Syntax:
*!   fixture_directed_network [, n_firms(#) n_edges(#) temporal seed(#) Verbose]
*!
*! Options:
*!   n_firms(#)  - Total number of firms (default: 100)
*!   n_edges(#)  - Number of edges/transactions (default: 500)
*!   temporal    - Add year dimension (2015-2019)
*!   seed(#)     - Random seed (default: 12345)
*!   Verbose     - Display fixture creation details
*!
*! Creates variables:
*!   seller  - Seller firm ID (source node)
*!   buyer   - Buyer firm ID (target node)
*!   weight  - Transaction value (log-normal)
*!   year    - Time period (if temporal option specified)
*!
*! Network properties (Bernard & Zi 2022):
*!   - Directed: seller → buyer
*!   - Weighted: transaction values
*!   - Sparse: not fully connected
*!   - NOT bipartite: firms can be both buyers and sellers
*!   - ~31% only buyers, ~13% only sellers, ~56% both

program define fixture_directed_network
    version 16
    
    syntax [, n_firms(integer 100) n_edges(integer 500) temporal seed(integer 12345) Verbose]
    
    // Display creation message if verbose
    if "`verbose'" != "" {
        local temp_msg = cond("`temporal'" != "", "temporal", "cross-sectional")
        display as text "Creating directed network: n_firms=`n_firms', n_edges=`n_edges', type=`temp_msg'"
    }
    
    clear
    set seed `seed'
    
    // Firm composition (Bernard & Zi 2022 calibration)
    // These shares come from Costa Rican production network data
    local n_only_buyers = floor(0.31 * `n_firms')
    local n_only_sellers = floor(0.13 * `n_firms')
    local n_both = `n_firms' - `n_only_buyers' - `n_only_sellers'
    
    // Seller pool: only_sellers + both
    local n_sellers = `n_only_sellers' + `n_both'
    // Buyer pool: only_buyers + both  
    local n_buyers = `n_only_buyers' + `n_both'
    
    // Create edges
    if "`temporal'" != "" {
        local n_years = 5
        local total_edges = `n_edges' * `n_years'
    }
    else {
        local total_edges = `n_edges'
    }
    
    set obs `total_edges'
    
    // Generate seller IDs (from seller pool)
    gen int seller = ceil(runiform() * `n_sellers')
    
    // Generate buyer IDs (from buyer pool, offset by n_only_sellers)
    // This allows overlap: firms in "both" category can buy from each other
    gen int buyer = `n_only_sellers' + ceil(runiform() * `n_buyers')
    
    // Allow self-loops to be removed (firm buying from itself is rare but possible)
    // In production networks, self-loops are usually excluded
    drop if seller == buyer
    
    // Transaction weight (log-normal, following BCCR data moments)
    // Mean ~0.034, calibrated to Costa Rican transaction data
    gen double weight = exp(rnormal(-3.4, 0.5))
    
    // Add temporal dimension if requested
    if "`temporal'" != "" {
        gen int year = 2015 + floor((_n - 1) / `n_edges')
        label variable year "Transaction year"
    }
    
    // Remove exact duplicates (keep unique edges per period)
    // In production networks, multiple transactions between same pair
    // are typically aggregated
    if "`temporal'" != "" {
        duplicates drop seller buyer year, force
    }
    else {
        duplicates drop seller buyer, force
    }
    
    // Labels
    label variable seller "Seller firm ID (source)"
    label variable buyer "Buyer firm ID (target)"
    label variable weight "Transaction value"
    
    // Return info
    quietly count
    return scalar n_edges = r(N)
    return scalar n_firms = `n_firms'
    return scalar n_sellers = `n_sellers'
    return scalar n_buyers = `n_buyers'
    
    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: directed_network"
    }
end
</antml9:parameter>

