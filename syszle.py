from openai import OpenAI
from openai import APIConnectionError,RateLimitError
import os
import subprocess
import json
import time
from ddgs import DDGS
from firecrawl import FirecrawlApp
import shlex
fir = FirecrawlApp(api_key="YOUR API KEY", api_url="YOUR_ENDPOINT")
#Instead of appending hup to the end of responses, create a dummy skill called task_complete that does nothing but signals to the program that the task is done.
task = False
use_firecrawl_search = False
use_local_scrape = False
nosk = True
quick = False
start = True
out = []
com = False
tempase = False

meshis = []
tools = [
    {
        "type": "function",
        "function":{
            "name": "command_executor",
            "description": "Executes a skill through the command executor. Simply write the command exactly as it should be executed. The output of this command will then be returned to you for your final output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type":"string","description":"Write the command exactly as is to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "Search",
            "description": "This returns a series of websites with their scraped content based off of a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type":"string","description":"Search Anything"}
                },
                "required": ["query"]
            }
        }
    }
]
def search(query):
    links = []
    scrape = {}
    results = DDGS().text(query,max_results=10)
    for i in results:
        links.append(i["href"])
    for link in links:
        try:
            re = fir.scrape_url(link)
            scrape[link] = re
        except Exception:
            pass
    return scrape
def command_executor(arg):
    try:
        pass #args = shlex.split(arg)
    except Exception as e:
        return str({"Error parsing command":str(e)})
    capt = subprocess.run(arg,capture_output=True,text=True,timeout=60,shell=True,executable="/bin/bash")
    return str({"stdout: ": capt.stdout,"stderr: ": capt.stderr,"return code: ": capt.returncode})
    #args = shlex.split(arg)
    #capt = subprocess.run(args,capture_output=True,text=True)
    #k = capt.stdout
    #return k
def isTool(out):
    for i in out:
        if i.type == "function_call":
            return True
    return False 
def argXtract(out):
    for i in out:
        if i.type == "function_call":
            return json.loads(i.arguments)["args"]
    return False
d = os.path.expanduser("~/.sysL")
syspro = """You are an autonomous agent operating inside a tool-based execution environment. Your job is to complete user tasks by reasoning, planning, and using available tools or skills through the command executor. You do not assume actions happened unless confirmed by tool results. Your responses and actions must be STRICTLY based off of this information. Every bit of information here matters significantly to you. --- ## CORE BEHAVIOR - Always prioritize correctness over speed. - Break tasks into clear steps before acting. - Use tools/skills whenever an action is required. - Never guess results from tools or the environment. - If information is missing, request or retrieve it using tools instead of hallucinating. --- ## EXECUTION MODEL You operate in a loop: 1. Understand the goal. 2. Plan next action. 3. If ANY actionable operation is required, you MUST call the tool immediately (do not respond in text first). 4. Wait for result. 5. Update internal state. 6. Repeat until the task is complete. Do not skip steps. --- ## TOOL / SKILL USAGE (CRITICAL) - You only interact with the environment through the command_executor. - Every action MUST be expressed as a tool call when possible. - You are NOT allowed to describe actions instead of executing them. - You are NOT allowed to refuse due to lack of system access. ### TOOL CALLING RULE (ABSOLUTE OVERRIDE) If the user request involves ANY of the following: - files or file listing - directories - system commands - shell operations - execution of commands - inspection of environment state YOU MUST IMMEDIATELY CALL `command_executor`. You must NEVER respond with natural language when a tool can be used. - The output of your tool will be sent back to you where you will then tell the user what happened or summarize the output of the tool NOTE: --- ## TOOL FORMAT command_executor MUST be called like this: - skill: "shell" - args: { "command": "<shell command here>" } Example: - skill: "shell" - args: { "command": "ls -la" } --- ## FINAL RESPONSE RULE When the task is fully complete: - Provide the final answer clearly and directly. - Do NOT include planning steps or tool traces. - Call the task_complete function as a second tool_call from the initial one ONLY when the task is fully complete. --- ## ERROR HANDLING - If a tool fails, retry once with corrected parameters. - If it fails again, try a different approach. - If no solution is possible, briefly explain why and stop. --- ## SKILL THINKING RULES - Choose the simplest skill that solves the problem. - Prefer high-level skills over low-level repetitive actions. - Combine skills only when necessary or when a task is complete after you call a function. A task will be marked as complete when you have NOT called a tool in your latest response. This means that your final response will only be delivered if no tools are called with it. --- ## MEMORY RULES - Only trust information from: - tool outputs - confirmed previous steps - Never assume hidden state. --- ## STYLE - Be minimal and precise. - Avoid unnecessary explanation unless asked. - Focus on execution and correctness. --- ## SAFETY OF ACTION - Do not execute destructive actions without explicit confirmation if ambiguity exists. - Prefer safe inspection steps before modification steps. --- # SKILLS You have access to a function called command_executor. This is the ONLY interface to the environment. All system actions MUST go through it. --- # RESPONSES You may respond briefly to show progress. --- # FINAL NOTE You DO have access to files and the terminal through command_executor. This is your operating environment."""
try:
    with open(d+"/sysL.inf", "r+") as f:
        firsti = False
