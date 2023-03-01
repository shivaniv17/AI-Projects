
# pose sequence as a NLI premise and label as a hypothesis
# imports
from __future__ import print_function
from genericpath import isdir
import re
import os
import json
#from threading import ExceptHookArgs
import requests
import torch
# import tensorflow as tf
#from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, BertTokenizer
from pytorch_pretrained_bert.modeling import BertForQuestionAnswering
# from transformers import pipeline
import ast
# fastapi imports
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# email IMAP imap
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from json2table import convert
from pathlib import Path

app = FastAPI()
origins = [
    "http://localhost:8081"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["application/json"],
)

# for intent _extraction
model_path = 'bart-large-mnli/'
# model_path='distilbert-base-uncased-mnli/'
nli_model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# for Questionanswering
qa_model_path = 'bert-large-uncased-whole-word-masking-finetuned-squad/'
qa_model = BertForQuestionAnswering.from_pretrained(qa_model_path)
qa_tokenizer = BertTokenizer.from_pretrained(qa_model_path)


def zero_shot(sequence_to_classify, candidate_labels):
    x = tokenizer.encode(sequence_to_classify, candidate_labels,
                         return_tensors='pt', truncation=False)
    
    logits = nli_model(x.to(device))[0]
    # we throw away "neutral" (dim 1) and take the probability of
    # "entailment" (2) as the probability of the label being true
    entail_contradiction_logits = logits[:, [0, 2]]
    probs = entail_contradiction_logits.softmax(dim=1)
    prob_label_is_true = probs[:, 1]
    
    return prob_label_is_true


def answer_question(question, answer_text):
    
    input_ids = qa_tokenizer.encode(question, answer_text)    
    sep_index = input_ids.index(qa_tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids) - num_seg_a

    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    assert len(segment_ids) == len(input_ids)
    with torch.no_grad():
        start_scores, end_scores = qa_model(torch.tensor([input_ids]),  # The tokens representing our input text.
                                            token_type_ids=torch.tensor([segment_ids]))  # The segment IDs to differentiate question from answer_text

    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)    
    if torch.max(start_scores) >= 2 and torch.max(end_scores) >= 2:
        if answer_end >= answer_start:
            tokens = qa_tokenizer.convert_ids_to_tokens(input_ids)
            answer = tokens[answer_start]

            for i in range(answer_start + 1, answer_end + 1):
                if tokens[i] not in ['[UNK]', '[SEP]', '[CLS]']:
                    if tokens[i][0:2] == '##':
                        answer += tokens[i][2:]
                    else:
                        answer += ' ' + tokens[i]
            return answer


def parse_email(email_subject, email_body, sender_address):
    query1 = "what is the Policy Number?"

    extracted_fields = dict()
    # extracted_fields["Title"] = email_subject
    # extracted_fields["EmailID"] = sender_address

    Policy_Number = answer_question(query1, email_body)
    if Policy_Number:
        extracted_fields["Policy_Number"] = Policy_Number
    else:
        extracted_fields["Policy_Number"] = ""
    if not extracted_fields["Policy_Number"]:
        return False
    return extracted_fields


