from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
import logging, os
from app.utils.system_prompt import system_prompt
from app.utils.load_model import load_model
from dotenv import load_dotenv

from app.utils.tool_calling.get_exchange_rates import get_exchange_rates        
from app.utils.tool_calling.get_weather import get_weather
from app.utils.tool_calling.web_search_summary import make_search_tool
from app.utils.tool_calling.current_datetime import get_current_datetime
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.runnables import RunnableConfig

load_dotenv()

conn = os.environ.get("POSTGRESQL_URL", "")
if not conn:
    raise ValueError("POSTGRESQL_URL environment variable is not set.")

model = load_model()
search_tool = make_search_tool()

tools = [get_weather, get_exchange_rates, search_tool, get_current_datetime]

# We'll initialize the checkpointer inside the async generator or as a global async object
# For simplicity with FastAPI lifespan or local usage, we can create it here but it needs an async loop to setup
async def get_app():
    checkpointer = AsyncPostgresSaver.from_conn_string(conn)
    # Note: version 0.2+ of langgraph-checkpoint-postgres uses aio
    # We'll use a simplified approach for the app compilation
    return create_react_agent(model, tools, checkpointer=checkpointer)

# We are now using sqlite to remember the context and hence for the agent to remember us by our
# user id
# from langgraph.checkpoint.sqlite import SqliteSaver


