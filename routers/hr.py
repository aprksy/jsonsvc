from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import Optional, List
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

# API keys for HR endpoints
VALID_HR_API_KEYS = {
    "hr_readonly": "hr_12345abcde",
    "hr_admin": "hr_admin_67890xyz",
    "payroll_access": "payroll_24680mnop"
}

def verify_hr_api_key(api_key: str = Header(..., description="API Key for HR endpoints", alias="X-API-Key")):
    if api_key not in VALID_HR_API_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid HR API key")
    return api_key

def load_hr_data():
    data_file = Path("data/hr.json")
    if not data_file.exists():
        # Generate sample HR data
        default_data = {
            "employees": generate_employee_data(),
            "policies": generate_policy_data(),
            "payroll": generate_payroll_data()
        }
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

def generate_employee_data():
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "IT", "Customer Support"]
    positions = ["Software Engineer", "Product Manager", "Sales Representative", "HR Specialist", 
                "Financial Analyst", "Operations Manager", "IT Support", "Customer Success Manager"]
    locations = ["New York", "San Francisco", "London", "Tokyo", "Berlin", "Singapore", "Toronto", "Sydney"]
    
    employees = []
    employee_id = 1000
    
    for i in range(50):
        first_name = random.choice(["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"])
        last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])
        dept = random.choice(departments)
        
        employees.append({
            "employee_id": f"EMP{employee_id}",
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@company.com",
            "department": dept,
            "position": random.choice(positions),
            "location": random.choice(locations),
            "hire_date": (datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460))).strftime("%Y-%m-%d"),
            "salary_band": random.choice(["A", "B", "C", "D", "E"]),
            "manager_id": f"EMP{random.randint(1000, 1040)}",
            "status": random.choice(["Active", "On Leave", "Probation"]),
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        })
        employee_id += 1
    
    return employees