def email_reader():
    # account credentials
    username = "syntbots.hyperautomation@gmail.com"
    password = "Syntbots123$"

    def clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    imap.list()
    imap.select('inbox')
    #path = "email"
    #path1 = ((os.getcwd()+"/"+path).replace("\\", "/"))
    # os.rmdir(path1)
    status, messages = imap.search(None, "UNSEEN")
    mail_ids = messages[0].decode()
    id_list = mail_ids.split()
    if not id_list:
        return False
    for i in id_list:
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):                
                msg = email.message_from_bytes(response[1])                
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):                    
                    subject = subject.decode(encoding)                
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)                
                for part in msg.walk():                                          
                    content_type = part.get_content_type()        
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain":
                        folder_name = clean("email")
                        if not os.path.isdir(folder_name):
                            if(os.path.dirname(os.getcwd()) != folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                        header = ["email_subject",
                                    "email_body", "sender_address"]
                        value = []
                        value.append(subject)
                        value.append(body)
                        value.append(From)

                        res = {header[i]: value[i]
                                for i in range(len(header))}
                        res["email_body"] = (
                            re.sub('\r?\n', '', res["email_body"]))                    
                        jsonname = (
                            "data"+str(random.randint(0, 15))+".json")
                        jsonpath = os.path.join(folder_name, jsonname)
                        #jsonpath1 = os.path.dirname(jsonpath)
                        with open(jsonpath, 'w') as outfile:
                            json.dump(res, outfile)
                        outfile.close
                        
        # close the connection and logout
    imap.close()
    imap.logout()
    return True

def email_Error(receiver_address):

    mail_content = "Dear Customer," + "<br><br>"+"The email request from your end could not be fulfilled." +"<br>"+"Reason:"+"<br>"+"The policy number that you have shared doesn't match any existing policies in our system.<br>Please check the policy number and send the request again."+"<br><br>" + "<br><br> Thank You "+"<br>"+" Insurance Service Team <br><br><br><br>"+"<b>Note: This is an automated response to your query. Please do not respond to this mail.</b>"

    # The mail addresses and password
    sender_address = 'syntbots.hyperautomation@gmail.com'
    sender_pass = 'Syntbots123$'
    #receiver_address = 'ankit.2.kumar@atos.net'
    #receiver_address = 'vatsalya.mathur@atos.net'
    ptrn = re.compile("<([^>]+)>")
    #findall returns ['email','email2']. Join concats them.
    receiver_address=ptrn.findall(receiver_address)
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address[0]
    message['Subject'] = '[Issue] Regarding your Policy Servicing Request'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def email_sender(content,receiver_address):
    def jsontotable(content):
        json = {}
        for key, value in content.items():
            if(key != ("Customer Name") and key != ("Policy Number")):
                json[key] = value
        build_direction = "LEFT_TO_RIGHT"
        table_attributes = {"style": "width:100%", "border": 1}
        html = convert(json, build_direction=build_direction,
                       table_attributes=table_attributes)
        return html
    table = jsontotable(content)
    mail_content = "Hello " + str(content["Customer Name"])+"," + "<br><br>"+"Please find below, the information you have requested regarding your Policy - "+str(content["Policy Number"])+"<br><br>" + str(
        table) + "<br><br> Thank You "+"<br>"+" Insurance Service Team <br><br><br><br>"+"<b>Note: This is an automated response to your query. Please do not respond to this mail.</b>"

    # The mail addresses and password
    sender_address = 'syntbots.hyperautomation@gmail.com'
    sender_pass = 'Syntbots123$'
    #receiver_address = 'ankit.2.kumar@atos.net'
    #receiver_address = 'vatsalya.mathur@atos.net'
    ptrn = re.compile("<([^>]+)>")
    #findall returns ['email','email2']. Join concats them.
    receiver_address=ptrn.findall(receiver_address)
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address[0]
    message['Subject'] = 'Policy Details for Policy Number-' + content["Policy Number"]  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def rename_key(dict1, res1):
    duckreek_output = dict()
    score = dict()
    score["output"] = {}

    for key, value in res1.items():
        for k, v in dict1["duckreek_output"].items():
            if (k == key):
                duckreek_output.update({res1[key]: v})

    for key, value in res1.items():
        for k, v in dict1["score"].items():
            if (k == key):
                score.update({res1[key]: v})

    for key, value in res1.items():
        for k, v in dict1["scoredown"].items():
            if (k == key):
                score.update({res1[key]: v})

    score["output"].update(duckreek_output)
    return duckreek_output, score



@app.get("/syntbots-ai/process_email")
def email_extraction(request: Request):
    path = "email"
    path1 = ((os.getcwd()+"/"+path).replace("\\", "/"))
    responses = []    
    flag = email_reader()
    if(os.path.isdir(path1)):
        os.chdir(path1)
    if(flag == False):
        
        return "No new email to be processed right now."
    if(os.path.isdir(path1)):
        def read_text_file(file_path):
            with open(file_path, 'r') as outfile:
                json_object = json.load(outfile)
                return json_object

    def process():
        resp = {}
        resp['score'] = {}
        resp['scoredown'] = {}
        resp['duckreek_output'] = {}

        output = {}
        Label = ["policyExpiryDate", "premiumDueDate",
                    "totalPremiumPaid", "policyInceptionDate", "email", "customerName",
                    "primaryPhoneNumber", "InsuredSum_sop", "PaymentDue_sop", "PremiumValue_sop", "TaxAmount_sop",
                    "InstallmentFrequency_sop", "Policy_Number"]

        freetext = ["Policy Expiry Date", "Premium Due Date", "Total Premium Paid",
                    "Policy Inception Date", "Registered Email", "Customer Name",
                    "Primary Phone Number", "Insured Sum", "Payment Due", "Premium Value", "Tax Amount",
                    "Installment Frequency", "Policy Number"]
        res1 = {Label[i]: freetext[i] for i in range(len(Label))}
        score_list = []
        for l in range(len(Label)):
            score_list.append(
                zero_shot(email_body, freetext[l]).detach().item())

        score = dict()

        res = {Label[i]: score_list[i] for i in range(len(score_list))}

        def filter_dict(d, f):
            newDict = dict()
            for key, value in d.items():
                if f(key, value):
                    newDict[key] = value
            return newDict

        score = (filter_dict(res, lambda k, v: v >= (.60)))
        scoredown = (filter_dict(res, lambda k, v: v <= (.60)))

        info = {
            "sopExecJSON": {
                "requestHeaderData": {
                    "userid": "sbsuperadmin"
                },
                "requestRulesData": {},
                "sopName": "InstallmentFrequency_sop",
                "execSOPParamsData": {
                    "policynumber": "1000026"
                }
            }
        }

        def getPODetails():
            url1 = "https://35.208.123.208:8443/syntbotssm/rest/executeSOPBySOPNameInSync"
            return url1

        def putResponse(url, p_no, sop):
            headers = {'Content-type': 'application/json',
                        'charset': 'utf-8'}
            formatdetails(sop, p_no)
            test1 = json.dumps(info, indent=4)
            response = requests.post(url, test1, auth=(
                'sbsuperadmin', 'Med2O!sChnTn'), headers=headers, verify=False)
            datastr = response.content
            r = json.loads(datastr)
            return r

        def formatdetails(sopname, p_no):
            info["sopExecJSON"]["sopName"] = sopname
            info["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no

        def getPOService(resp, score):
            p_no = resp["Policy_Number"]
            url = getPODetails()
            output = []
            polist = []
            respo = {}
            # sop=["InsuredSum_sop","PaymentDue_sop","PremiumValue_sop","TaxAmount_sop","InstallmentFrequency_sop"]
            for key, value in score.items():
                output.append(putResponse(url, p_no, key))
                polist.append(key)
            res = {polist[i]: output[i] for i in range(len(output))}
            for k, v in res.items():
                if v != {'ExceptionType': 'Validation', 'Message': 'SOP Name is not Valid'}:
                    respo[k] = v            
            return respo

        # calling get service

        def getdetails(id):
            url = ("http://35.206.75.60:9090/api/v1/policy/"+id)
            return url

        def getResponse(url):                
            response = requests.get(url)                        
            datastr = response.text
            status=response.status_code
            if(status != 200):
                return False     
            data = json.loads(datastr)
            return data

        def getservice(resp):
            data=True
            #pre = "Line"
            p_no = resp["Policy_Number"]           
           # p_no = pre+p_no
            url = getdetails(p_no)
            data = getResponse(url)
            
            if(data==False):
                return False,score, scoredown
            # extracting name from data

            name = ['customerName']
            name = dict({item: data.get(item)for item in name})

            # explict addition of name to
            score.update(name)
            data = data.copy()
            
            
            
            data.update(data["customer"])
            del data['customer']

            for key, value in score.items():
                for key1, value1 in data.items():
                    if (key == key1):
                        output[key] = value1
            if(data==False):
                return False,score, scoredown

            return output, score, scoredown

        # calling question_answermodel
        if email_subject and email_body and sender_address:
            QAResult = True
            data=True 
            w_policy=True 
            NO_policy=True
            QAResult = parse_email(
                email_subject, email_body, sender_address)
            NO_policy=QAResult    
            if(QAResult == False):
                return NO_policy, res1, data
            data, score, scoredown = getservice(QAResult)
            w_policy=data
            if(w_policy==False ):                
                return QAResult,res,w_policy    

            poResp = getPOService(QAResult, score)
            for key, value in QAResult.items():
                resp["duckreek_output"][key] = value

            for key, value in data.items():
                resp["duckreek_output"][key] = value

            for key, value in score.items():
                if(key != ("customerName")):
                    resp["score"][key] = value

            for key, value in scoredown.items():
                resp["scoredown"][key] = value

            for key, value in poResp.items():
                resp["duckreek_output"][key] = value

            
        else:
            resp = {"error_msg": "Received invalid input"}

        return Response(content=json.dumps(resp), media_type="application/json"), res1,True

    # iterate through all file
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".json"):
            response = True
            file_path = f"{path1}/{file}"
            # call read text file function
            json_object = read_text_file(file_path)
            email_subject = json_object["email_subject"]
            email_body = json_object["email_body"]
            sender_address = json_object["sender_address"]
            print(email_subject)
            response, map,w_policy = process()
            if (response == False):
                if(os.path.isdir(path1)): 
                    if file.endswith(".json"):
                        file_path = f"{path1}/{file}"
                        os.remove(file_path)
                content={"response":"Policy number not found"}
                email_Error(sender_address)        
                responses.append(content)
                continue
            if (w_policy == False):
                if(os.path.isdir(path1)):                         
                    if file.endswith(".json"):
                        file_path = f"{path1}/{file}"
                        os.remove(file_path)   
                content1={"response":"Something is wrong with Policy Number"}
                email_Error(sender_address)        
                responses.append(content1)
                continue
            datastr = response.body
            respo = json.loads(datastr)
            e_response, postresponse = rename_key(respo, map)
            email_sender(e_response,sender_address)
            responses.append(postresponse)
            if file.endswith(".json"):
                file_path = f"{path1}/{file}"
                os.remove(file_path)
        
    del_path = os.path.dirname(os.getcwd())
    os.chdir(del_path)
    os.rmdir(del_path+"/"+path)

    return responses

  # uvicorn server
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8081, reload=False)
