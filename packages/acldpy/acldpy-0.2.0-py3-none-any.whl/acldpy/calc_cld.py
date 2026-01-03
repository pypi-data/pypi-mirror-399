"""The core functions to calculate a compact letter display (cld).

The objective of the cld is to summarize the results of multiple pairwise comparisons. Treatments
that are not significantly different from one another share at least one letter, while treatments
that are significantly different share no letters. 


Simple definitions of key terms:
    Treatment: All samples that are "the same", i.e. replicates of one another, are the same
        treatment. Users perform a statistical test to compare different treatments. The 
        statistical difference between different treatments is what the cld seeks to express. In the
        the letter matrix, each row corresponds to a treatment.
    Letter: In the final cld, letters will be assigned. To calculate which treatment should get
        which letters, algorithms manipulate the letter matrix. Each column of the letter matrix
        is translated into a letter after the calculations are finished.
    Letter matrix: A 2D matrix where each row is a treatment, each column is a letter, and the 
        elements indicate wether the treatment should (1) or should not (0) have the letter
        assigned. When calculating the cld, the letter matrix is filled and extended, and in the
        end, translated into the letters that each treatment should receive.
    Capital H: The set of all treatment pairs whose elements are significantly different from one
        another.

Further documentation: https://github.com/anyusernameisokay/acldpy
Created by Noël Jung, 2025. 

TODO:
-Bad variables names.
-Letter_matrix vs M.
-In check input function: Call list_unique_treatments.
"""

from typing import List, Tuple, Dict, Optional
import numpy as np

def check_input(
    first_treatments: List[str],
    second_treatments: List[str],
    p_values: List[float],
    alpha: float):
    """
    Checks whether the user input looks like it is supposed to.
        - Each treatment pair must have an assocoiated p-value.
        - Each possible treatment pair must be represented exactly once.
        - The p-values and alpha must be between 0 and 1.

        Parameters: 
            first_treatments: List of all first treatments of multiple pairwise comparisons.
            second_treatments: List of all second treatments of multiple pairwise comparisons.
            p_values: List of all p-values on which the comparisons are based on.
            alpha: Significance level. 
    """
    # Check whether all input lists have the same length.
    assert (len(first_treatments) == len(second_treatments) == len(p_values)), \
    "Inputs 'first_treatments', 'second_treatments', and 'p_values' must have the same length."

    # Check whether each treatment pair is present and unique.
    all_treatments = first_treatments + second_treatments
    unique_treatments = tuple(list(dict.fromkeys(all_treatments)))
    all_treatment_pairs = []
    for t in unique_treatments:
        for t2 in unique_treatments:
            if t != t2:
                pair = tuple(sorted((t, t2)))
                all_treatment_pairs.append(pair)
    unique_treatment_pairs = set(all_treatment_pairs)

    provided_treatment_pairs = set()
    for treat_one, treat_two in zip(first_treatments, second_treatments):
        assert treat_one != treat_two, \
        f"Comparisons between the same treatment ({treat_one}) not allowed."

        pair = tuple(sorted((treat_one, treat_two)))

        assert pair not in provided_treatment_pairs, \
        f"Multiple p-values for treatment pair {pair} provided. Each pair must only occur once."

        provided_treatment_pairs.add(pair)
    provided_treatment_pairs = set(provided_treatment_pairs)
    print(provided_treatment_pairs)

    assert unique_treatment_pairs == provided_treatment_pairs, \
    f"Input does not include comparisons of all treatment pairs:\n \
Provided treatment pairs: {provided_treatment_pairs} \n \
All possible treatment pairs: {unique_treatment_pairs}"

    # Check whether p-values are between 0 and 1.
    for p_value in p_values:
        assert 0 <= p_value <= 1, \
        f"All p-values must be between 0 and 1. Invalid p-value found: {p_value}"

    # Check whether alpha is between 0 and 1.
    assert  0 <= alpha <= 1, \
    f"Alpha must be between 0 and 1. Invalid value: {alpha}"


def calc_capital_h(
    first_treatments: List[str],
    second_treatments: List[str],
    p_values: List[float],
    alpha: float
    ) -> List[Tuple[str, str]]:
    """
    Checks which treatments are significantly different from one another. Treatments that are
    significantly different are added to capital_h as a tuple. Treatments are signficantly
    different from one another, when their respective p-value is below the significance level.
    
        Parameters: 
            first_treatments: List of all first treatments of multiple pairwise comparisons.
            second_treatments: List of all second treatments of multiple pairwise comparisons.
            p_values: List of all p-values on which the comparisons are based on.
            alpha: Significance level. 
        
        Returns:
            capital_h: List of treatment pairs with significant difference.
    """
    capital_h = []
    for (treat_one, treat_two, p_value) in zip(first_treatments, second_treatments, p_values):
        if p_value < alpha:
            capital_h.append((treat_one, treat_two))
    return capital_h

