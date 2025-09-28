
import os
import json
from retell_sdk import Retell
from retell_sdk.models import CreateAgentRequest, UpdateAgentRequest
load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
if not RETELL_API_KEY:
    raise ValueError("RETELL_API_KEY not found in environment variables.")

retell = Retell(api_key=RETELL_API_KEY)


# System Prompt and Tools from the specification
SYSTEM_PROMPT = """
You are the friendly maître d’ for {{RestaurantName}}. Greet callers, announce today’s special if present, then ask: ‘Would you like a reservation, a takeout order, or have a question about events?’
Rules:

Confirm items, sizes, quantities; never guess allergens.

Announce 86’d items immediately and offer alternatives.

For reservations, collect date/time/party size/name/phone; read back to confirm.

For event planning, capture date, party size, type (birthday/corporate), budget, contact; create a reminder to Chef to call within 24 hours.

Payments are via SMS/email link only—never collect card by phone.

If caller is stuck or requests staff, escalate with handover.
"""

TOOL_SCHEMA = [
  {"name":"get_menu","description":"List menu items","parameters":{"type":"object","properties":{"tags":{"type":"array","items":{"type":"string"}}}}},
  {"name":"check_item_availability","parameters":{"type":"object","properties":{"item_id":{"type":"string"},"qty":{"type":"number"}},"required":["item_id","qty"]}},
  {"name":"create_order","parameters":{"type":"object","properties":{"items":{"type":"array","items":{"type":"object","properties":{"item_id":{"type":"string"},"qty":{"type":"integer"},"notes":{"type":"string"}},"required":["item_id","qty"]}},"customer":{"type":"object","properties":{"name":{"type":"string"},"phone":{"type":"string"},"email":{"type":"string"}},"required":["name","phone"]}},"required":["items","customer"]}},
  {"name":"get_timeslots","parameters":{"type":"object","properties":{"date":{"type":"string","format":"date"},"party_size":{"type":"integer"}},"required":["date","party_size"]}},
  {"name":"create_reservation","parameters":{"type":"object","properties":{"datetime":{"type":"string","format":"date-time"},"party_size":{"type":"integer"},"name":{"type":"string"},"phone":{"type":"string"}},"required":["datetime","party_size","name","phone"]}},
  {"name":"create_reminder","parameters":{"type":"object","properties":{"assignee":{"type":"string","enum":["chef"]},"due_at":{"type":"string","format":"date-time"},"payload":{"type":"object"}},"required":["assignee","due_at","payload"]}},
  {"name":"handover_human","parameters":{"type":"object","properties":{"reason":{"type":"string"}},"required":["reason"]}}
]

def create_or_update_agent():
    agent_id = os.getenv("RETELL_AGENT_ID")

    # Common agent parameters
    agent_params = {
        "llm_websocket_url": "wss://your-backend-url/api/voice/retell/llm-websocket", # Placeholder
        "voice_id": "11labs-Adrian", # Example from docs
        "agent_name": "VoiceFlow AI Restaurant Agent",
        "voice_speed": 1.0,
        "voice_temperature": 1.0,
        "enable_backchannel": True,
        "reminder_prompt": "Just a reminder, I\'m here to help with reservations, takeout orders, or any questions you have about our events. What can I do for you?",
        "system_prompt": SYSTEM_PROMPT,
        "tools": TOOL_SCHEMA,
    }

    if agent_id:
        print(f"Updating existing agent with ID: {agent_id}")
        try:
            updated_agent = retell.agent.update(agent_id, **agent_params)
            print(f"Agent updated successfully: {updated_agent.agent_name} (ID: {updated_agent.agent_id})")
            return updated_agent.agent_id
        except Exception as e:
            print(f"Error updating agent: {e}")
            print("Attempting to create a new agent instead.")
            agent_id = None # Fallback to creation if update fails

    if not agent_id:
        print("Creating new agent...")
        try:
            new_agent = retell.agent.create(**agent_params)
            print(f"Agent created successfully: {new_agent.agent_name} (ID: {new_agent.agent_id})")
            
            # Output RETELL_AGENT_ID to .env.local
            with open(".env.local", "a") as f:
                f.write(f"\nRETELL_AGENT_ID={new_agent.agent_id}\n")
            print(f"RETELL_AGENT_ID={new_agent.agent_id} written to .env.local")
            
            # In a real scenario, you would also store this in a secrets store.
            print("Remember to store RETELL_AGENT_ID in your secrets store.")
            return new_agent.agent_id
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

if __name__ == "__main__":
    agent_id = create_or_update_agent()
    if agent_id:
        print(f"Operation completed for agent ID: {agent_id}")
    else:
        print("Failed to create or update Retell agent.")



