*! assert_var_type v1.1.0  statatest  2025-12-30
*! Assert that a variable has the expected type.
*!
*! Syntax:
*!   assert_var_type varname, type(string) [message(string)] [Verbose]
*!
*! Type options: numeric, string, byte, int, long, float, double, str#
*!
*! Examples:
*!   sysuse auto, clear
*!   assert_var_type price, type("numeric")
*!   assert_var_type make, type("string")
*!   assert_var_type mpg, type("int")

program define assert_var_type, rclass
    version 16
    
    syntax varname, Type(string) [Message(string)] [Verbose]
    
    // Get actual type using extended macro function
    local actual_type : type `varlist'
    
    // Determine if type matches (handle categories: numeric, string)
    local type_match = 0
    
    if "`type'" == "numeric" {
        // Check if any numeric type
        if inlist("`actual_type'", "byte", "int", "long", "float", "double") {
            local type_match = 1
        }
    }
    else if "`type'" == "string" {
        // Check if any string type (starts with "str")
        if substr("`actual_type'", 1, 3) == "str" {
            local type_match = 1
        }
    }
    else {
        // Exact type match
        if "`actual_type'" == "`type'" {
            local type_match = 1
        }
    }
    
    if `type_match' == 0 {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_var_type"
            display as error "  Variable: `varlist'"
            display as error "  Expected type: `type'"
            display as error "  Actual type:   `actual_type'"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_var_type: `varlist' is `actual_type' not `type'"
        }
        noisily display "_STATATEST_FAIL_:assert_var_type_:`varlist' is `actual_type' not `type'_END_"
        exit 9
    }
    
    if "`verbose'" != "" {
        display as text "PASS: assert_var_type"
    }
    noisily display "_STATATEST_PASS_:assert_var_type_"
    
    return local passed "1"
    return local var_type "`actual_type'"
end