def list_unique_treatments(
        first_treatments: List[str],
        second_treatments: List[str],
        letter_order: Optional[List[str]],
        ) -> Tuple:
    """
    Lists all treatments that are included in the comparison. If an order is given, the treatments
    are put in that order.
    
        Parameters: 
            first_treatments: List of all first treatments of multiple pairwise comparisons.
            second_treatments: List of all second treatments of multiple pairwise comparisons.
            letter_order: Optional. List of all treatments in the order they should be assigned
                letters to. The first treatment in the list will get the "lowest" letter.
                           
        Returns:
            unique_treatments: All unique treatments.
    """
    all_treatments = first_treatments + second_treatments
    unique_treatments = tuple(list(dict.fromkeys(all_treatments)))
    if isinstance(letter_order, list):
        assert sorted(unique_treatments) == sorted(letter_order), \
        f"""letter_order must be a list containing all treatments exactly once.

        Treatments listed in letter_order: {letter_order}
        All treatments: {unique_treatments}
        """
        unique_treatments = tuple(letter_order)

    return unique_treatments

def insert_new_columns(
        M: np.ndarray,
        i: np.ndarray,
        j: np.ndarray
        ) -> List[np.ndarray]:
    """
    Inserts new columns to the letter matrix if required. New columns are required for each
    original column that contains 1 in two rows, that correspond to treatments that are
    significantly different from one another.
    In that case, the original column is removed, and  a two new ones are added: 
        1. Contains 1 in row 1 and 0 inrow 2.
        2. Contains 0 in row 1 and 1 in row 2.
    This function is called once for each pair with significant difference.

        Parameters:
            M: Letter matrix as a 2D numpy array, where each column corresponds to a treatment,
                and each row corresponds to a letter (1 indicates presence of letter, 0 absence).
            i: Indices indicating for which letters the first treatment has a 1.
            j: Indices indicating for which letters the second treatment has a 1.

        Returns:
            new_matrix_columns: List of all columns after the insertion step.
    """
    new_matrix_columns = []

    # Iterate over columns of M. (M.shape[1] is number of columns).
    # And check whether column needs to be duplicated.
    for column_id in range(M.shape[1]):
        column_in_M = M[:, column_id]
        ith_position = column_in_M[i]
        jth_position = column_in_M[j]

        # No insertion needed, original column can be kept.
        if (ith_position == 1 and jth_position == 0) or (ith_position == 0 and jth_position == 1):
            new_matrix_columns.append(column_in_M)

        elif ith_position == 0 and jth_position == 0:
            new_matrix_columns.append(column_in_M)

        # Column needs to be duplicated if it contains 1 on both, i and j.
        elif ith_position == 1 and jth_position == 1:
            # One copy must be like original, but with position 0, and jth position 1.
            # The other copy must be like original, but with position 1, and jth position 0.
            column_copy_one = column_in_M.copy()
            column_copy_one.put([i, j], [0, 1])

            column_copy_two = column_in_M.copy()
            column_copy_two.put([i, j], [1, 0])

            new_matrix_columns.append(column_copy_one)
            new_matrix_columns.append(column_copy_two)

    return new_matrix_columns

def absorb_columns(
        M: List[np.ndarray]
        ) -> List[np.ndarray]:
    """
    Absorbs columns, if possible. A column (each column is a letter) can be absorbed (= removed)
    if there exist another column that contains 1 for all the same treatments (rows = treatments).
    In the following example, L1 can be absorbed (removed), by L2.
       L1 L2 L3  
    T1 0  1  0
    T2 1  1  0
    T3 1  1  1
    T4 0  0  1
    
        Parameter:
            M: List of all columns after the insertion step.

        Returns:
            not_absorbed_cols: The letter matrix containing only columns that were not absorbed.
    """
    # Collects all columns that need to be kept.
    not_absorbed_columns = []

    # Tracks cols that have been absobed to avoid columns reffering to each other when determing
    # whether they should be absorbed.
    absorbed_column_ids = []

    for column_one_id, column_one in enumerate(M):
        can_col_one_be_absorbed = False
        non_zero_col_one_idx = column_one.nonzero()
        # Compare against each other column.
        for column_two_id, column_two in enumerate(M):
            if (column_one_id == column_two_id) or (column_one_id in absorbed_column_ids):
                continue

            non_zero_col_two_idx = column_two.nonzero()
            is_col_one_completly_in_col_two = np.isin(non_zero_col_one_idx,
                non_zero_col_two_idx).all()
            if is_col_one_completly_in_col_two:
                # Column one should not be kept.
                absorbed_column_ids.append(column_one_id)
                can_col_one_be_absorbed = True
                break

        # If we reach here, col one could not be absorbed.
        if not can_col_one_be_absorbed:
            not_absorbed_columns.append(column_one)

    return not_absorbed_columns

