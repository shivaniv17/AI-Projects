import requests
from typing import List, Dict, Text, Tuple
import logging
import json
import re
import requests

policycancel = {
    "sopExecJSON": {
        "requestHeaderData": {
            "userid": "sbsuperadmin"
        },
        "requestRulesData": {},
        "sopName": "policycancelSOP",
        "execSOPParamsData": {
            "msg": "test message",
            "sleep": "120",
            "EffectiveDate": "7/10/2021",
            "policynumber": "Line1000105",
            "url": "http://10.128.0.2:8080/Express/express.aspx"
        }
    }
}

invoiceDocument = {
    "sopExecJSON": {
        "requestHeaderData": {
            "userid": "sbsuperadmin"
        },
        "requestRulesData": {},
        "sopName": "invoicesop",
        "execSOPParamsData": {

            "msg": "test message",
            "sleep": "120",
            "policynumber": "Line1000007",
            "url": "http://10.128.0.2:8080/Express/default.aspx"
        }
    }

}

claimStaus = {

    "sopExecJSON": {

        "requestHeaderData": {

            "userid": "sbsuperadmin"

        },

        "requestRulesData": {},

        "sopName": "claimSOP",

        "execSOPParamsData": {



            "msg": "test message",

            "sleep": "120",

            "Claimnumber": "PR2109000090",

            "url": "http://localhost/Suite_AFS.Claims/Desktop/HomePage/Default.aspx?src=%2fSuite_AFS.Claims%2fDesktop%2fHomePage%2fHomePage.aspx&StaticPulseMode=true&IframeMode=true&UserStateId=08D93F869129A7A9"

        }

    }

}

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

dateOfLoss = {

    "sopExecJSON": {

        "requestHeaderData": {

            "userid": "sbsuperadmin"

        },

        "requestRulesData": {},

        "sopName": "dateSOP",

        "execSOPParamsData": {



            "msg": "test message",

            "sleep": "120",

            "policynumber": "Line1000026",

            "url": "http://localhost/Suite_AFS.Claims/Desktop/HomePage/Default.aspx?src=%2fSuite_AFS.Claims%2fDesktop%2fHomePage%2fHomePage.aspx&StaticPulseMode=true&IframeMode=true&UserStateId=08D93F869129A7A9"

        }

    }

}

policyDocument = {
    "sopExecJSON": {
        "requestHeaderData": {
            "userid": "sbsuperadmin"
        },
        "requestRulesData": {},
        "sopName": "policydocsop",
        "execSOPParamsData": {

            "msg": "test message",
            "sleep": "120",
            "policynumber": "Line1000007",
            "url": "http://10.128.0.2:8080/Express/express.aspx"
        }
    }

}

policyendorse = {
    "sopExecJSON": {
        "requestHeaderData": {
            "userid": "sbsuperadmin"
        },
        "requestRulesData": {},
        "sopName": "endorsesop",
        "execSOPParamsData": {
            "msg": "test message",
            "sleep": "120",
            "Detail": "Shifting to new City",
            "EffectiveDate": "9/9/2021",
            "Reason": "Endorsement",
            "policynumber": "Line1000105",
            "url": "http://10.128.0.2:8080/Express/express.aspx"
        }
    }

}
##############################################################################


def getResponse(url):
    resp = requests.get(url)
    code = resp.status_code
    datastr = resp.text
    data = json.loads(datastr)
    return data


def getdetails(id):
    url = ("http://35.206.75.60:9090/api/v1/policy/"+id)
    return url


def getPODetails():
    url = "https://35.208.123.208:8443/syntbotssm/rest/executeSOPBySOPNameInSync"
    return url


