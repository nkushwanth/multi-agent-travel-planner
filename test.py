from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

results = search_flights("plan a 7 day trip from New York to London")
print(results)

# results = tavily_search("Best places to visit in Europe")
# print(results)