def insert_absorb(
        unique_treatments: Tuple,
        capital_h: List[Tuple[int, int]]
        ) -> np.ndarray:
    """
    Iterates over the treatment pairs with significant difference to apply the insert-absorb
    algorithm to generate the initial letter matrix.

        Parameters:
            unique_treatments: All unique treatments.
            capital_h: List of treatment pairs with significant difference.

        Returns:
            M: Letter matrix as a 2D numpy array, where each column corresponds to a treatment and
                each row corresponds to a letter (1 indicates presence of letter, 0 absence).
    """
    # 1) Generate inital treatment column.
    index_column = np.array(unique_treatments)
    column_one = np.ones(len(unique_treatments), dtype=np.int8).reshape(-1, 1)
    M = column_one
    # 2) Iterate over significantly different pairs.
    for (treat_one, treat_two) in capital_h:
        # 2.1) Find indices of the treatments that are significantly different.
        treat_one_index = np.where(index_column == treat_one)[0][0]
        treat_two_index = np.where(index_column == treat_two)[0][0]

        # 2.2) Insert and absorb.
        M = insert_new_columns(M, treat_one_index, treat_two_index)
        M = absorb_columns(M)

        # 2.3) Reshape letter_matrix back to 2D array.
        M = np.array(M).T
    return M

def sweep(
        M: np.ndarray
        ) -> np.ndarray:
    """
    Performs sweeping of the letter matrix. A column can be removed if for each possible pair of 1s
    in its rows, there is at least one other column that contains 1s for in the same respective
    rows. In the following example column L2 can be removed by sweeping.
      L1 L2 L3  L4
    T1 1  1  0  1
    T2 1  0  0  1
    T3 1  1  1  0
    T4 0  0  1  0
    T5 0  1  1  1

        Parameter:
            M: 2D letter matrix, after insert-absorb.

        Returns:
            M: 2D letter matrix, after sweep
    """
    # Iterate over letters (columns in the letter matrix).
    for first_column_nr, unique_letter_column in enumerate(M.T):
        # Go through each treatment in the column and check letter.
        for i_index, i_th_treat_let in enumerate(unique_letter_column):

            # If the letter is 0, nothing needs to be done.
            if i_th_treat_let == 0:
                continue
            # If the letter is 1, check whether it can be removed. (aka, replaced with 0)
            # Check for redundancy.
            # The ith letter can be changed in this first column from 1 to 0 if all other
            # treatments (all jth) that share the letter with i, also share another letter
            # with i in another column.
            jth_share_letter_with_ith = []

            # Go through the other treatments in the same column.
            for j_index, j_th_treat_let in enumerate(unique_letter_column):
                # Skip if j_index is the same as i_index.
                # Also skip if j_th_treat_let is 0.
                if j_index == i_index or j_th_treat_let == 0:
                    continue
                # If both, i_th_treat_let and j_th_treat_let are 1,
                # Check if they have common letter in any other column.
                ith_and_jth_pair_found_in_other_column = False
                for second_column_nr, second_column in enumerate(M.T):
                    # Skip if second_column_nr is the same as first_column_nr.
                    if second_column_nr == first_column_nr:
                        continue
                    # Check if both treatments have letter 1 in any second column.
                    if second_column[i_index] == 1 and second_column[j_index] == 1:
                        ith_and_jth_pair_found_in_other_column = True
                        break
                jth_share_letter_with_ith.append(ith_and_jth_pair_found_in_other_column)
            # Check if all pairs between i and any j, share a letter in at least one column.
            # If jth_share_letter_with_ith is empty, it means that i_th_treat_let was the only
            # one with letter 1 in this column. In that case, wether it can be removed or not,
            # depends on whether the treatment has any other 1 in its row.
            ith_letter_is_only_letter_in_ith_row = np.sum(M[i_index, :]) == 1
            ith_letter_connected_to_all_jths_in_other_cols = (all(jth_share_letter_with_ith)
                and len(jth_share_letter_with_ith) > 0) # TODO: Name bad

            if ith_letter_connected_to_all_jths_in_other_cols:
                M[i_index, first_column_nr] = 0
            if not ith_letter_is_only_letter_in_ith_row and len(jth_share_letter_with_ith) == 0:
                M[i_index, first_column_nr] = 0

    # Remove empty columns (all zeros).
    non_empty_columns = []
    for column in M.T:
        if not np.all(column == 0):
            non_empty_columns.append(column)
    M = np.array(non_empty_columns).T

    return M

