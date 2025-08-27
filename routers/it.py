from fastapi import APIRouter, HTTPException, Depends, Query, Header, Body
from typing import Optional, List, Dict, Any
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, model_validator, field_validator

router = APIRouter()

# API keys for IT endpoints
VALID_IT_API_KEYS = {
    "it_readonly": "it_12345abcde",
    "it_admin": "it_admin_67890xyz",
    "it_support": "it_support_24680mnop"
}

def verify_it_api_key(api_key: str = Header(..., description="API Key for IT endpoints", alias="X-API-Key")):
    if api_key not in VALID_IT_API_KEYS.values():
        raise HTTPException(status_code=401, detail="Invalid IT API key")
    return api_key

# Pydantic models for request bodies
class SupportTicketRequest(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    category: Optional[str] = "general"
    contact_email: Optional[EmailStr] = None
    
    @field_validator('priority')
    def validate_priority(cls, v):
        if v.lower() not in ['low', 'medium', 'high', 'critical']:
            raise ValueError('Priority must be low, medium, high, or critical')
        return v.lower()

class PasswordResetRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @model_validator(mode='after')
    def validate_at_least_one(self):
        if self.username is None and self.email is None:
            raise ValueError('Either username or email must be provided')
        return self

def load_it_data():
    data_file = Path("data/it.json")
    if not data_file.exists():
        # Generate sample IT data
        default_data = {
            "system_status": generate_system_status_data(),
            "support_tickets": [],
            "password_resets": []
        }
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

def save_it_data(data: Dict[str, Any]):
    data_file = Path("data/it.json")
    data_file.write_text(json.dumps(data, indent=2))

def generate_system_status_data():
    services = [
        "Authentication Service", "Database Cluster", "API Gateway", 
        "File Storage", "Email Service", "Monitoring System",
        "Cache Service", "Load Balancer", "CDN", "Message Queue",
        "Web Application", "Mobile API", "Payment Gateway", "Analytics Service"
    ]
    
    status_data = []
    
    for service in services:
        status_options = ["operational", "degraded", "outage", "maintenance"]
        weights = [0.7, 0.15, 0.05, 0.1]  # Weighted probability
        status = random.choices(status_options, weights=weights, k=1)[0]
        
        status_data.append({
            "service_name": service,
            "status": status,
            "response_time": round(random.uniform(50, 500), 2) if status == "operational" else round(random.uniform(800, 2000), 2),
            "uptime": round(random.uniform(99.5, 99.99), 2),
            "last_updated": (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%Y-%m-%d %H:%M:%S"),
            "incidents_last_24h": random.randint(0, 3) if status != "operational" else 0
        })
    
    return status_data

def generate_support_ticket_id():
    return f"TICKET-{random.randint(10000, 99999)}"

def generate_password_reset_token():
    return f"RESET-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}"

@router.get("/status", dependencies=[Depends(verify_it_api_key)])
async def get_system_status(
    service_name: Optional[str] = Query(None, description="Filter by service name")
):
    data = load_it_data()
    system_status = data["system_status"]
    
    # Apply filter if provided
    if service_name:
        filtered_status = [s for s in system_status if service_name.lower() in s["service_name"].lower()]
        if not filtered_status:
            raise HTTPException(status_code=404, detail=f"No service found with name containing '{service_name}'")
        system_status = filtered_status
    
    # Calculate overall status
    operational_services = sum(1 for s in system_status if s["status"] == "operational")
    total_services = len(system_status)
    overall_status = "operational" if operational_services == total_services else "degraded" if operational_services > total_services * 0.7 else "outage"
    
    return {
        "overall_status": overall_status,
        "operational_services": operational_services,
        "total_services": total_services,
        "services": system_status,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@router.get("/status/overview", dependencies=[Depends(verify_it_api_key)])
async def get_system_overview():
    data = load_it_data()
    system_status = data["system_status"]
    
    status_counts = {}
    for service in system_status:
        status_counts[service["status"]] = status_counts.get(service["status"], 0) + 1
    
    avg_response_time = round(sum(s["response_time"] for s in system_status) / len(system_status), 2)
    avg_uptime = round(sum(s["uptime"] for s in system_status) / len(system_status), 2)
    
    return {
        "status_summary": status_counts,
        "average_response_time": avg_response_time,
        "average_uptime": avg_uptime,
        "total_services": len(system_status)
    }

@router.post("/support/ticket", dependencies=[Depends(verify_it_api_key)])
async def create_support_ticket(ticket_request: SupportTicketRequest):
    data = load_it_data()
    
    ticket_id = generate_support_ticket_id()
    new_ticket = {
        "ticket_id": ticket_id,
        "title": ticket_request.title,
        "description": ticket_request.description,
        "priority": ticket_request.priority,
        "category": ticket_request.category,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "contact_email": ticket_request.contact_email,
        "assigned_to": None,
        "resolution": None
    }
    
    data["support_tickets"].append(new_ticket)
    save_it_data(data)
    
    return {
        "message": "Support ticket created successfully",
        "ticket_id": ticket_id,
        "ticket": new_ticket
    }

@router.get("/support/tickets", dependencies=[Depends(verify_it_api_key)])
async def get_support_tickets(
    status: Optional[str] = Query(None, description="Filter by ticket status"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    data = load_it_data()
    tickets = data["support_tickets"]
    
    # Apply filters
    if status:
        tickets = [t for t in tickets if t["status"] == status.lower()]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority.lower()]
    
    # Sort by creation date (newest first)
    tickets.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "count": len(tickets),
        "tickets": tickets
    }

@router.post("/auth/password/reset", dependencies=[Depends(verify_it_api_key)])
async def reset_user_password(reset_request: PasswordResetRequest):
    # In a real system, this would interact with your authentication system
    # For this dummy server, we'll just generate a reset token and log the request
    
    data = load_it_data()
    
    reset_token = generate_password_reset_token()
    reset_record = {
        "request_id": f"REQ-{random.randint(10000, 99999)}",
        "username": reset_request.username,
        "email": reset_request.email,
        "reset_token": reset_token,
        "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "ip_address": f"192.168.1.{random.randint(1, 255)}"
    }
    
    data["password_resets"].append(reset_record)
    save_it_data(data)
    
    # Simulate sending email (in real system, this would actually send an email)
    email_address = reset_request.email or f"{reset_request.username}@company.com"
    
    return {
        "message": "Password reset initiated successfully",
        "reset_token": reset_token,
        "email_sent_to": email_address,
        "expires_at": reset_record["expires_at"],
        "note": "In a real system, an email with reset instructions would be sent"
    }

@router.get("/auth/password/resets", dependencies=[Depends(verify_it_api_key)])
async def get_password_reset_history(
    username: Optional[str] = Query(None, description="Filter by username"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    data = load_it_data()
    resets = data["password_resets"]
    
    # Apply filters
    if username:
        resets = [r for r in resets if r["username"] == username]
    if status:
        resets = [r for r in resets if r["status"] == status.lower()]
    
    # Sort by request date (newest first)
    resets.sort(key=lambda x: x["requested_at"], reverse=True)
    
    return {
        "count": len(resets),
        "password_resets": resets
    }

@router.get("/it/dashboard", dependencies=[Depends(verify_it_api_key)])
async def get_it_dashboard():
    """Comprehensive IT dashboard with all relevant metrics"""
    data = load_it_data()
    
    # System status summary
    system_status = data["system_status"]
    status_counts = {}
    for service in system_status:
        status_counts[service["status"]] = status_counts.get(service["status"], 0) + 1
    
    # Support tickets summary
    tickets = data["support_tickets"]
    ticket_status_counts = {}
    ticket_priority_counts = {}
    
    for ticket in tickets:
        ticket_status_counts[ticket["status"]] = ticket_status_counts.get(ticket["status"], 0) + 1
        ticket_priority_counts[ticket["priority"]] = ticket_priority_counts.get(ticket["priority"], 0) + 1
    
    # Password reset summary
    resets = data["password_resets"]
    recent_resets = [r for r in resets if datetime.strptime(r["requested_at"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(days=7)]
    
    return {
        "system_health": {
            "total_services": len(system_status),
            "status_breakdown": status_counts,
            "operational_rate": round(status_counts.get("operational", 0) / len(system_status) * 100, 1)
        },
        "support_tickets": {
            "total_tickets": len(tickets),
            "open_tickets": ticket_status_counts.get("open", 0),
            "status_breakdown": ticket_status_counts,
            "priority_breakdown": ticket_priority_counts
        },
        "password_resets": {
            "total_requests": len(resets),
            "recent_requests": len(recent_resets),
            "pending_requests": sum(1 for r in resets if r["status"] == "pending")
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }