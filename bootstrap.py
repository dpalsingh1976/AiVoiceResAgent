
import os
from dotenv import load_dotenv, find_dotenv, set_key
from create_agent import create_or_update_agent
from publish_agent import publish_agent
from provision_number import provision_number

def bootstrap_retell_setup():
    print("Starting Retell API bootstrap process...")

    # Ensure .env.local exists for writing
    if not os.path.exists(".env.local"):
        open(".env.local", "a").close()

    # Load environment variables from .env.local
    load_dotenv(dotenv_path=".env.local")

    # 1. Create or Update Agent
    agent_id = create_or_update_agent()
    if not agent_id:
        print("Failed to create or update agent. Exiting bootstrap.")
        return
    
    # Update .env.local with the new agent_id if it was created
    set_key(find_dotenv(usecwd=True), "RETELL_AGENT_ID", agent_id)
    load_dotenv(dotenv_path=".env.local", override=True) # Reload to ensure new agent_id is available

    # 2. Publish Agent (placeholder for now)
    if not publish_agent(agent_id):
        print("Failed to publish agent. Exiting bootstrap.")
        return

    # 3. Provision Phone Number
    # You might want to pass area_code or other parameters here dynamically
    provisioned_number = provision_number(agent_id)
    if not provisioned_number:
        print("Failed to provision phone number. Exiting bootstrap.")
        return
    
    # Update .env.local with the new phone number
    set_key(find_dotenv(usecwd=True), "RETELL_PHONE_NUMBER", provisioned_number)
    load_dotenv(dotenv_path=".env.local", override=True) # Reload

    print("Retell API bootstrap process completed successfully!")
    print(f"Agent ID: {os.getenv("RETELL_AGENT_ID")}")
    print(f"Phone Number: {os.getenv("RETELL_PHONE_NUMBER")}")

if __name__ == "__main__":
    bootstrap_retell_setup()


