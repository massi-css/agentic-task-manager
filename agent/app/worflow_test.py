import asyncio
from langchain_core.messages import HumanMessage
from task_manager_agent import task_manager_graph

async def workflow_test():

    message = input("Enter your message: ")
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "tool_logs": []
    }
    config = {"configurable": {"thread_id": "test-thread-001"}}
    final_state = await task_manager_graph.ainvoke(initial_state, config)

    print("Final State:", final_state)
    print("\nResponse:", final_state.get("final_response"))

# Run it
asyncio.run(workflow_test())