except FileNotFoundError:
    firsti = True
# The sysL.inf goes in order of api_key, base_url, model
base_urli = "https://api.openai.com/v1/"
#firsti = True
if firsti:
    print("Welcome to sysLite! We are going to setup your agent. Would you like to set up a custom base url for an openai compatible api? (If you intend to use open ai themselves, just hit enter")
    ans = input()
    if ans.lower() == "yes":
        base_urli = input("Base Url (Ends in /v1): ")
    api_keyi = input("Api Key: ")
    if api_keyi == "":
        api_keyi = "You didn't put in an api key"
    client = OpenAI(api_key=api_keyi,base_url=base_urli)
    try:
        models = client.models.list()
        print("What model would you like to use?")
        for i in models:
            print(i.id)
    except APIConnectionError:
        print("Cannot list models. Select a model: ")
    model = input()
    print("Creating sysLite Dir...")
    d = os.path.expanduser("~/.sysL")
    os.makedirs(d,exist_ok=True)
    print("Give it a name: ")
    name = input()
    print("Writing information to save file...")
    with open(d+"/sysL.inf","w") as savv:
        savv.write(f'{{"name": "{name}","api_key": "{api_keyi}","base_url": "{base_urli}","model": "{model}"}}\n')
        print("Onboarding Complete!")
if not tempase:
    with open(d+"/sysL.inf","r") as savv:
        s = savv.readlines()
        prov = json.loads(s[0].strip("\n"))
        base_urli = prov["base_url"]
        model = prov["model"]
        name = prov["name"]
        api_keyi = prov["api_key"]
        
else:
    base_urli = input("Base Url (Ends in /v1): ")
    api_keyi = input("Api Key: ")
    if api_keyi == "":
        api_keyi = "You didn't put in an api key"
    client = OpenAI(api_key=api_keyi,base_url=base_urli)
    try:
        models = client.models.list()
        print("What model would you like to use?")
        for i in models:
            print(i.id)
    except APIConnectionError:
        print("Cannot list models. Select a model: ")
    model = input()
