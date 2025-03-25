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
    
    # 4. Staff Patient Distribution (3 subplots)
    create_staff_patient_distribution_plot(df)
    
    # 5. Service Time Distribution
    create_service_time_plot(df)
    
    # 6. Queue and Service Time per Staff
    create_queue_service_time_per_staff_plot(df)
    
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
        'Rejected by System Overload': df['proportion_totalPatientsDeclinedAccess'].mean() / df['general_totalPatients'].mean()
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
    avg_revenue = df['financials_revenue_total'].mean()
    avg_expenses = df['financials_expenses_total'].mean()
    avg_profit = df['financials_profit_total'].mean()
    
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
    
    plt.title('Total Financial Performance', fontsize=16)
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

def create_queue_service_time_per_staff_plot(df):
    """Create a figure with 2 subplots comparing waiting and service times across staff types"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # 1. Waiting Times Comparison
    ax1.set_title('Average Waiting Time by Staff Type', fontsize=14)
    
    # Calculate average waiting times for each staff type
    staff_wait_times = {
        'Doctor': {
            'Critical': df['doctor_waitingInQueue_duration_critical_average'].mean(),
            'Urgent': df['doctor_waitingInQueue_duration_urgent_average'].mean(),
            'Moderate': df['doctor_waitingInQueue_duration_moderate_average'].mean(),
            'Low': df['doctor_waitingInQueue_duration_low_average'].mean()
        },
        'Nurse': {
            'Moderate': df['nurse_waitingInQueue_duration_moderate_average'].mean(),
            'Low': df['nurse_waitingInQueue_duration_low_average'].mean()
        },
        'Receptionist': {
            'All Patients': df['reception_waitingInQueue_duration_average'].mean()
        }
    }
    
    # Calculate overall average for each staff type
    doctor_avg = sum(staff_wait_times['Doctor'].values()) / len(staff_wait_times['Doctor'])
    nurse_avg = sum(staff_wait_times['Nurse'].values()) / len(staff_wait_times['Nurse'])
    reception_avg = staff_wait_times['Receptionist']['All Patients']
    
    # Create bar chart
    staff_types = ['Doctor', 'Nurse', 'Receptionist']
    wait_times = [doctor_avg, nurse_avg, reception_avg]
    
    # Sort by waiting time
    sorted_indices = np.argsort(wait_times)
    sorted_staff = [staff_types[i] for i in sorted_indices]
    sorted_times = [wait_times[i] for i in sorted_indices]
    
    bars = ax1.bar(sorted_staff, sorted_times, color=['#3498db', '#2ecc71', '#e74c3c'])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{height:.1f} min', ha='center', va='bottom', fontsize=10)
    
    ax1.set_ylabel('Average Wait Time (minutes)', fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add detailed breakdown as text annotation
    details = "Breakdown by Priority:\n"
    details += "Doctor: " + ", ".join([f"{k}: {v:.1f} min" for k, v in staff_wait_times['Doctor'].items()]) + "\n"
    details += "Nurse: " + ", ".join([f"{k}: {v:.1f} min" for k, v in staff_wait_times['Nurse'].items()])
    
    ax1.annotate(details, xy=(0.5, 0.02), xycoords='axes fraction', 
                ha='center', va='bottom', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    # 2. Service Times Comparison
    ax2.set_title('Average Service Time by Staff Type', fontsize=14)
    
    # Calculate average service times for each staff type
    staff_service_times = {
        'Doctor': {
            'Critical': df['doctor_serviceTime_duration_critical_average'].mean(),
            'Urgent': df['doctor_serviceTime_duration_urgent_average'].mean(),
            'Moderate': df['doctor_serviceTime_duration_moderate_average'].mean(),
            'Low': df['doctor_serviceTime_duration_low_average'].mean()
        },
        'Nurse': {
            'Moderate': df['nurse_serviceTime_duration_moderate_average'].mean(),
            'Low': df['nurse_serviceTime_duration_low_average'].mean()
        },
        'Receptionist': {
            'All Patients': df['reception_serviceTime_duration_average'].mean()
        }
    }
    
    # Calculate overall average for each staff type
    doctor_service_avg = sum(staff_service_times['Doctor'].values()) / len(staff_service_times['Doctor'])
    nurse_service_avg = sum(staff_service_times['Nurse'].values()) / len(staff_service_times['Nurse'])
    reception_service_avg = staff_service_times['Receptionist']['All Patients']
    
    # Create bar chart
    service_times = [doctor_service_avg, nurse_service_avg, reception_service_avg]
    
    # Sort by service time
    sorted_service_indices = np.argsort(service_times)
    sorted_service_staff = [staff_types[i] for i in sorted_service_indices]
    sorted_service_times = [service_times[i] for i in sorted_service_indices]
    
    bars = ax2.bar(sorted_service_staff, sorted_service_times, color=['#9b59b6', '#f39c12', '#1abc9c'])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f} min', ha='center', va='bottom', fontsize=10)
    
    ax2.set_ylabel('Average Service Time (minutes)', fontsize=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add detailed breakdown as text annotation
    service_details = "Breakdown by Priority:\n"
    service_details += "Doctor: " + ", ".join([f"{k}: {v:.1f} min" for k, v in staff_service_times['Doctor'].items()]) + "\n"
    service_details += "Nurse: " + ", ".join([f"{k}: {v:.1f} min" for k, v in staff_service_times['Nurse'].items()])
    
    ax2.annotate(service_details, xy=(0.5, 0.02), xycoords='axes fraction', 
                ha='center', va='bottom', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    plt.suptitle('Staff Efficiency Comparison', fontsize=16, y=0.98)
    plt.tight_layout()
    
    plt.savefig('plots/queue_service_time_per_staff.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_plots()