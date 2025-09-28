
import os
from dotenv import load_dotenv
from retell_sdk import Retell
from retell_sdk.models import CreatePhoneNumberRequest

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
if not RETELL_API_KEY:
    raise ValueError("RETELL_API_KEY not found in environment variables.")

retell = Retell(api_key=RETELL_API_KEY)


def provision_number(agent_id: str, area_code: str = "", country_code: str = "US"):
    print(f"Provisioning phone number for agent ID: {agent_id}...")
    try:
        # First, check if a number is already provisioned for this agent or in .env.local
        phone_number = os.getenv("RETELL_PHONE_NUMBER")
        if phone_number:
            print(f"Using existing phone number from .env.local: {phone_number}")
            # In a real scenario, you might want to verify this number is still active and linked to the agent
            return phone_number

        # Search for available numbers
        # The Retell API might have a search endpoint for available numbers.
        # For this example, we'll assume a direct creation or assignment.
        
        # Create a new phone number and assign it to the agent
        # This part needs to be adapted based on the actual Retell API for phone number provisioning.
        # Assuming a simple create request for a new number and linking it to an agent.
        create_number_request = CreatePhoneNumberRequest(
            agent_id=agent_id,
            # Additional parameters like area_code, country_code would go here
            # For example: area_code=area_code, country_code=country_code
            # Inbound webhook URL would be set here or via an update call
            # The spec mentions: Set inbound webhook to POST /api/voice/retell/webhook (signed).
            # This would typically be part of the phone number configuration.
            # For now, we'll use a placeholder.
            # webhook_url="https://your-backend-url/api/voice/retell/webhook"
        )
        
        # The spec mentions: Set inbound webhook to POST /api/voice/retell/webhook (signed).
        # This would typically be part of the phone number configuration.
        # We'll use a placeholder URL for now, assuming it will be updated later.
        create_number_request.webhook_url = "https://your-backend-url/api/voice/retell/webhook"
        
        new_phone_number = retell.phone_number.create(create_number_request)
        provisioned_number = new_phone_number.phone_number

        print(f"Phone number {provisioned_number} provisioned and assigned to agent {agent_id}.")

        # Output RETELL_PHONE_NUMBER to .env.local
        with open(".env.local", "a") as f:
            f.write(f"\nRETELL_PHONE_NUMBER={provisioned_number}\n")
        print(f"RETELL_PHONE_NUMBER={provisioned_number} written to .env.local")
        
        # In a real scenario, you would also store this in a secrets store.
        print("Remember to store RETELL_PHONE_NUMBER in your secrets store.")

        # Support multi-location routing rules by Caller ID, time of day, and language preference
        # This logic would typically reside in your backend webhook handler, not in the provisioning script.
        print("Multi-location routing rules need to be implemented in the backend webhook handler.")

        return provisioned_number
    except Exception as e:
        print(f"Error provisioning phone number: {e}")
        return None

if __name__ == "__main__":
    agent_id = os.getenv("RETELL_AGENT_ID")
    if not agent_id:
        print("RETELL_AGENT_ID not found in environment variables. Please run create_agent.py first.")
    else:
        # Example: provision a number with a specific area code
        # You might want to get area_code from user input or config
        provisioned_num = provision_number(agent_id, area_code="555")
        if provisioned_num:
            print(f"Operation completed for phone number: {provisioned_num}")
        else:
            print("Failed to provision Retell phone number.")