def generate_policy_data():
    policy_types = ["Leave", "Expense", "Code of Conduct", "Remote Work", "Benefits", "Travel", "IT Security", "Performance"]
    
    policies = []
    
    for policy_type in policy_types:
        for i in range(3):
            policies.append({
                "policy_id": f"POL-{policy_type[:3].upper()}-{i+1:03d}",
                "policy_type": policy_type,
                "title": f"{policy_type} Policy v{i+1}.0",
                "effective_date": (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                "version": f"{i+1}.0",
                "category": policy_type,
                "description": f"Official company policy regarding {policy_type.lower()} procedures and guidelines.",
                "document_url": f"/policies/{policy_type.lower()}-v{i+1}.0.pdf",
                "last_updated": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
            })
    
    return policies

def generate_payroll_data():
    periods = [f"{year}-{month:02d}" for year in [2023, 2024] for month in range(1, 13)]
    payroll_entries = []
    entry_id = 1
    
    # Generate payroll for each employee for random periods
    employees = generate_employee_data()
    
    for employee in employees[:30]:  # Payroll for first 30 employees
        for period in random.sample(periods, 8):  # 8 random periods per employee
            base_salary = random.randint(50000, 120000)
            bonus = random.randint(0, 10000) if random.random() > 0.7 else 0
            deductions = random.randint(500, 2000)
            
            payroll_entries.append({
                "id": entry_id,
                "employee_id": employee["employee_id"],
                "employee_name": employee["full_name"],
                "department": employee["department"],
                "period": period,
                "base_salary": base_salary,
                "bonus": bonus,
                "overtime": random.randint(0, 2000) if random.random() > 0.8 else 0,
                "deductions": deductions,
                "net_pay": base_salary + bonus - deductions,
                "payment_date": f"{period}-{random.randint(25, 28)}",
                "payment_method": random.choice(["Direct Deposit", "Wire Transfer"]),
                "status": random.choice(["Paid", "Processing", "Completed"])
            })
            entry_id += 1
    
    return payroll_entries

@router.get("/employees", dependencies=[Depends(verify_hr_api_key)])
async def get_employees(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    name: Optional[str] = Query(None, description="Filter by employee name (full or partial)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by employment status")
):
    data = load_hr_data()
    employees = data["employees"]
    
    # Apply filters
    filtered_employees = employees
    
    if employee_id:
        filtered_employees = [e for e in filtered_employees if e["employee_id"] == employee_id]
    
    if name:
        name_lower = name.lower()
        filtered_employees = [
            e for e in filtered_employees 
            if name_lower in e["full_name"].lower() or 
               name_lower in e["first_name"].lower() or 
               name_lower in e["last_name"].lower()
        ]
    
    if department:
        filtered_employees = [e for e in filtered_employees if e["department"].lower() == department.lower()]
    
    if status:
        filtered_employees = [e for e in filtered_employees if e["status"].lower() == status.lower()]
    
    if not filtered_employees:
        raise HTTPException(status_code=404, detail="No employees found matching criteria")
    
    return {
        "count": len(filtered_employees),
        "employees": filtered_employees
    }

@router.get("/employees/{employee_id}", dependencies=[Depends(verify_hr_api_key)])
async def get_employee_by_id(employee_id: str):
    data = load_hr_data()
    employees = data["employees"]
    
    for employee in employees:
        if employee["employee_id"] == employee_id:
            return employee
    
    raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

@router.get("/policies", dependencies=[Depends(verify_hr_api_key)])
async def get_hr_policies(
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    category: Optional[str] = Query(None, description="Filter by policy category")
):
    data = load_hr_data()
    policies = data["policies"]
    
    # Apply filters
    filtered_policies = policies
    
    if policy_type:
        filtered_policies = [p for p in filtered_policies if p["policy_type"].lower() == policy_type.lower()]
    
    if category:
        filtered_policies = [p for p in filtered_policies if p["category"].lower() == category.lower()]
    
    if not filtered_policies:
        raise HTTPException(status_code=404, detail="No policies found matching criteria")
    
    # Group by policy type for better organization
    policies_by_type = {}
    for policy in filtered_policies:
        if policy["policy_type"] not in policies_by_type:
            policies_by_type[policy["policy_type"]] = []
        policies_by_type[policy["policy_type"]].append(policy)
    
    return {
        "count": len(filtered_policies),
        "policies_by_type": policies_by_type,
        "all_policies": filtered_policies
    }

@router.get("/payroll", dependencies=[Depends(verify_hr_api_key)])
async def get_payroll_data(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    period: Optional[str] = Query(None, description="Filter by period (YYYY-MM)"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    data = load_hr_data()
    payroll_data = data["payroll"]
    
    # Apply filters
    filtered_payroll = payroll_data
    
    if employee_id:
        filtered_payroll = [p for p in filtered_payroll if p["employee_id"] == employee_id]
    
    if period:
        filtered_payroll = [p for p in filtered_payroll if p["period"] == period]
    
    if department:
        filtered_payroll = [p for p in filtered_payroll if p["department"].lower() == department.lower()]
    
    if not filtered_payroll:
        raise HTTPException(status_code=404, detail="No payroll data found matching criteria")
    
    # Calculate summary statistics
    total_net_pay = sum(p["net_pay"] for p in filtered_payroll)
    total_base_salary = sum(p["base_salary"] for p in filtered_payroll)
    total_bonus = sum(p["bonus"] for p in filtered_payroll)
    
    summary_by_department = {}
    summary_by_period = {}
    
    for entry in filtered_payroll:
        summary_by_department[entry["department"]] = summary_by_department.get(entry["department"], 0) + entry["net_pay"]
        summary_by_period[entry["period"]] = summary_by_period.get(entry["period"], 0) + entry["net_pay"]
    
    return {
        "count": len(filtered_payroll),
        "total_net_pay": total_net_pay,
        "total_base_salary": total_base_salary,
        "total_bonus": total_bonus,
        "summary_by_department": summary_by_department,
        "summary_by_period": summary_by_period,
        "payroll_entries": filtered_payroll
    }

@router.get("/summary", dependencies=[Depends(verify_hr_api_key)])
async def get_hr_summary():
    """Get overall HR summary statistics"""
    data = load_hr_data()
    employees = data["employees"]
    payroll = data["payroll"]
    
    # Employee statistics
    dept_count = {}
    status_count = {}
    location_count = {}
    
    for employee in employees:
        dept_count[employee["department"]] = dept_count.get(employee["department"], 0) + 1
        status_count[employee["status"]] = status_count.get(employee["status"], 0) + 1
        location_count[employee["location"]] = location_count.get(employee["location"], 0) + 1
    
    # Payroll statistics
    total_payroll = sum(p["net_pay"] for p in payroll)
    avg_salary = total_payroll / len(payroll) if payroll else 0
    
    return {
        "total_employees": len(employees),
        "departments_summary": dept_count,
        "employment_status": status_count,
        "locations_summary": location_count,
        "total_payroll_processed": total_payroll,
        "average_salary": round(avg_salary, 2),
        "total_payroll_records": len(payroll)
    }