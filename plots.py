import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_data(file_path='results.csv'):
    """Load simulation results from CSV file"""
    return pd.read_csv(file_path)

def create_plots():
    """Create and save multiple plots from simulation data"""
    # Load the data
    df = load_data()
    
    # Set the style for all plots
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 12})
    
    # Create output directory if it doesn't exist
    import os
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    # 1. Patient Distribution by Priority
    create_patient_distribution_plot(df)
    
    # 2. Financial Metrics
    create_financial_metrics_plot(df)
    
    # 3. Waiting Times
    create_waiting_times_plot(df)
    
    # 4. Staff Patient Distribution (3 subplots)
    create_staff_patient_distribution_plot(df)
    
    # 5. Service Time Distribution
    create_service_time_plot(df)
    
    # 6. Nurse Patient Distribution
    create_nurse_distribution_plot(df)
    
    print("All plots have been created and saved to the 'plots' directory.")

def create_patient_distribution_plot(df):
    """Create a pie chart showing the distribution of patients by priority"""
    # Calculate average proportions
    priorities = {
        'Critical': df['proportion_CriticalPatients'].mean(),
        'Urgent': df['proportion_UrgentPatients'].mean(),
        'Moderate': df['proportion_ModeratePatients'].mean(),
        'Low': df['proportion_LowPatients'].mean(),
        'Non-Urgent': df['proportion_NonUrgentPatients'].mean(),
        'Declined Access': df['proportion_totalPatientsDeclinedAccess'].mean() / df['general_totalPatients'].mean()
    }
    
    # Create pie chart
    plt.figure(figsize=(10, 8))
    colors = sns.color_palette('viridis', len(priorities))
    
    # Sort wedges from highest to lowest
    sorted_priorities = dict(sorted(priorities.items(), key=lambda x: x[1], reverse=True))
    
    wedges, texts, autotexts = plt.pie(
        sorted_priorities.values(), 
        labels=sorted_priorities.keys(),
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=[0.05] * len(sorted_priorities)  # Explode all slices slightly
    )
    
    # Enhance the appearance
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=12)
    plt.axis('equal')
    plt.title('Patient Distribution by Priority Level', fontsize=16, pad=20)
    
    plt.savefig('plots/patient_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_financial_metrics_plot(df):
    """Create a bar chart showing financial metrics"""
    # Calculate average values
    avg_revenue = df['totalFinancials'].mean()
    avg_expenses = df['totalExpenses'].mean()
    avg_profit = df['totalProfit'].mean()
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    metrics = ['Revenue', 'Expenses', 'Profit']
    values = [avg_revenue, avg_expenses, avg_profit]
    
    bars = plt.bar(metrics, values, color=['#2ecc71', '#e74c3c', '#3498db'])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'${height:.2f}',
                ha='center', va='bottom', fontsize=12)
    
    plt.title('Average Financial Performance', fontsize=16)
    plt.ylabel('Amount ($)', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add profit margin as text annotation
    profit_margin = (avg_profit / avg_revenue) * 100
    plt.annotate(f'Profit Margin: {profit_margin:.1f}%', 
                xy=(0.5, 0.9), 
                xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    plt.savefig('plots/financial_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_waiting_times_plot(df):
    """Create a horizontal bar chart comparing different waiting times"""
    # Calculate average waiting times
    avg_arrival_wait = df['arrival_waitingTime_average'].mean()
    avg_reception_wait = df['reception_waitingInQueue_duration_average'].mean()
    avg_reception_service = df['reception_serviceTime_duration_average'].mean()
    
    # Create horizontal bar chart
    plt.figure(figsize=(12, 6))
    
    metrics = ['Arrival Wait Time', 'Reception Queue Wait', 'Reception Service Time']
    values = [avg_arrival_wait, avg_reception_wait, avg_reception_service]
    
    # Sort by duration
    sorted_indices = np.argsort(values)
    sorted_metrics = [metrics[i] for i in sorted_indices]
    sorted_values = [values[i] for i in sorted_indices]
    
    # Create horizontal bars with gradient colors
    bars = plt.barh(sorted_metrics, sorted_values, 
                   color=sns.color_palette("YlOrRd", len(metrics)))
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{width:.2f} min', 
                ha='left', va='center', fontsize=12)
    
    plt.title('Average Patient Wait Times', fontsize=16)
    plt.xlabel('Time (minutes)', fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.savefig('plots/waiting_times.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_service_time_plot(df):
    """Create a stacked bar chart showing service time distribution"""
    # Calculate average service times
    reception_time = df['reception_serviceTime_duration_total'].mean()
    reception_wait = df['reception_waitingInQueue_duration_total'].mean()
    arrival_time = df['arrival_waitingTime_total'].mean()
    
    # Calculate percentages
    total_time = reception_time + reception_wait + arrival_time
    reception_pct = (reception_time / total_time) * 100
    reception_wait_pct = (reception_wait / total_time) * 100
    arrival_pct = (arrival_time / total_time) * 100
    
    # Create stacked bar
    plt.figure(figsize=(10, 6))
    
    # Create a single stacked bar
    plt.bar(0, arrival_pct, color='#3498db', label='Arrival Time')
    plt.bar(0, reception_wait_pct, bottom=arrival_pct, color='#e74c3c', label='Reception Queue Wait')
    plt.bar(0, reception_pct, bottom=arrival_pct+reception_wait_pct, color='#2ecc71', label='Reception Service')
    
    # Remove x-axis ticks and labels
    plt.xticks([])
    plt.xlim(-0.5, 0.5)
    
    # Add percentage labels
    plt.text(0, arrival_pct/2, f'{arrival_pct:.1f}%', ha='center', va='center', fontsize=12, color='white')
    plt.text(0, arrival_pct + reception_wait_pct/2, f'{reception_wait_pct:.1f}%', ha='center', va='center', fontsize=12, color='white')
    plt.text(0, arrival_pct + reception_wait_pct + reception_pct/2, f'{reception_pct:.1f}%', ha='center', va='center', fontsize=12, color='white')
    
    plt.ylabel('Percentage of Total Time (%)', fontsize=14)
    plt.title('Distribution of Patient Time in System', fontsize=16)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)
    
    # Add total time annotation
    plt.annotate(f'Total Time: {total_time:.2f} minutes', 
                xy=(0.5, 0.95), 
                xycoords='axes fraction',
                ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    plt.savefig('plots/service_time_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_nurse_distribution_plot(df):
    """Create a pie chart showing nurse patient distribution"""
    # Calculate average proportions
    moderate = df['nurse_proportion_moderatePatients'].mean()
    low = df['nurse_proportion_lowPatients'].mean()
    
    # Create pie chart
    plt.figure(figsize=(10, 6))
    
    labels = ['Moderate Priority', 'Low Priority']
    sizes = [moderate, low]
    colors = ['#3498db', '#e74c3c']
    explode = (0.1, 0)  # explode the 1st slice
    
    wedges, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels,
                                      autopct='%1.1f%%', startangle=90, colors=colors,
                                      wedgeprops={'edgecolor': 'w', 'linewidth': 1})
    
    # Enhance the appearance
    plt.setp(autotexts, size=12, weight="bold")
    plt.setp(texts, size=14)
    plt.axis('equal')
    plt.title('Nurse Patient Distribution by Priority', fontsize=16)
    
    plt.savefig('plots/nurse_patient_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_staff_patient_distribution_plot(df):
    """Create a figure with 3 pie charts showing patient distribution for different staff"""
    plt.figure(figsize=(18, 6))
    
    # 1. Receptionist - All patients by priority
    plt.subplot(1, 3, 1)
    
    # Calculate average proportions for receptionist
    reception_priorities = {
        'Critical': df['proportion_CriticalPatients'].mean(),
        'Urgent': df['proportion_UrgentPatients'].mean(),
        'Moderate': df['proportion_ModeratePatients'].mean(),
        'Low': df['proportion_LowPatients'].mean(),
        'Non-Urgent': df['proportion_NonUrgentPatients'].mean()
    }
    
    # Sort wedges from highest to lowest
    sorted_reception = dict(sorted(reception_priorities.items(), key=lambda x: x[1], reverse=True))
    
    colors_reception = sns.color_palette('viridis', len(reception_priorities))
    wedges, texts, autotexts = plt.pie(
        sorted_reception.values(), 
        labels=sorted_reception.keys(),
        autopct='%1.1f%%',
        startangle=90,
        colors=colors_reception,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    plt.axis('equal')
    plt.title('Receptionist: Patient Distribution', fontsize=14)
    
    # 2. Nurse - Moderate vs Low patients
    plt.subplot(1, 3, 2)
    
    # Calculate average proportions for nurse
    moderate = df['nurse_proportion_moderatePatients'].mean()
    low = df['nurse_proportion_lowPatients'].mean()
    
    labels = ['Moderate Priority', 'Low Priority']
    sizes = [moderate, low]
    colors_nurse = ['#3498db', '#e74c3c']
    
    wedges, texts, autotexts = plt.pie(
        sizes, 
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors_nurse,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    plt.axis('equal')
    plt.title('Nurse: Patient Distribution', fontsize=14)
    
    # 3. Doctor - Critical, Urgent, Moderate, Low patients
    plt.subplot(1, 3, 3)
    
    # For doctor, we need to calculate the proportion of patients that reach the doctor
    # We'll use the patient priority distribution but exclude non-urgent patients
    # and normalize the remaining proportions
    doctor_priorities = {
        'Critical': df['proportion_CriticalPatients'].mean(),
        'Urgent': df['proportion_UrgentPatients'].mean(),
        'Moderate': df['proportion_ModeratePatients'].mean() * moderate,  # Only moderate patients that remain moderate
        'Low': df['proportion_LowPatients'].mean() * low  # Only low patients that remain low
    }
    
    # Normalize to make sure they sum to 100%
    total = sum(doctor_priorities.values())
    doctor_priorities = {k: v/total for k, v in doctor_priorities.items()}
    
    # Sort wedges from highest to lowest
    sorted_doctor = dict(sorted(doctor_priorities.items(), key=lambda x: x[1], reverse=True))
    
    colors_doctor = sns.color_palette('plasma', len(doctor_priorities))
    wedges, texts, autotexts = plt.pie(
        sorted_doctor.values(), 
        labels=sorted_doctor.keys(),
        autopct='%1.1f%%',
        startangle=90,
        colors=colors_doctor,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    plt.axis('equal')
    plt.title('Doctor: Patient Distribution', fontsize=14)
    
    # Add overall title
    plt.suptitle('Patient Distribution by Staff Type', fontsize=16, y=1.05)
    
    plt.tight_layout()
    plt.savefig('plots/staff_patient_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_plots()