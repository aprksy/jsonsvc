from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import Optional, List
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import secrets

router = APIRouter()

# Simple API key storage (in production, use proper authentication)
VALID_API_KEYS = {
    "financial_readonly": "fin_12345abcde",
    "financial_admin": "fin_admin_67890xyz"
}

def verify_api_key(api_key: str = Header(..., description="API Key for financial endpoints")):
    if api_key not in VALID_API_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

def load_financial_data():
    data_file = Path("data/financial.json")
    if not data_file.exists():
        # Generate sample financial data
        default_data = {
            "budgets": generate_budget_data(),
            "expenses": generate_expense_data(),
            "revenues": generate_revenue_data()
        }
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

def generate_budget_data():
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    projects = ["Project Alpha", "Project Beta", "Project Gamma", "Project Delta"]
    fiscal_years = [2023, 2024, 2025]
    
    budgets = []
    budget_id = 1
    
    for year in fiscal_years:
        for dept in departments:
            for project in projects:
                budgets.append({
                    "id": budget_id,
                    "department": dept,
                    "project_id": f"PROJ-{budget_id % 1000:03d}",
                    "project_name": project,
                    "fiscal_year": year,
                    "allocated_budget": random.randint(50000, 500000),
                    "remaining_budget": random.randint(10000, 100000),
                    "spent_to_date": random.randint(10000, 400000),
                    "status": random.choice(["On Track", "Over Budget", "Under Budget"])
                })
                budget_id += 1
    
    return budgets

def generate_expense_data():
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    categories = ["Salaries", "Equipment", "Travel", "Software", "Office Supplies", "Marketing"]
    
    expenses = []
    expense_id = 1
    start_date = datetime(2023, 1, 1)
    
    for i in range(1000):
        dept = random.choice(departments)
        date = start_date + timedelta(days=random.randint(0, 730))
        
        expenses.append({
            "id": expense_id,
            "department": dept,
            "category": random.choice(categories),
            "amount": round(random.uniform(100, 10000), 2),
            "date": date.strftime("%Y-%m-%d"),
            "description": f"{dept} {random.choice(categories)} expense",
            "vendor": f"Vendor {random.randint(1, 50)}",
            "status": random.choice(["Approved", "Pending", "Rejected"])
        })
        expense_id += 1
    
    return expenses

def generate_revenue_data():
    departments = ["Sales", "Marketing", "Partnerships", "Services"]
    products = ["Product A", "Product B", "Product C", "Service X", "Service Y"]
    periods = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025"]
    
    revenues = []
    revenue_id = 1
    
    for period in periods:
        for dept in departments:
            for product in products:
                revenues.append({
                    "id": revenue_id,
                    "department": dept,
                    "product": product,
                    "period": period,
                    "revenue_amount": round(random.uniform(5000, 100000), 2),
                    "units_sold": random.randint(10, 500),
                    "growth_rate": round(random.uniform(-10, 30), 1),
                    "project_id": f"REV-{revenue_id % 1000:03d}" if random.random() > 0.3 else None
                })
                revenue_id += 1
    
    return revenues

@router.get("/budgets", dependencies=[Depends(verify_api_key)])
async def get_budget_info(
    department: Optional[str] = Query(None, description="Filter by department"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year")
):
    data = load_financial_data()
    budgets = data["budgets"]
    
    # Apply filters
    filtered_budgets = budgets
    if department:
        filtered_budgets = [b for b in filtered_budgets if b["department"].lower() == department.lower()]
    if project_id:
        filtered_budgets = [b for b in filtered_budgets if b["project_id"] == project_id]
    if fiscal_year:
        filtered_budgets = [b for b in filtered_budgets if b["fiscal_year"] == fiscal_year]
    
    if not filtered_budgets:
        raise HTTPException(status_code=404, detail="No budget data found matching criteria")
    
    return {
        "count": len(filtered_budgets),
        "results": filtered_budgets
    }

@router.get("/expenses", dependencies=[Depends(verify_api_key)])
async def get_expense_reports(
    department: Optional[str] = Query(None, description="Filter by department"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    data = load_financial_data()
    expenses = data["expenses"]
    
    # Apply filters
    filtered_expenses = expenses
    if department:
        filtered_expenses = [e for e in filtered_expenses if e["department"].lower() == department.lower()]
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d") >= date_from_obj]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d") <= date_to_obj]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
    
    # Calculate summary statistics
    total_amount = sum(e["amount"] for e in filtered_expenses)
    by_category = {}
    by_department = {}
    
    for expense in filtered_expenses:
        by_category[expense["category"]] = by_category.get(expense["category"], 0) + expense["amount"]
        by_department[expense["department"]] = by_department.get(expense["department"], 0) + expense["amount"]
    
    return {
        "count": len(filtered_expenses),
        "total_amount": total_amount,
        "summary_by_category": by_category,
        "summary_by_department": by_department,
        "expenses": filtered_expenses
    }

@router.get("/revenues", dependencies=[Depends(verify_api_key)])
async def get_revenue_data(
    department: Optional[str] = Query(None, description="Filter by department"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    period: Optional[str] = Query(None, description="Filter by period (e.g., Q1 2024)")
):
    data = load_financial_data()
    revenues = data["revenues"]
    
    # Apply filters
    filtered_revenues = revenues
    if department:
        filtered_revenues = [r for r in filtered_revenues if r["department"].lower() == department.lower()]
    if project_id:
        filtered_revenues = [r for r in filtered_revenues if r.get("project_id") == project_id]
    if period:
        filtered_revenues = [r for r in filtered_revenues if r["period"].lower() == period.lower()]
    
    if not filtered_revenues:
        raise HTTPException(status_code=404, detail="No revenue data found matching criteria")
    
    # Calculate summary
    total_revenue = sum(r["revenue_amount"] for r in filtered_revenues)
    by_period = {}
    by_department = {}
    
    for revenue in filtered_revenues:
        by_period[revenue["period"]] = by_period.get(revenue["period"], 0) + revenue["revenue_amount"]
        by_department[revenue["department"]] = by_department.get(revenue["department"], 0) + revenue["revenue_amount"]
    
    return {
        "count": len(filtered_revenues),
        "total_revenue": total_revenue,
        "summary_by_period": by_period,
        "summary_by_department": by_department,
        "revenues": filtered_revenues
    }

@router.get("/summary", dependencies=[Depends(verify_api_key)])
async def get_financial_summary():
    """Get overall financial summary"""
    data = load_financial_data()
    
    total_budget = sum(b["allocated_budget"] for b in data["budgets"])
    total_expenses = sum(e["amount"] for e in data["expenses"])
    total_revenue = sum(r["revenue_amount"] for r in data["revenues"])
    
    return {
        "total_budget": total_budget,
        "total_expenses": total_expenses,
        "total_revenue": total_revenue,
        "net_income": total_revenue - total_expenses,
        "budget_utilization": (total_expenses / total_budget * 100) if total_budget > 0 else 0
    }