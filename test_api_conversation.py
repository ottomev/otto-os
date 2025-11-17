#!/usr/bin/env python3
"""
Test script for Otto API conversation flow.
This tests creating a thread and having a conversation with the agent.
"""

import requests
import json
import time
import sys

# API Configuration
API_BASE_URL = "https://api.otto.lk/api"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6IjRWV21mWHVxOTNPcWFTM3giLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2R4enliZ3l1ZmJpbW53eWRiZXJhLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJkNWUwNmUxYy1iMjAxLTQ4YTMtYmUwNS02NmYyMTlmZmNkOWIiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzYzMzE5MTAyLCJpYXQiOjE3NjMzMTU1MDIsImVtYWlsIjoiY20uY29sbGVjdGl2ZS5lc3NlbmNlQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ29vZ2xlIiwicHJvdmlkZXJzIjpbImdvb2dsZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJhdmF0YXJfdXJsIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jS1FqcHVZaWdhb2tHUlloVnpMeEtDVU10alg1b0dITzdFWllVWEJFQjZ4b1JzSktnPXM5Ni1jIiwiZW1haWwiOiJjbS5jb2xsZWN0aXZlLmVzc2VuY2VAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6IkNhbHZpbiBNZW1vcnkiLCJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYW1lIjoiQ2FsdmluIE1lbW9yeSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0tRanB1WWlnYW9rR1JZaFZ6THhLQ1VNdGpYNW9HSE83RVpZVVhCRUI2eG9Sc0pLZz1zOTYtYyIsInByb3ZpZGVyX2lkIjoiMTEzMjAwNjc1NDEwODQwMTc5ODA5Iiwic3ViIjoiMTEzMjAwNjc1NDEwODQwMTc5ODA5In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib2F1dGgiLCJ0aW1lc3RhbXAiOjE3NjMzMTU1MDJ9XSwic2Vzc2lvbl9pZCI6IjRiZGE2MGFmLTRjMWEtNDhlYi04ZTYzLTE4OGE5N2ViYjU4YyIsImlzX2Fub255bW91cyI6ZmFsc2V9.CkAe1ZyObSSGWIXsC6KVbzsauVWgYuN_hbJGFIyzQwU"

def get_headers():
    """Get headers for API requests"""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

