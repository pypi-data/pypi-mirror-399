import requests
ans=""
def OllamaMadhiri(string,ask):
    obj=string
    obj2=ask
    object={
        "model":obj,
        "prompt":obj2,
        "stream":False
    }
    res=requests.post("http://localhost:11434/api/generate",json=object)
    global ans
    ans=res.json()["response"]

def badhil():
    return ans
 