def formatdetailsSop(sopname, p_no):
    info["sopExecJSON"]["sopName"] = sopname
    info["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no


def SopResponse(url, p_no, sop):
    formatdetailsSop(sop, p_no)
    test1 = json.dumps(info, indent=4)
    response = requests.post(url, test1, auth=(
        'sbsuperadmin', 'Med2O!sChnTn'), headers=headers, verify=False)
    datastr = response.content
    r = json.loads(datastr)
    return r


def formatdetailsdoc(sopname, p_no):
    if(sopname == "policydocsop"):
        policyDocument["sopExecJSON"]["sopName"] = sopname
        policyDocument["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no
    elif(sopname == "dateSOP"):
        dateOfLoss["sopExecJSON"]["sopName"] = sopname
        dateOfLoss["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no
    elif(sopname == "fetchdSOP"):
        policyDocument["sopExecJSON"]["sopName"] = sopname
        policyDocument["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no
    elif(sopname == "endorsesop"):
        policyendorse["sopExecJSON"]["sopName"] = sopname
        policyendorse["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no
    elif(sopname == "policycancelSOP"):
        policycancel["sopExecJSON"]["sopName"] = sopname
        policycancel["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no
    else:
        invoiceDocument["sopExecJSON"]["sopName"] = sopname
        invoiceDocument["sopExecJSON"]["execSOPParamsData"]["policynumber"] = p_no


def DocResponse(url, p_no, sop):
    formatdetailsdoc(sop, p_no)
    if(sop == "policydocsop" or sop == "fetchdSOP"):
        test1 = json.dumps(policyDocument, indent=4)
    elif(sop == "endorsesop"):
        test1 = json.dumps(policyendorse, indent=4)
    elif(sop == "policycancelSOP"):
        test1 = json.dumps(policycancel, indent=4)
    elif(sop == "invoicesop"):
        test1 = json.dumps(invoiceDocument, indent=4)
    elif(sop == "claimSOP"):
        test1 = json.dumps(claimStaus, indent=4)
    elif(sop == "dateSOP"):
        test1 = json.dumps(dateOfLoss, indent=4)
    else:
        print("No entity")
    response = requests.post(url, test1, auth=(
        'sbsuperadmin', 'Med2O!sChnTn'), headers=headers, verify=False)
    datastr = response.content
    r = json.loads(datastr)
    return r


##update part##
headers = {'Content-type': 'application/json', 'charset': 'utf-8'}
test = {
    "insuranceProduct": "",
    "customer": {
        "firstName": None,
        "lastName": None,
        "saluation": None,
        "nationality": None,
        "gender": None,
        "dob": None,
        "primaryPhoneNumber": 3216459870,
        "secondaryPhoneNumber": 0,
        "email": "abc@abc.com"
    },
    "agency": {
        "agencyId": 0
    },
    "policyInceptionDate": "2021-05-03",
    "policyExpiryDate": "2022-05-03",
    "quoteNumber": "Line18Q2021",
    "premiumAmount": 0,
    "premiumFrequency": None,
    "policyTerm": 12
}


def formatdetails(data, key, val):
    test["customer"]["firstName"] = data["customer"]["firstName"]
    test["customer"]["lastName"] = data["customer"]["lastName"]
    test["customer"]["saluation"] = data["customer"]["saluation"]
    test["customer"]["nationality"] = data["customer"]["nationality"]
    test["customer"]["gender"] = data["customer"]["gender"]
    test["customer"]["dob"] = data["customer"]["dob"]
    test["customer"]["primaryPhoneNumber"] = data["customer"]["primaryPhoneNumber"]
    test["customer"]["email"] = data["customer"]["email"]
    test["policyInceptionDate"] = data["policyInceptionDate"]
    test["policyExpiryDate"] = data["policyExpiryDate"]
    test["quoteNumber"] = data["quoteNumber"]
    test["premiumAmount"] = data["premiumAmount"]
    test["premiumFrequency"] = data["premiumFrequency"]
    test["policyTerm"] = data["policyTerm"]
    test["customer"][key] = val


def formatdetailsname(data, key1, val1, key2, val2):
    test["customer"]["firstName"] = data["customer"]["firstName"]
    test["customer"]["lastName"] = data["customer"]["lastName"]
    test["customer"]["saluation"] = data["customer"]["saluation"]
    test["customer"]["nationality"] = data["customer"]["nationality"]
    test["customer"]["gender"] = data["customer"]["gender"]
    test["customer"]["dob"] = data["customer"]["dob"]
    test["customer"]["primaryPhoneNumber"] = data["customer"]["primaryPhoneNumber"]
    test["customer"]["email"] = data["customer"]["email"]
    test["policyInceptionDate"] = data["policyInceptionDate"]
    test["policyExpiryDate"] = data["policyExpiryDate"]
    test["quoteNumber"] = data["quoteNumber"]
    test["premiumAmount"] = data["premiumAmount"]
    test["premiumFrequency"] = data["premiumFrequency"]
    test["policyTerm"] = data["policyTerm"]
    test["customer"][key1] = val1
    test["customer"][key2] = val2


def putResponse(p_no, url, val, key):
    geturl = getdetails(p_no)
    data = getResponse(geturl)
    formatdetails(data, key, val)
    test1 = json.dumps(test, indent=4)
    response = requests.put(url, test1, headers=headers)
    datastr = response.content
    r = json.loads(datastr)
    return r


def putResponsename(p_no, url, val1, key1, val2, key2):
    geturl = getdetails(p_no)
    data = getResponse(geturl)
    formatdetailsname(data, key1, val1, key2, val2)
    test1 = json.dumps(test, indent=4)
    response = requests.put(url, test1, headers=headers)
    datastr = response.content
    r = json.loads(datastr)
    return r


def updatedetails(id):
    url = ("http://35.206.75.60:9090/api/v1/policy/async/"+id)
    return url


p_no = "Line1000010"  # entity_dict.get("policyno")  # "Line1000009"
# query = "I want to update my primaryphonenumber"  # entity_dict.get("query")
query = "i want to know my insuredsum"
url = getdetails(p_no)
data = getResponse(url)
print(data)
s = query
s = s.split(" ")
# data1= {"father": ['dad', 'daddy', 'old man', 'pa', 'pappy', 'papa', 'pop'],
#  "mother": ["mamma", "momma", "mama", "mammy", "mummy", "mommy", "mom", "mum"]}

entities = ["email", "registered email", "email ids", "emailid", "firstname", "customername", "primaryphonenumber",
            "firstName",  "lastname", "policyinceptiondate", "policyexpirydate", "premiumamount",
            "premiumduedate", "premiumfrequency", "policyterm", "totalpremiumPaid", "sumassured",
            "endorsementhistory", "nationality", "insuredsum", "paymentdue", "premiumvalue", "taxamount",
            "installmentfrequency", "invoicedocument", "policydocument", "policy", "endorsementsop"]
intent = ["update", "change", "render", "know",
          "show", "see", "get", "what", "want my",
          "want", "fetch", "cancel", "claim"]

for i in s:
    if(i == "know" or i == "show" or i == "see" or i == "get" or i == "what" or i == "want my" or i == "fetch" or i == "cancel" or i == "claim" or i == "date"):
        for i in s:
            if i in entities:
                if i == "email":
                    response = data["customer"]["email"]
                    print(response)
                    break
                elif i == "firstname":
                    response = data["customer"]["firstName"]
                    print(response)
                    break
                elif i == "primaryphonenumber":
                    response = str(
                        data["customer"]["primaryPhoneNumber"])
                    print(response)
                    break
                elif i == "lastname":
                    response = data["customer"]["lastName"]
                    print(response)
                    break
                elif i == "customername":
                    response = data["customerName"]
                    print(response)
                    break
                elif i == "policyinceptiondate":
                    response = str(data["policyInceptionDate"])
                    print(response)
                    break
                elif i == "policyexpirydate":
                    response = data["policyExpiryDate"]
                    print(response)
                    break
                elif i == "premiumamount":
                    response = str(data["premiumAmount"])
                    print(response)
                    break
                elif i == "premiumduedate":
                    response = str(data["premiumDueDate"])
                    print(response)
                    break
                elif i == "premiumfrequency":
                    response = data["premiumFrequency"]
                    print(response)
                    break
                elif i == "policyterm":
                    response = str(data["policyTerm"])
                    print(response)
                    break
                elif i == "totalpremiumPaid":
                    response = str(data["totalPremiumPaid"])
                    print(response)
                    break
                elif i == "sumassured":
                    response = str(data["sumAssured"])
                    print(response)
                    break
                elif i == "endorsementhistory":
                    response = str(data["endorsementHistory"])
                    print(response)
                    break
                elif i == "nationality":
                    response = data["nationality"]
                    print(response)
                    break
                ###SOP###
                elif i == "insuredsum":
                    url = getPODetails()
                    data = SopResponse(url, p_no, "InsuredSum_sop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = str(data["SumInsuredValue"])
                    print(response)
                    break
                elif i == "paymentdue":
                    url = getPODetails()
                    data = SopResponse(url, p_no, "PaymentDue_sop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = data["PaymentDue"]
                    print(response)
                    break
                elif i == "premiumvalue":
                    url = getPODetails()
                    data = SopResponse(
                        url, p_no, "PremiumValue_sop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = str(data["PremiumValue"])
                    print(response)
                    break
                elif i == "taxamount":
                    url = getPODetails()
                    data = SopResponse(url, p_no, "TaxAmount_sop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = str(data["TaxAmount"])
                    print(response)
                    break
                elif i == "installmentfrequency":
                    url = getPODetails()
                    data = SopResponse(
                        url, p_no, "InstallmentFrequency_sop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = str(
                        data["InstallmentFrequency"])
                    print(response)
                    break
                elif i == "invoicedocument":
                    url = getPODetails()
                    data = DocResponse(url, p_no, "invoicesop")
                    response = "Your invoice document has been sent to your registered email id. Please check after some time."
                    print(response)
                    break
                elif i == "policydocument":
                    url = getPODetails()
                    data = DocResponse(url, p_no, "policydocsop")
                    response = "Your policy document has been sent to your registered email id. Please check after some time."
                    print(response)
                    break
                elif i == "policy":
                    url = getPODetails()
                    data = DocResponse(
                        url, p_no, "policycancelSOP")
                    # data["policycancelSOP"]
                    response = "your policy has been cancelled"
                    print(response)
                    break
                elif i == "endorsementsop":
                    url = getPODetails()
                    data = DocResponse(url, p_no, "endorsesop")
                    data = {x.translate({32: None}): y
                            for x, y in data.items()}
                    response = data
                    print(response)
                    break

    elif(i == "update" or i == "change" or i == "render"):
        for i in s:
            if i in entities:
                if i == "email":
                    key = "email"
                    value = "a@gmail.com"  # entity_dict.get("email")
                    url = updatedetails(p_no)

                    data = putResponse(p_no, url, value, key)
                    print(data["message"])
                    break
                elif i == "firstname":

                    key = "firstName"
                    value = "harry"  # entity_dict.get("firstname")
                    url = updatedetails(p_no)
                    data = putResponse(p_no, url, value, key)
                    print(data["message"])
                    break
                elif i == "primaryphonenumber":

                    key = "primaryPhoneNumber"
                    value = int("1234567890")  # entity_dict.get("phoneNumber")
                    url = updatedetails(p_no)
                    data = putResponse(p_no, url, value, key)
                    print(data["message"])
                    break
                elif i == "lastname":

                    key = "lastName"
                    value = "potter"  # entity_dict.get("lastname")
                    url = updatedetails(p_no)
                    data = putResponse(p_no, url, value, key)
                    print(data["message"])
                    break
                elif i == "customername":

                    key1 = "firstName"
                    value1 = "Rakesh"  # entity_dict.get("firstname")
                    key2 = "lastName"
                    value2 = "Kumar"  # entity_dict.get("lastname")
                    url = updatedetails(p_no)
                    data = putResponsename(
                        p_no, url, value1, key1, value2, key2)
                    print(data["message"])
                    break

#intent = entity_dict.get("intent")

# if(intent == "know" or intent == "show" or intent == "see" or intent == "get" or intent == "what" or intent == "want my" or intent == "want" or intent == "fetch" or intent == "cancel" or intent == "claim" or intent == "date"):

# url = updatedetails(p_no)
# data = putResponse(p_no, url, value, entity)
# print(data)

# response = data["customerName"]
# print(response)