def determine_letters(
        letter_matrix: np.ndarray,
        unique_groups: Tuple,
        letter_type: str ='low_a-z'
        ) -> Dict[str, str]:
    """
    Translates the letter matrix into a dictionary mapping each treatment to its assigned letters.

        Parameters:
            letter_matrix: 2D letter matrix after sweep and sorting.
            unique_treatments: All unique treatments.
            letter_type: Type of letters to use. 'low_a-z' for lowercase letters, 'up_A-Z' for 
                uppercase letters.
        
        Returns:
            cld_dict: Dictionary mapping each treatment to its assigned letters.
    """
    cld_dict = {}

    n_letters = letter_matrix.shape[1]
    if letter_type == 'low_a-z':
        letters = [chr(i) for i in range(97, 97 + n_letters)]  # a-z
    elif letter_type == 'up_A-Z':
        letters = [chr(i) for i in range(65, 65 + n_letters)]  # A-Z
    else:
        raise ValueError("Not a valid letter type was chosen. Choose 'low_a-z' or 'up_A-Z'.")

    for i, group in enumerate(unique_groups): # TODO: Name bad
        group_letters = ''
        for j in range(n_letters):
            if letter_matrix[i, j] == 1:
                group_letters += letters[j]
        cld_dict[group] = group_letters

    return cld_dict

def fill_all_zero_rows(letter_matrix: np.ndarray) -> np.ndarray:
    """
    Creates a new column if there exists one or more rows, that have not a single 1, but only 0s in
    their columns. The new column has 1s in all the rows that were all-0 rows before. This is
    necessary as after insert-absorb and sweep, there exists the possibility that some treatments
    have no letters assigned to them and the subsequent translation to letters requires that each
    treatment has at least one letter

        Parameter:
            letter_matrix: 2D letter matrix after sweep.

        Returns:
            Either: Original letter matrix if no all-0 rows were found.
            Or: Letter matrix after adding column for all-0 rows.
    """
    # Check for any all-0 rows.
    zero_rows = np.all(letter_matrix == 0, axis=1)
    any_row_all_zero = np.any(zero_rows)
    if any_row_all_zero:
        # Create a new matrix with an additional column.
        new_matrix = np.zeros((letter_matrix.shape[0], letter_matrix.shape[1] + 1), dtype=np.int8)
        # Copy the old matrix into the new one.
        new_matrix[:, :-1] = letter_matrix
        # Set the new column to 1 for all-0 rows.
        new_matrix[zero_rows, -1] = 1
        return new_matrix

    return letter_matrix

def sort_letters(
        M: np.ndarray
        ) -> np.ndarray:
    """
    Is called, if the user provided a specific order for the treatments. Sorts the columns of the
    binary letter matrix by prioritizing columns with 1s in higher rows.

    Columns are ordered left to right based on the earliest occurrence of a 1 in each column:
        - Columns with a 1 in the first row are placed furthest to the left.
        - If multiple columns have a 1 in the same row, the next row is used to break the tie.
        - This process continues row by row until all columns are ordered.

       L1 L2 L3         L1 L2 L3       
    T1 0  1  0        T1 1  0  0  
    T2 1  1  0   -->  T2 1  1  0  
    T3 1  1  1        T3 1  1  1  
    T4 0  0  1        T4 0  0  1    

        Parameter:
            M: Unsorted letter matrix.

        Returns
            sorted_M: Matrix after the sorting algorithm.
    """
    sorted_indices = np.lexsort(M[::-1, :])
    sorted_indices =np.flip(sorted_indices)
    sorted_M = M[:, sorted_indices]

    return sorted_M

