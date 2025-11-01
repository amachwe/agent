from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from gen_ai_web_server import llm_client   

client = llm_client.Client()


class DataRecord(TypedDict):
    timestamp: str
    delta_open_price: float
    delta_close_price: float
    delta_high_price: float
    delta_low_price: float
    delta_volume: int

class AnalysisState(TypedDict):
    data: DataRecord
    insights: str
    validation: bool

def analyse_delta(data: AnalysisState):
    print(data)
    response  = client.send_request(prompt=[{"role": "user", "content":f"Analyze the following stock data changes and provide insights:\n{data}"}], run_config={"max_new_tokens": 1000, })
    analysis = client.extract_response(response)
    return {"insights": analysis}

def validate_insights(insights: str):
    print("Validating insights:", insights)
    if insights and len(insights["insights"]) > 10:
        return {"validation":True}
    return {"validation":False}

graph = StateGraph(AnalysisState)
graph.add_node(analyse_delta)
graph.add_node(validate_insights)
graph.add_edge(START, "analyse_delta")
graph.add_edge("analyse_delta", "validate_insights")
graph.add_edge("validate_insights", END)
graph = graph.compile()

data = DataRecord({
    "timestamp": "2024-10-01T10:00:00Z",
    "delta_open_price": 1.5,
    "delta_close_price": -0.5,
    "delta_high_price": 2.0,
    "delta_low_price": -1.0,
    "delta_volume": 100000
})
#resp = graph.invoke(AnalysisState({"data": data}))
#print("Analysis Result:", resp)

import tqdm
with open("./data/dracula.txt","r", encoding="utf-8") as file:
    para = ""
  
    rdf = ""
    for line in tqdm.tqdm(file.readlines()):
        if line.strip() == "":
            if para.strip() != "":
                response = client.send_request(prompt=[{"role": "user", "content":f"Update RDF using data:\n{para}\n\n RDF:{rdf}"}], run_config={"max_new_tokens": 1000})
                rdf += client.extract_response(response)
                para = ""
            else:
                print("Skipping empty paragraph")   
      
            
        para += line.strip() + "\n"


    print("Final RDF Data:\n", rdf)

    with open("dracula.rdf","w", encoding="utf-8") as rdf_file:
        rdf_file.write(rdf)