async def stream_model_output_new(prompt: str, thread_id=1):
    """
    Yields structured dictionary objects for the frontend asynchronously.
    """
    import time
    start_time = time.time()
    logging.warning(f"🚀 Starting request for prompt: '{prompt[:50]}...'")
    
    config: RunnableConfig = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"user_id": thread_id},
    }
    
    async with AsyncPostgresSaver.from_conn_string(conn) as checkpointer:
        checkpoint_time = time.time()
        # logging.warning(f"⏱️  Checkpointer created: {checkpoint_time - start_time:.2f}s")
        
        await checkpointer.setup()
        setup_time = time.time()
        # logging.warning(f"⏱️  Checkpointer setup: {setup_time - checkpoint_time:.2f}s")
        
        app = create_react_agent(model, tools, checkpointer=checkpointer)
        agent_time = time.time()
        # logging.warning(f"⏱️  Agent created: {agent_time - setup_time:.2f}s")
        
        prev_state = await app.aget_state(config=config)
        prev_state_message = (
            prev_state.values["messages"]
            if prev_state and prev_state.values and "messages" in prev_state.values
            else []
        )

        if not prev_state or not prev_state_message:
            state = {
                "messages": [
                    SystemMessage(content=system_prompt()),
                    HumanMessage(content=prompt),
                ]
            }
        else:
            prev_state.values["messages"].append(HumanMessage(content=prompt))
            state = prev_state.values

        state_time = time.time()
        
        # Start of AI Processing Block
        print("\n" + "#" * 50)
        logging.warning(f"🧠  AI AGENT ACTIVATED | THREAD ID: {thread_id}")
        yield {"type": "signal", "status": "thinking", "message": f"Agent activated in {state_time - start_time:.2f}. ⏳ 処理が遅いマシンを使っているので、少し待ってください。 :-)"}
        logging.warning(f"⏱️  PREPARATION TIME: {state_time - start_time:.2f}s")
        print("#" * 50)
        
        iteration_count = 0
        agent_calls = 0
        tool_calls = 0
        
        # Use stream_mode=["messages", "updates"] to catch both content and graph transitions
        async for stream_type, chunk in app.astream(
            state,
            config=config,
            stream_mode=["messages", "updates"],
        ):
            iteration_count += 1
            
            if stream_type == "messages":
                msg, metadata = chunk
                if isinstance(msg, AIMessageChunk) and msg.content:
                    if iteration_count == 1:
                        first_chunk_time = time.time()
                        logging.warning(f"⚡  FIRST CHUNK GENERATED: {first_chunk_time - start_time:.2f}s")
                    yield {"type": "chunk", "data": msg.content}
            
            elif stream_type == "updates":
                if "agent" in chunk:
                    agent_calls += 1
                    print("\n" + "   " + "-" * 30)
                    logging.warning(f"🤖  STEP {agent_calls}: AGENT THINKING...")
                    print("   " + "-" * 30)
                    yield {"type": "signal", "status": "thinking", "message": "Yeti「イエティ」は氷河の上で瞑想しています……"}
                elif "tools" in chunk:
                    tool_calls += 1
                    tool_info = chunk.get("tools", {})
                    # Clean up tool info for display
                    tool_name = "Unknown Tool"
                    content = ""
                    if 'messages' in tool_info and tool_info['messages']:
                        tool_name = tool_info['messages'][0].name
                        content = tool_info['messages'][0].content
                    
                    print("\n" + "   " + "🔧" * 20)
                    logging.warning(f"🛠️  EXECUTING TOOL: {tool_name}")
                    logging.warning(f"📥  TOOL OUTPUT: {str(tool_info)[:100]}...")
                    print("   " + "🔧" * 20 + "\n")
                    
                    # Create a friendly search message based on the tool
                    search_msg = f"Yeti「イエティ」は谷をくまなく探して {tool_name} を探しています"
                    sources = []
                    
                    if "web_search" in tool_name.lower() or "search" in tool_name.lower():
                        import re
                        search_msg = "Yeti「イエティ」は答えを探してインターネットを閲覧しています。"
                        # Extract URLs from the content
                        urls = re.findall(r'https?://[^\s\)\n]+', content)
                        # Deduplicate and limit to top 6 randomized
                        unique_urls = []
                        for u in urls:
                            if u not in unique_urls:
                                unique_urls.append(u)
                        
                        import random
                        random.shuffle(unique_urls)
                        
                        if len(unique_urls) > 6:
                            unique_urls = unique_urls[:6]
                        
                        for url in unique_urls:
                            domain = url.split("//")[-1].split("/")[0]
                            sources.append({
                                "url": url,
                                "domain": domain,
                                "favicon": f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
                            })
                    elif "weather" in tool_name.lower():
                        search_msg = "Yeti「イエティ」は天気のためにAPIに接続しています。"
                        sources.append({
                            "url": "https://www.weatherapi.com/",
                            "domain": "weatherapi.com",
                            "favicon": "https://www.google.com/s2/favicons?domain=weatherapi.com&sz=64"
                        })
                    elif "exchange" in tool_name.lower() or "rate" in tool_name.lower():
                        search_msg = "Yeti「イエティ」はスマイルズ・モバイル・レミットの為替レートに関するAPIリクエストを送信しています。"
                        sources.append({
                            "url": "https://www.smileswallet.com/japan/exchange-rates/",
                            "domain": "smileswallet.com",
                            "favicon": "https://www.google.com/s2/favicons?domain=smileswallet.com&sz=64"
                        })
                        
                    yield {
                        "type": "signal", 
                        "status": "searching", 
                        "message": search_msg, 
                        "sources": sources
                    }
        
        end_time = time.time()
        total_time = end_time - start_time
        print("\n" + "#" * 50)
        logging.warning(f"🏁  PROCESS COMPLETE | Total Time: {total_time:.2f}s")
        logging.warning(f"📊  STATS: Agent Steps: {agent_calls} | Tool Calls: {tool_calls}")
        yield {"type": "signal", "status": "complete", "message": "Yeti「イエティ」は現在の作業を完了しました。"}
        print("#" * 50 + "\n")


async def get_chat_history(thread_id: int):
    """
    Fetch conversation history for a given thread_id from the database.
    Returns messages in the format expected by the frontend.
    """
    config: RunnableConfig = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"user_id": thread_id},
    }

    async with AsyncPostgresSaver.from_conn_string(conn) as checkpointer:
        await checkpointer.setup()
        app_instance = create_react_agent(model, tools, checkpointer=checkpointer)

        state = await app_instance.aget_state(config=config)
        messages = state.values.get("messages", []) if state and state.values else []

        # Convert LangChain messages to frontend format
        frontend_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                continue  # Skip system messages in the UI
            elif isinstance(msg, HumanMessage):
                frontend_messages.append({
                    "role": "user",
                    "content": msg.content,
                    "think": ""
                })
            elif isinstance(msg, AIMessage):
                # Extract think tags if present
                content = msg.content
                think = ""
                if "<think>" in content and "</think>" in content:
                    match = re.search(r"<think>([\s\S]*?)<\/think>", content)
                    if match:
                        think = match.group(1).strip()
                        content = content[match.end():].strip()

                frontend_messages.append({
                    "role": "ai",
                    "content": content,
                    "think": think
                })

        return frontend_messages
