# Description
This functionality adds new time steps to an existing scenario (hereafter "reference scenario"). This will be done by creating a new empty scenario (hereafter "new scenario") and:
- Copying all sets from reference scenario and adding new time steps to relevant sets (e.g., adding 2025 between 2020 and 2030 in the set "year")
- Copying all parameters from reference scenario, adding new time steps to relevant parameters, and calculating missing values for the added time steps.

# Main steps
1. An existing scenario is loaded and the desired new years is specified. The new years can be in between existing years or beyond the existing model horizon.
2. A new (empty) scenario is created for adding the new time steps.
3. The new years added to the relevant sets. This include:
- adding new years to the set "year"
- adding new years to the set "cat_year"
- changing "first_modelyear" and "last_modelyear" if needed.

Usage:
    This script can be used either:
    A) By running directly from the command line, example:
    ---------------------------------------------------------------------------
    python f_addNewYear.py --model_ref "MESSAGE_Model" --scen_ref "baseline"
    --years_new "[2015,2025,2035,2045]"
    ---------------------------------------------------------------------------
    (Other input arguments are optional. For more info see Section V below.)

    B) By calling the class "addNewYear" from other python scripts
