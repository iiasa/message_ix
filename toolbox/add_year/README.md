## Description
This functionality adds new time steps to an existing scenario (hereafter "reference scenario"). This will be done by creating a new empty scenario (hereafter "new scenario") and:
- Copying all sets from reference scenario and adding new time steps to relevant sets (e.g., adding 2025 between 2020 and 2030 in the set "year")
- Copying all parameters from reference scenario, adding new time steps to relevant parameters, and calculating missing values for the added time steps.

## Main features
- It can be used for any MESSAGE scenario, from tutorials, country-level, and global models.
- The new years can be consecutive, between existing years, and after the model horizon.
- The user can define for what regions and parameters the new years should be added. This saves time when adding the new years to only one parameter of the reference scenario, when other parameters had been successfully added to the new scenario previously.

## Main steps
1. An existing scenario is loaded and the desired new years is specified.
2. A new (empty) scenario is created for adding the new time steps.
3. The new years are added to the relevant sets:
- adding new years to the set "year" and "type_year"
- changing "firstmodelyear", "lastmodelyear", "baseyear_macro", and "initializeyear_macro" if needed.
- modifying the set "cat_year" for the new years.
4. The new years are added to the index sets of relevant parameters, and the missing data for the new years are calculated based on interpolation of adjacent data points. The following steps are applied:
- each non-empty parameter is loaded from the reference scenario
- the year-related indexes of the parameter are identified (either 0, 1, and 2 index under MESSAGE scheme)
- the new years are added to the parameter, and the missing data is calculated based on the number of year-related indexes. For example, the new years are added to index "year_vtg" in parameter "inv_cost", while these new years are added both to "year_vtg" and "year_act" in parameter "output".
- the missing data is calculated by interpolation.
- for the parameters with 2 year-related index (such as "output"), a final check is applied so ensure that the vintaging is correct. This step is done based on lifetime of each technology.
5. The changes are commited and saved to the new scenario.

## Notice:
I. This functionality in the current format does not ensure that the new scenario will solve after adding the new years. The user needs to load the new scenario, check some key parameters (like bounds) and solve the new scenario.

## Usage:
This script can be used either:
A) By running directly from the command line, example:
    ```
    python f_addNewYear.py --model_ref "MESSAGE_Model" --scen_ref "baseline" --years_new "[2015,2025,2035,2045]"
    ```
For the full list of input arguments see the explanation in the code.
B) By calling the class "addNewYear" from another python script.
