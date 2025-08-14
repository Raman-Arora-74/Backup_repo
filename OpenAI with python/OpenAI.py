from openai import OpenAI 
client = OpenAI()
# this system content u can change which u want behaviour of ChatGPT
messages = [
    {"role":"system","content":"you are a kind assistant,friendly and explain things with real time examples"}
]
def chat():
    while True:
        msg = input(str("You :")).strip()
# here u can write any specific word which help to exit from the loop 
        if msg.capitalize() in ["Bye","Exit","Goodbye","See ya"]: 
            print("Chatbot : Goodbye! See ya.")  
            break  
        dic = {"role":"user","content":msg}
        messages.append(dic)
        response = client.chat.completions.create(
# choose any model    ⬇️       here 
            model='gpt-4.1-mini',
            messages=messages 
        )        
        reply = response.choices[0].message.content
        print("ChatGPT :", reply)
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat()
