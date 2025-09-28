
from fastapi import FastAPI, Request, HTTPException
from .database import fetch_all, execute_query
from dotenv import load_dotenv
import os
import hmac
import hashlib
import json
from .models import (
    GetMenuPayload,
    CheckItemAvailabilityPayload,
    CreateOrderPayload,
    GetTimeslotsPayload,
    CreateReservationPayload,
    CreateReminderPayload,
    HandoverHumanPayload
)


load_dotenv()

app = FastAPI()

RETELL_WEBHOOK_SECRET = os.getenv("RETELL_WEBHOOK_SECRET")

@app.get("/")
async def read_root():
    return {"message": "VoiceFlow AI Backend API"}

@app.post("/api/voice/retell/webhook")
async def retell_webhook(request: Request):
    if not RETELL_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="RETELL_WEBHOOK_SECRET not configured.")

    # Verify Retell signature
    signature = request.headers.get("X-Retell-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="X-Retell-Signature header missing.")

    body = await request.body()
    expected_signature = hmac.new(
        RETELL_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid Retell webhook signature.")

    event = json.loads(body.decode("utf-8"))
    event_type = event.get("event_name")

    print(f"Received Retell webhook event: {event_type}")
    # Handle events: call.started, transcript.delta, tool.invocation, call.ended, handover.requested, error.
    # Upsert calls row; append transcript segments (store raw + normalized).
    # Rate-limit, queue heavy work, and retry idempotently.
    # Mask PII in logs; keep audio/transcripts 30 days (configurable).

    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    if event_type == "call.started":
        call_id = event.get("call_id")
        agent_id = event.get("agent_id")
        start_time = event.get("start_timestamp")
        await execute_query(
            "INSERT INTO call_logs (retell_call_id, restaurant_id, agent_id, start_time, status, raw_event_data) VALUES ($1, $2, $3, to_timestamp($4 / 1000.0), $5, $6)",
            call_id, RESTAURANT_ID, agent_id, start_time, "started", json.dumps(event)
        )
        print(f"Call started: {call_id}")
    elif event_type == "transcript.delta":
        call_id = event.get("call_id")
        transcript_segment = event.get("transcript")
        await execute_query(
            "UPDATE call_logs SET transcript = COALESCE(transcript, '') || $1, updated_at = CURRENT_TIMESTAMP WHERE retell_call_id = $2",
            transcript_segment, call_id
        )
        print(f"Transcript delta for call {call_id}: {transcript_segment}")
    elif event_type == "call.ended":
        call_id = event.get("call_id")
        end_time = event.get("end_timestamp")
        status = event.get("call_status")
        transcript = event.get("transcript")
        await execute_query(
            "UPDATE call_logs SET end_time = to_timestamp($1 / 1000.0), status = $2, transcript = $3, raw_event_data = $4, updated_at = CURRENT_TIMESTAMP WHERE retell_call_id = $5",
            end_time, status, transcript, json.dumps(event), call_id
        )
        print(f"Call ended: {call_id} with status {status}")
    elif event_type == "handover.requested":
        call_id = event.get("call_id")
        reason = event.get("reason")
        # Log handover request in call_logs or a separate table
        print(f"Handover requested for call {call_id} with reason: {reason}")
    elif event_type == "error":
        call_id = event.get("call_id")
        error_message = event.get("error_message")
        await execute_query(
            "UPDATE call_logs SET status = 'error', raw_event_data = $1, updated_at = CURRENT_TIMESTAMP WHERE retell_call_id = $2",
            json.dumps(event), call_id
        )
        print(f"Error in call {call_id}: {error_message}")
    else:
        print(f"Unhandled event type: {event_type}")


    return {"status": "success", "event_received": event_type}

@app.post("/api/voice/retell/action")
async def retell_action(request: Request):
    # This endpoint will handle tool invocations from Retell.
    # It will route by tool.name to appropriate functions.

    body = await request.json()
    tool_name = body.get("tool_name")
    parameters = body.get("parameters", {})

    if tool_name == "get_menu":
        payload = GetMenuPayload(**parameters)
        return await get_menu(payload)
    elif tool_name == "check_item_availability":
        payload = CheckItemAvailabilityPayload(**parameters)
        return await check_item_availability(payload)
    elif tool_name == "create_order":
        payload = CreateOrderPayload(**parameters)
        return await create_order(payload)
    elif tool_name == "get_timeslots":
        payload = GetTimeslotsPayload(**parameters)
        return await get_timeslots(payload)
    elif tool_name == "create_reservation":
        payload = CreateReservationPayload(**parameters)
        return await create_reservation(payload)
    elif tool_name == "create_reminder":
        payload = CreateReminderPayload(**parameters)
        return await create_reminder(payload)
    elif tool_name == "handover_human":
        payload = HandoverHumanPayload(**parameters)
        return await handover_human(payload)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

# Placeholder functions for each tool
async def get_menu(payload: GetMenuPayload):
    print(f"Executing get_menu with tags: {payload.tags}")
    # For multi-tenancy, you would get the restaurant_id from the request context
    # For now, we'll use a placeholder or environment variable
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1) # Default to 1 for now

    query = "SELECT id, name, description, price, category, tags, is_available, is_86d FROM menu_items WHERE restaurant_id = $1"
    params = [RESTAURANT_ID]

    if payload.tags:
        query += " AND $2::text[] <@ tags"
        params.append(payload.tags)

    menu_items = await fetch_all(query, *params)
    
    # Convert asyncpg.Record objects to dictionaries for JSON serialization
    formatted_menu = []
    for item in menu_items:
        formatted_menu.append({
            "id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "price": float(item["price"]),
            "category": item["category"],
            "tags": item["tags"],
            "is_available": item["is_available"],
            "is_86d": item["is_86d"],
        })

    return {"status": "success", "data": formatted_menu}

async def check_item_availability(payload: CheckItemAvailabilityPayload):
    print(f"Executing check_item_availability for {payload.qty} of {payload.item_id}")
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    query = "SELECT is_available, is_86d FROM menu_items WHERE id = $1 AND restaurant_id = $2"
    item = await fetch_one(query, payload.item_id, RESTAURANT_ID)

    if item:
        available = item["is_available"] and not item["is_86d"]
        return {"status": "success", "available": available}
    else:
        return {"status": "success", "available": False, "message": "Item not found."}


async def create_order(payload: CreateOrderPayload):
    print(f"Executing create_order for customer {payload.customer.name}")
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    # Calculate total amount (placeholder for now, should fetch actual prices from DB)
    total_amount = 0.0
    for item in payload.items:
        # In a real scenario, fetch item price from menu_items table
        # For now, assume a dummy price or pass it in payload if available
        total_amount += 10.0 * item.qty # Dummy price

    # Create order
    order_query = "INSERT INTO orders (restaurant_id, customer_name, customer_phone, customer_email, status, total_amount, pay_link) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id"
    pay_link = f"https://stripe.com/pay/{os.urandom(16).hex()}" # Placeholder Stripe link
    order_id = await fetch_one(order_query, RESTAURANT_ID, payload.customer.name, payload.customer.phone, payload.customer.email, "pending", total_amount, pay_link)
    order_id = order_id["id"]

    # Add order items
    for item in payload.items:
        # In a real scenario, fetch menu_item_id and price_at_order from menu_items table
        item_query = "INSERT INTO order_items (order_id, menu_item_id, quantity, notes, price_at_order) VALUES ($1, $2, $3, $4, $5)"
        await execute_query(item_query, order_id, item.item_id, item.qty, item.notes, 10.0) # Dummy price

    return {"status": "success", "order_id": str(order_id), "pay_link": pay_link}

async def get_timeslots(payload: GetTimeslotsPayload):
    print(f"Executing get_timeslots for {payload.party_size} on {payload.date}")
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    # This is a simplified placeholder. Real implementation would involve:
    # 1. Checking restaurant operating hours for the given date.
    # 2. Checking existing reservations to find available slots.
    # 3. Considering party size and table availability.
    
    # For now, return some dummy available timeslots
    available_times = ["18:00", "19:00", "20:00"]
    return {"status": "success", "data": available_times}

async def create_reservation(payload: CreateReservationPayload):
    print(f"Executing create_reservation for {payload.name} on {payload.datetime}")
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    query = "INSERT INTO reservations (restaurant_id, customer_name, customer_phone, datetime, party_size, status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id"
    reservation_id = await fetch_one(query, RESTAURANT_ID, payload.name, payload.phone, payload.datetime, payload.party_size, "pending")
    reservation_id = reservation_id["id"]

    return {"status": "success", "reservation_id": str(reservation_id)}

async def create_reminder(payload: CreateReminderPayload):
    print(f"Executing create_reminder for {payload.assignee} due at {payload.due_at}")
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)

    query = "INSERT INTO reminders (restaurant_id, assignee, due_at, payload, is_completed) VALUES ($1, $2, $3, $4, FALSE) RETURNING id"
    reminder_id = await fetch_one(query, RESTAURANT_ID, payload.assignee, payload.due_at, payload.payload)
    reminder_id = reminder_id["id"]

    return {"status": "success", "reminder_id": str(reminder_id)}

async def handover_human(payload: HandoverHumanPayload):
    print(f"Executing handover_human due to: {payload.reason}")
    # In a real scenario, this would trigger an alert to staff, log the event,
    # and potentially update the call status in the database.
    # For now, we'll just log it and return success.
    RESTAURANT_ID = os.getenv("RESTAURANT_ID", 1)
    # Assuming a call_id would be available in the context for logging purposes
    # For simplicity, we'll just log the reason here.
    print(f"Handover requested for restaurant {RESTAURANT_ID} with reason: {payload.reason}")
    return {"status": "success", "message": "Handover request logged."}"}



