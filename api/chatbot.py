import json
from random import randint
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def messageGenerator(msg,type):
    with open('bot.json') as json_data:
        dataFinal = json.load(json_data)
    data = dataFinal['type']
    if type == 'type':
        output = ""
        flag = 0
        for i in data.keys():
            if flag == 0:
                if msg.lower() in i.lower():
                    flag = 1
                    output = data[i]
                    break
                else:
                    for j in data[i].keys():
                        if flag == 0:
                            if msg.lower() in j.lower():
                                flag = 1
                                output = data[i][j]
                                break
                            else:
                                for k in data[i][j]:
                                    if flag == 0:
                                        for l in k:
                                            if flag == 0:
                                                if msg.lower() in l.lower():
                                                    flag = 1
                                                    output = k
                                                    break
                                                else:
                                                    output = "Sorry, I don't understand"
                                                    break
    else:
        data = dataFinal['questions']
        output = "Sorry, I don't understand"
        temp = []
        for i in data.keys():
            temp.append([similar(msg.lower(),i.lower()),i])
        temp.sort(key=lambda x: x[0], reverse=True)
        output = data[temp[0][1]]
    return output

while True:
    msg = input("Enter your message: ")
    msgType = 'type'
    output = messageGenerator(msg,msgType)
    if msgType != 'type':
        if type(output) == str:
            print(output)
        else:
            print(output[randint(0,len(output)-1)])
    else:
        print(output)