def test_health_check():
    """Test that the API is responding"""
    print("\n=== Testing API Health Check ===")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def start_agent_conversation(prompt: str, thread_id: str = None):
    """Start an agent conversation with a prompt"""
    print(f"\n=== Starting Agent Conversation ===")
    print(f"Prompt: {prompt}")
    print(f"Thread ID: {thread_id or 'NEW THREAD'}")

    # Prepare form data
    data = {
        "prompt": prompt
    }

    if thread_id:
        data["thread_id"] = thread_id

    # Make request (multipart/form-data for file upload support)
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    response = requests.post(
        f"{API_BASE_URL}/agent/start",
        headers=headers,
        data=data  # Using data for form-encoded
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Thread ID: {result.get('thread_id')}")
        print(f"Agent Run ID: {result.get('agent_run_id')}")
        print(f"Status: {result.get('status')}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def stream_agent_response(agent_run_id: str, timeout: int = 60):
    """Stream the agent's response for a given agent run"""
    print(f"\n=== Streaming Agent Response ===")
    print(f"Agent Run ID: {agent_run_id}")

    headers = get_headers()

    response = requests.get(
        f"{API_BASE_URL}/agent-run/{agent_run_id}/stream",
        headers=headers,
        stream=True,
        timeout=timeout
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("\n--- Agent Response Stream ---")

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')

                # SSE format: "data: {...}"
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]  # Remove "data: " prefix

                    # Check for stream end
                    if data_str.strip() == "[DONE]":
                        print("\n--- Stream Complete ---")
                        break

                    try:
                        event_data = json.loads(data_str)
                        event_type = event_data.get("type")

                        if event_type == "content":
                            # Print content chunks
                            content = event_data.get("content", "")
                            print(content, end="", flush=True)

                        elif event_type == "tool_call":
                            tool_name = event_data.get("tool_name", "unknown")
                            print(f"\n[TOOL CALL: {tool_name}]", flush=True)

                        elif event_type == "tool_result":
                            print(f"\n[TOOL RESULT]", flush=True)

                        elif event_type == "status":
                            status = event_data.get("status", "")
                            print(f"\n[STATUS: {status}]", flush=True)

                        elif event_type == "error":
                            error_msg = event_data.get("error", "Unknown error")
                            print(f"\n[ERROR: {error_msg}]", flush=True)

                    except json.JSONDecodeError:
                        print(f"[Invalid JSON: {data_str}]")

        print("\n")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def get_agent_run_details(agent_run_id: str):
    """Get details of an agent run"""
    print(f"\n=== Getting Agent Run Details ===")
    print(f"Agent Run ID: {agent_run_id}")

    headers = get_headers()

    response = requests.get(
        f"{API_BASE_URL}/agent-run/{agent_run_id}",
        headers=headers
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        run_data = response.json()
        print(f"Status: {run_data.get('status')}")
        print(f"Error: {run_data.get('error')}")
        print(f"Model: {run_data.get('model')}")
        print(f"Created: {run_data.get('created_at')}")

        return run_data
    else:
        print(f"Error: {response.text}")
        return None

def get_thread_messages(thread_id: str):
    """Get all messages from a thread"""
    print(f"\n=== Getting Thread Messages ===")
    print(f"Thread ID: {thread_id}")

    headers = get_headers()

    response = requests.get(
        f"{API_BASE_URL}/threads/{thread_id}/messages",
        headers=headers
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        messages_data = response.json()

        # Check if it's a dict with a messages key or a list
        if isinstance(messages_data, dict):
            messages = messages_data.get("messages", messages_data.get("data", []))
        else:
            messages = messages_data

        print(f"Total Messages: {len(messages)}")

        for msg in messages[:5]:  # Show first 5 messages
            msg_type = msg.get("type")
            content = msg.get("content", {})
            print(f"\n  Type: {msg_type}")

            if isinstance(content, dict):
                role = content.get("role", "")
                text = content.get("content", "")
                if isinstance(text, str):
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"  Role: {role}")
                    print(f"  Content: {preview}")

        return messages
    else:
        print(f"Error: {response.text}")
        return None

def main():
    """Main test flow"""
    print("=" * 60)
    print("Otto API Conversation Test")
    print("=" * 60)

    # Step 1: Health check
    if not test_health_check():
        print("❌ Health check failed. Exiting.")
        sys.exit(1)
    print("✅ Health check passed")

    # Step 2: Start a conversation with a simple prompt
    test_prompt = "Hello! Can you tell me a short joke about programming?"

    result = start_agent_conversation(test_prompt)

    if not result:
        print("❌ Failed to start agent conversation. Exiting.")
        sys.exit(1)

    thread_id = result.get("thread_id")
    agent_run_id = result.get("agent_run_id")

    print("✅ Agent conversation started")

    # Step 3: Stream the agent's response
    # Wait a moment for the agent to start processing
    time.sleep(2)

    if stream_agent_response(agent_run_id):
        print("✅ Successfully streamed agent response")
    else:
        print("❌ Failed to stream agent response")

    # Step 3.5: Get agent run details to see if there was an error
    get_agent_run_details(agent_run_id)

    # Step 4: Retrieve thread messages
    messages = get_thread_messages(thread_id)
    if messages:
        print("✅ Successfully retrieved thread messages")

    # Step 5: Test follow-up message on same thread
    print("\n" + "=" * 60)
    print("Testing Follow-up Message")
    print("=" * 60)

    followup_prompt = "Can you make that joke even shorter?"
    result2 = start_agent_conversation(followup_prompt, thread_id=thread_id)

    if result2:
        agent_run_id_2 = result2.get("agent_run_id")
        time.sleep(2)

        if stream_agent_response(agent_run_id_2):
            print("✅ Successfully streamed follow-up response")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
