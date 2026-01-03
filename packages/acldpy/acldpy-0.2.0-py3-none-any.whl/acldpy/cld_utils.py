"""A bunch of utility functions that could be useful for the clc analysis, 
but are not necessary for the core functionality."""

def find_cld_columns(result, result_type):
    """ 
	Adapter that can extract the columns necessary for CLD analysis,
	group_1_col, group_2_col, p_value_col, p_vals, from the result objects 
	of common statistcal test.

	Parameters:
	result_type: A string indicating the type of result ("pg_tk" or "stm_tk").
		result: The result object containing comparison data.
	
	Returns:
		The three columnns that are needed to run the CLD analysis.
	"""

    if result_type == "pg_tk":
        return list(result['A']), list(result['B']), list(result['p-tukey'])     

    if result_type == "stm_tk":
        data_table = result._results_table.data
        data_ids =  [data_table[0].index(i) for i in ["group1", "group2", "p-adj"]]
        return [[row[i] for row in data_table[1:]] for i in data_ids]
