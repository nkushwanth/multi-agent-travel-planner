import os
import certifi
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict,Annotated
import operator
import uuid
import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    BaseMessage,AnyMessage,HumanMessage,AIMessage,SystemMessage)

from langchain_groq import ChatGroq
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

def get_db_url():

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    if "sslmode=" not in db_url:
        seperator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{seperator}sslmode=require"
    return db_url

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

llm=ChatGroq(model="llama-3.3-70b-versatile",api_key=GROQ_API_KEY)

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage],operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)
    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight results obtained.")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def hotel_agent(state: TravelState):
    query = state["user_query"]
    hotel_data = tavily_search(query)
    return {
        "hotel_results": hotel_data,
        "messages": [AIMessage(content="Hotel results obtained.")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def itinerary_agent(state: TravelState):
    prompt = f"""
create a complete itinerary.
User query: {state['user_query']}
Flight results: {state['flight_results']}
Hotel results: {state['hotel_results']} 
Make the itineray practical , budget aware and easy to follow
"""
    response = llm.invoke(
        [SystemMessage(content="You are a travel planning assistant."),
         HumanMessage(content=prompt)]) 
    
    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def final_agent(state: TravelState):
    final_prompt = f"""
    Generate a final travel plan based on the following information:
User Query: {state['user_query']},
Flight Results: {state['flight_results']},
Hotel Results: {state['hotel_results']},
Itinerary: {state['itinerary']}
Format the final answer beautifully using these sections:
1.Trip Summary
2.Flight Details
3.Hotel suggestions
4.Day-wise Itinerary
5.Estimated Budget
6.Final Recommendations

Important:
-Be clear and practical
-mention that live flight API may not provide ticket prices if it is unavailable, so users should check with airlines for the latest information.
-keep the response useful for real travel planning
    """
    response = llm.invoke(
        [SystemMessage(content="You are a professional ai travel planning assistant."),
         HumanMessage(content=final_prompt)])
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

DATABASE_URL = get_db_url()
_conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer)

def run_travel_agent(user_input:str,thread_id:str|None=None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}
    result = travel_graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )
    final_response = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_response,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0)
    }