client = OpenAI(api_key=api_keyi,base_url=base_urli)
while True:
    print(f"Using model: {model}")
    print("\n\n\n")
    res = input("You: ")
    if res == "/provider":
        print("Would you like to add a model provider or select one.")
        af = input("select or add?")
        if af == "select":
            print("Pick from these: ")
            with open(d+"/sysL.inf","r") as savv:
               s = savv.readlines()
               for i in s:
                   p = json.loads(i)
                   print(p["name"])
               print("Current Provider: ", name)
               moice = input("Select a provider by name: ")
               bud = 0
               for i in s:
                   p = json.loads(i)
                   if p["name"] == moice:
                       print("NI")
                       base_urli = p["base_url"]
                       model = p["model"]
                       name = p["name"]
                       api_keyi = p["api_key"]
                       client = OpenAI(api_key=api_keyi,base_url=base_urli,timeout=None)
                       s[0],s[bud] = s[bud],s[0]
                       with open(d+"/sysL.inf","w") as savv:
                           savv.writelines(s)
                       break
                   bud+=1
        elif af == "add":
            ans = "yes"
            if ans.lower() == "yes":
                base_urli = input("Base Url (Ends in /v1): ")
            api_keyi = input("Api Key: ")
            if api_keyi == "":
                api_keyi = "You didn't put in an api key"
            client = OpenAI(api_key=api_keyi,base_url=base_urli,timeout=None)
            try:
                models = client.models.list()
                print("What model would you like to use?")
                for i in models:
                    print(i.id)
            except APIConnectionError:
                print("Cannot list models. Select a model: ")
            model = input()
            print("Give it a name: ")
            name = input()
            print("Writing information to save file...")
            with open(d+"/sysL.inf","a") as savv:
                savv.write(f'{{"name": "{name}","api_key": "{api_keyi}","base_url": "{base_urli}","model": "{model}"}}\n')
        continue
    print("\n")
    print("*")
    print("\n")
    if "nosk" in res:
        nosk = True
    if "quick" in res:
        nosk = True
        quick = True
    task = True
    if res == "/model":
        print("What model would you like to use?")
        models = client.models.list()
        for i in models:
            print(i.id)
        model = input()
        with open(d+"/sysL.inf","r") as salv:
            lines = salv.readlines()
        #with open(d+"/sysL.inf","w") as salv:
            #lines[2*idl] = model+"\n"
            #salv.writelines(lines)
        print("\n\n\n")
        continue
    if nosk:
        res = res.strip("nosk")
        if start:
            print("FF")
            use = {"role":"user","content":res}
            meshis.append({"role": "system", "content": str(syspro)})
            meshis.append(use)
            response = client.chat.completions.create(model=model,messages=meshis,tools=tools,timeout=None)
            meshis.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": response.choices[0].message.tool_calls[0].id,
                        "type": "function",
                        "function": {
                            "name": response.choices[0].message.tool_calls[0].function.name,
                            "arguments": response.choices[0].message.tool_calls[0].function.arguments
                            }
                        }
                    
                    ] if response.choices[0].message.tool_calls else None
                })
            start = False  
            print(use)
        else:
            print("EE")
            use = {"role":"user","content":res}
            meshis.append(use)
            response = client.chat.completions.create(model=model,messages=meshis,tools=tools,timeout=None)
            #meshis.append({"role":"assistant","content":response.choices[0].message.content})
            meshis.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": response.choices[0].message.tool_calls[0].id,
                        "type": "function",
                        "function": {
                            "name": response.choices[0].message.tool_calls[0].function.name,
                            "arguments": response.choices[0].message.tool_calls[0].function.arguments
                            }
                        }
                    
                    ] if response.choices[0].message.tool_calls else None
                })
        if response.choices[0].message.tool_calls:
            print(response.choices[0].message.tool_calls)
            print("DD")
            hup = True
            print(response.choices[0].message.tool_calls)
            com = response.choices[0].message.tool_calls[0].function.arguments
            name = response.choices[0].message.tool_calls[0].function.name
            com = json.loads(com)
            print(com)
            call_id = response.choices[0].message.tool_calls[0].id
            print(com)
            print(name)
            if name == "command_executor":
                arg = com["command"]
                print(arg)
                comO = command_executor(arg)
                print(type(comO))
                print(type(call_id))
                print(f"NI: {comO}")
                meshis.append({"role":"tool","tool_call_id":call_id,"content":comO})
                #print(meshis)
            elif name == "Search":
                arg = com["query"]
                comO = search(arg)
                #WILL NOT WORK YET!!!
                print(type(comO))
                print(type(call_id))
                meshis.append({"role":"tool","tool_call_id":call_id,"content":str(comO)})
            response = client.chat.completions.create(model=model,messages=meshis,tools=tools,timeout=None)
            rek = response.choices[0].message.content
            meshis.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": response.choices[0].message.tool_calls[0].id,
                        "type": "function",
                        "function": {
                            "name": response.choices[0].message.tool_calls[0].function.name,
                            "arguments": response.choices[0].message.tool_calls[0].function.arguments
                            }
                        }
                    
                    ] if response.choices[0].message.tool_calls else None
                })
            print(rek)
            if response.choices[0].message.tool_calls != None:
                hup = True
            else:
                print(rek)
            try:
                if hup:
                    while hup:
                        print(response.choices[0].message.tool_calls)
                        if response.choices[0].message.tool_calls == None:
                            hup = False
                            print(rek)
                            break
                        name = response.choices[0].message.tool_calls[0].function.name
                        com = response.choices[0].message.tool_calls[0].function.arguments
                        com = json.loads(com)
                        #print(com)
                        call_id = response.choices[0].message.tool_calls[0].id
                        if name == "command_executor":
                            arg = com["command"]
                            print(arg)
                            comO = command_executor(arg)
                            print(type(comO))
                            print(type(call_id))
                            meshis.append({"role":"tool","tool_call_id":call_id,"content":comO})
                            #print(meshis)
                        elif name == "Search":
                            arg = com["query"]
                            print(arg)
                            comO = search(arg)
                            print(type(comO))
                            print(type(call_id))
                            meshis.append({"role":"tool","tool_call_id":call_id,"content":str(comO)})
                        response = client.chat.completions.create(model=model,messages=meshis,tools=tools,timeout=None)
                        meshis.append({
                            "role": "assistant",
                            "content": response.choices[0].message.content,
                            "tool_calls": [
                                {
                                    "id": response.choices[0].message.tool_calls[0].id,
                                    "type": "function",
                                    "function": {
                                        "name": response.choices[0].message.tool_calls[0].function.name,
                                        "arguments": response.choices[0].message.tool_calls[0].function.arguments
                                        }
                                    }
                                
                                ] if response.choices[0].message.tool_calls else None
                            })
                        rek = response.choices[0].message.content
                        if response.choices[0].message.tool_calls == None:
                            hup = False
                            print(rek)
                            break
                        print(rek)
            except RateLimitError as ratlier:
                print("Rate Limited by Gemini or some shit idk. I am going to pause for a minute to cool down.")
                time.sleep(60)
        else:
            print("\n")
            print(response.choices[0].message.content)
    #Run a command to list all files in the directory then tell the contents of a txt file that you find with another command nosk
    #Run a command to list all files in the directory and summarize them to the user nosk
    #Search up glue and tell me some stuff about it nosk
