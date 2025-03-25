import pandas as pd

df = pd.read_csv("results.csv")

# Create a nested dictionary to group metrics by all underscore levels
grouped_metrics = {}

for col in df.columns:
    parts = col.split('_')
    
    # Navigate/create nested dictionary structure
    current_dict = grouped_metrics
    for level in parts[:-1]:  # All parts except the last one are levels
        if level not in current_dict:
            current_dict[level] = {}
        current_dict = current_dict[level]
    
    # Store the final value
    final_level = parts[-1]
    if isinstance(current_dict, dict):
        current_dict[final_level] = df[col].mean()

# Helper function to print nested dictionary with proper indentation
def print_nested_dict(d, indent=0):
    for key, value in d.items():
        print("    " * indent + f"{key}:")
        if isinstance(value, dict):
            print_nested_dict(value, indent + 1)
        else:
            print("    " * (indent + 1) + f"- {value}")

# Print grouped metrics in desired format
print_nested_dict(grouped_metrics)

print("-"*50)

print(df.describe())