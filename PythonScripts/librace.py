"""
Defining a library module for Aim 1 Indicator 3: Race of SRD project
This file contains functions to calculate majority and entropy.

This is a module. Should be imported in the main script for the calculation of race measures as:
(import librace) or (import librace as ...) or from (librace import *)

Last updated: 01 March, 2024
"""

# Function to classify each county based on Majority Minority Rule
def classify_county(row):
    percentages = [(row['PWhite'], 'White'), (row['PBlack'], 'Black'),
                   (row['POther'], 'Other')]
    max_percentage, majority_group = max(percentages)

    if max_percentage < 50:
        return 'No majority'
    elif max_percentage >= 90:
        return f'{majority_group}-dominant'
    else:
        percentages.remove((max_percentage, majority_group))
        if any(perc >= 10 for perc, _ in percentages):
            return f'{majority_group}-other'
        else:
            return f'{majority_group}-shared'


# Function to compute entropy for each county
import numpy as np
def compute_entropy(row):
    props = row[['White_Prop', 'Black_Prop', 'Other_Prop']]
    entropy = -sum(p * np.log(p) for p in props if p > 0)
    return entropy