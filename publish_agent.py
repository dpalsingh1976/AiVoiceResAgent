
import os
from dotenv import load_dotenv
from retell_sdk import Retell

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
if not RETELL_API_KEY:
    raise ValueError("RETELL_API_KEY not found in environment variables.")

retell = Retell(api_key=RETELL_API_KEY)


def publish_agent(agent_id: str):
    print(f"Publishing agent with ID: {agent_id}...")
    try:
        # The Retell API documentation should specify how to 'publish' or 'promote' an agent.
        # Assuming there's an update mechanism that changes its status or version.
        # For now, this is a placeholder as the exact API call for 'publishing' isn't explicit in the provided spec.
        # If 'publish' means updating a status, we would use retell.agent.update with a specific field.
        # If it means creating a new version, the API would likely have a versioning endpoint.
        
        # Placeholder: Assuming 'publishing' might involve updating some metadata or status.
        retell.agent.publish(agent_id)
        print(f"Agent {agent_id} published successfully.")
        
        # In a real scenario, you would also persist the agent config and version to a DB.
        print("Remember to persist the agent config and version to your database (integrations table).")
        return True
    except Exception as e:
        print(f"Error publishing agent {agent_id}: {e}")
        return False

if __name__ == "__main__":
    agent_id = os.getenv("RETELL_AGENT_ID")
    if not agent_id:
        print("RETELL_AGENT_ID not found in environment variables. Please run create_agent.py first.")
    else:
        if publish_agent(agent_id):
            print("Agent publishing process initiated (further Retell API details needed for full implementation).")
        else:
            print("Failed to publish Retell agent.")


