import os
import json

simul_data = open("C:/Personal File/estimation_time/result.json")
sim_data = json.load(simul_data)

get_proc_time = sim_data["time"]
print(get_proc_time)