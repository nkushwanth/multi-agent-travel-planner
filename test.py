# from tools.tavily_tool import tavily_search
# from tools.flight_tool import search_flights
# from backend import run_travel_agent
# # results = search_flights("plan a 7 day trip from New York to London")
# # print(results)

# # results = tavily_search("Best places to visit in Europe")
# # print(results)
# user_input = input("Enter travel request: ")

# response = run_travel_agent(
#     user_input=user_input,
#     thread_id="test_user"
# )

# print("\nFINAL RESPONSE:\n")
# print(response["answer"])



import asyncio
# from mcp_client_test import get_all_tools, tavily_mcp_search
from mcp_client import get_all_tools



if __name__ == "__main__":
    asyncio.run(get_all_tools())


import subprocess
import sys
import os
import traceback


# AVIATION_STACK_API_KEY = os.environ.get("AVIATION_STACK_API_KEY")

# # Test the aviationstack server directly
# def test_aviationstack_direct():
#     env = os.environ.copy()
#     env["AVIATION_STACK_API_KEY"] = AVIATION_STACK_API_KEY or ""
#     env["AVIATIONSTACK_API_KEY"] = AVIATION_STACK_API_KEY or ""
    
#     try:
#         result = subprocess.run(
#             ["uvx", "aviationstack-mcp"],
#             env=env,
#             capture_output=True,
#             text=True,
#             timeout=5
#         )
#         print(f"STDOUT: {result.stdout}")
#         print(f"STDERR: {result.stderr}")
#         print(f"Return code: {result.returncode}")
#     except subprocess.TimeoutExpired:
#         print("Server started successfully (timeout expected)")
#     except Exception as e:
#         print(f"Error: {e}")
#         traceback.print_exc()

# # Call this to test
# test_aviationstack_direct()



# Test your aviationstack connection
# async def test_aviation():
#     try:
#         # Try to get available tools
#         tools = await client.get_tools(server_name="aviationstack")
#         print(f"✓ AviationStack available! Tools: {[t.name for t in tools]}")
        
#         # Try a real request
#         flights = await aviation_mcp_call(
#             "search_flights",  # or whatever the tool is called
#             {"limit": 5}
#         )
#         print(f"✓ Flight data: {flights}")
        
#     except Exception as e:
#         print(f"✗ Error: {e}")
#         traceback.print_exc()

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_aviation())