def verify_cld(final_letters, first_treatments, second_treatments, p_values, alpha):
    """
    Checks whether the calculated cld is accurate by iterating over all treatment pairs and
    confirming that treatments that are not significantly different share at least one letter, and
    treatments that are significantly different share no letters.

        Parameters:
            final_letters: Dictionary mapping each treatment to its assigned letters, as returned
                from determine_letters().
            first_treatments: List of all first treatments of multiple pairwise comparisons.
            second_treatments: List of all second treatments of multiple pairwise comparisons.
            p_values: List of all p-values of the comparisons.
            alpha: Significance level. 

        Returns nothing.
    """
    for (treat_one, treat_two, p_value) in zip(first_treatments, second_treatments, p_values):
        letters_one = final_letters[treat_one]
        letters_two = final_letters[treat_two]

        # Check if there is any common letter between the two groups.
        shared_letters = set(letters_one).intersection(set(letters_two))

        if p_value < alpha:
            # Groups should not share any letters.
            assert shared_letters == set(), \
            f"Groups {treat_one} and {treat_two} share letters {shared_letters} but should not."
        else:
            # Groups should share at least one letter.
            assert shared_letters != set(), \
            f"Groups {treat_one} and {treat_two} do not share any letters but should."

def run_cld(
    first_treatments: List[str],
    second_treatments: List[str],
    p_values: List[float],
    alpha: float = 0.05,
    letter_order: Optional[List[str]] = None,
    ) -> Dict[str, str]:
    """
    Assigns letters to indicate statistically significant differences between treatments following
    multiple pairwise comparisons. Implementation of the insert-absorb and sweep algorithms by
    Piepho (2004). First, all significant differences are identified. Then, the insert-absorb and
    sweep algorithms are applied to find a compact letter display (cld). Finally, the letter
    assignment is verified.

        Parameters: 
            first_treatments: List of all first treatments of multiple pairwise comparisons.
            second_treatments: List of all second treatments of multiple pairwise comparisons.
            p_values: List of all p-values of the comparisons.
            alpha: Significance level. 
            letter_order: Optional. List of all treatments in the order they should be assigned
                letters to. The first treatment in the list will get the "lowest" letter.
        
        Returns: 
            final_letters: Dictionary mapping each treatment to its assigned letters.
    """
    # 0) Check input
    check_input(first_treatments, second_treatments, p_values, alpha)
    # 1) Filter out all pairs with significant differences (capital_h).
    capital_h = calc_capital_h(first_treatments, second_treatments, p_values, alpha)
    # 2) List all unique treatments.
    unique_treatments = list_unique_treatments(first_treatments, second_treatments, letter_order)
    # 3) Insert and absorb algorithm.
    letter_matrix = insert_absorb(unique_treatments, capital_h)
    #if DEBUG and TEST_PERMUT:
    #    letter_matrix = rearrange_columns(letter_matrix)
    # 4) Sweep
    letter_matrix = sweep(letter_matrix)
    # 5) Fill in any all-0 rows
    letter_matrix = fill_all_zero_rows(letter_matrix)
    # 6) Sort letter matrix rows according to unique treatments order.
    letter_matrix = (letter_matrix if isinstance(letter_order, type(None))
        else sort_letters(letter_matrix))
    # 7) Translate matrix into letters.
    final_letters = determine_letters(letter_matrix, unique_treatments)
    # 8) Verify that the calculated solutions solves the problem correctly.
    verify_cld(final_letters, first_treatments, second_treatments, p_values, alpha)

    return final_letters

DEBUG = False
TEST_PERMUT = False
"""
def rearrange_columns(M):
    # Not used yet....
    print("Before permutation")
    print(M)
    perm_one = [4,3,2,1,0,5]

    idx = np.empty_like(perm_one)
    idx[perm_one] = np.arange(len(perm_one))
    M[:, idx]
    M[:] = M[:, idx] 
    print("After permutation")
    print(M)
    return M

# Debugging

if __name__ == "__main__":
    DEBUG = True
    if DEBUG:
        
        group_1_names = ["T1"] * 7 + ["T2"] * 6 + ["T3"] * 5 + 
        ["T4"] * 4 + ["T5"] * 3 + ["T6"] * 2 + ["T7"] * 1 + ["T8"] * 0
        group_2_names = []
        for t in range(1, 9):
            for t2 in range(t + 1, 9):
                group_2_names.append(f"T{t2}")
        print(group_1_names)
        print(group_2_names)
        p_values = [1] * len(group_1_names)
        sig_dif_pairs = [["T1", "T7"], ["T1", "T8"], ["T2", "T4"], ["T2", "T5"], ["T3", "T5"]]
        for t1, t2 in sig_dif_pairs:
            for p_id in range(len(p_values)):
                if (group_1_names[p_id] == t1) and (group_2_names[p_id] == t2):
                    print(t1, t2)
                    p_values[p_id] = 0
        
        final_letters = run_cld(group_1_names, group_2_names, p_values,)
        print(final_letters)

"""
