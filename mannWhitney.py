import pandas as pd
from scipy.stats import mannwhitneyu

# Datos por caso y variable (en formato [grupo1, grupo2, grupo3])
# Caso 1
case1_unique_transfers = [79, 51, 52]
case1_data_types = [7, 6, 5]
case1_unique_domains = [26, 18, 21]

# Caso 2
case2_unique_transfers = [71, 17]
case2_data_types = [7, 4]
case2_unique_domains = [27, 9]

# Caso 3
case3_unique_transfers = [86, 108]
case3_data_types = [6, 8]
case3_unique_domains = [32, 42]

# Mann-Whitney U test function
def mann_whitney_test(data1, data2):
    stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
    return stat, p_value

# Preparing results for statistical tests
results = {
    "Case 1 - Unique Transfers": mann_whitney_test(case1_unique_transfers[:2], case1_unique_transfers[2:]),
    "Case 1 - Data Types": mann_whitney_test(case1_data_types[:2], case1_data_types[2:]),
    "Case 1 - Unique Domains": mann_whitney_test(case1_unique_domains[:2], case1_unique_domains[2:]),
    "Case 2 - Unique Transfers": mann_whitney_test(case2_unique_transfers[:1], case2_unique_transfers[1:]),
    "Case 2 - Data Types": mann_whitney_test(case2_data_types[:1], case2_data_types[1:]),
    "Case 2 - Unique Domains": mann_whitney_test(case2_unique_domains[:1], case2_unique_domains[1:]),
    "Case 3 - Unique Transfers": mann_whitney_test(case3_unique_transfers[:1], case3_unique_transfers[1:]),
    "Case 3 - Data Types": mann_whitney_test(case3_data_types[:1], case3_data_types[1:]),
    "Case 3 - Unique Domains": mann_whitney_test(case3_unique_domains[:1], case3_unique_domains[1:]),
}

# Create a DataFrame for better visualization
results_df = pd.DataFrame(results, index=["Statistic", "P-value"]).T

# Display the results
print("Mann-Whitney U Test Results for Cases")
print(results_df)
