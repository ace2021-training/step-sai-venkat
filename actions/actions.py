# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from re import S
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import spacy
import mysql.connector

nlp = spacy.load('en_core_web_md')

mydb = mysql.connector.connect(host = "localhost", user = "root",password = "", database = "OfficeApplications")  
print(f"my db is {mydb}")

class ActionLogin(Action):

    def name(self) -> Text:
        return "action_login"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username")[0]
        password = tracker.get_slot("password")[0]

        print(f"my username is {username}")
        print(f"my password is {password}")

        mycursor = mydb.cursor()
        sql = "SELECT Password FROM Account WHERE Username = %s "
        adr = (username, )

        mycursor.execute(sql, adr)

        myresult = mycursor.fetchall()
        print(f"my myresult is {myresult}")

        if (len(myresult) == 0):
            dispatcher.utter_message("User does not exist, would you like to create an account?")
        
        else:
            if(password in myresult[0]):
                sql2 = "Select Position FROM Positions WHERE Status IS NULL"
                mycursor.execute(sql2)
                myresults2 = mycursor.fetchall()

                message = "Login was successful. Please type a desired position from the options below"

                buttons = []

                for x in myresults2:
                    buttons.append({"title": "{}".format(x[0]), "payload":x[0]})
                print(f"my buttons is {buttons}")
                dispatcher.utter_message(text=message , buttons=buttons)
                
            else:
                dispatcher.utter_message("Password Incorrect, Please start from the beginning")


        return []

class ActionAddUnderJob(Action):

    def name(self) -> Text:
        return "action_add_under_job"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sentence = tracker.latest_message.get('text')

        rules_pos = ["NOUN", "PART"]
        rules_morph = ["Case=Nom", "Case=Acc", "NumType=Card", "Degree=Pos", "VerbForm=Inf"]
        rules_dep = ["nsubj", "dobj", "pobj"]

        sentence_list = []
        sentence_list = sentence.split(",")

        l = ""

        x = 0

        for z in range (0, len(sentence_list)):

            keywords = []

            list_morphed = []

            doc = nlp(sentence_list[z])

            for token in doc:
                if(token.is_stop == False):
                    morphing = token.morph
                    list_morphed = str(morphing).split("|")
                    for i in range(0, len(list_morphed)):
                        if(token.pos_ in rules_pos or list_morphed[i] in rules_morph or token.dep_ in rules_dep):
                            keywords.append(token)
                            break

            i = ""
            j = 0
            if(x != len(sentence_list)-1):
                for words in keywords:
                    if(j==0):
                        i = i + str(words)
                
                    elif(j == len(keywords)-1):
                        i = i + " " + str(words) + ", "
                
                    else:
                        i = i + " " + str(words)
                    j = j + 1
            else:
                for words in keywords:
                    if(j==0):
                        i = i + str(words)
                
                    else:
                        i = i + " " + str(words)
                    j = j + 1
            
            x = x + 1
                
            l = l + i

        role = tracker.get_slot("position_role")[0]
        username = tracker.get_slot("username")[0]

        print(f"my role is {role}")

        mycursor = mydb.cursor()

        sql = "SELECT Name FROM Account WHERE Username = %s"
        adr = (username,)

        mycursor.execute(sql, adr)

        myresult = mycursor.fetchall()

        for y in myresult:
            mycursor = mydb.cursor()
            sql2 = "UPDATE Positions SET PositionHolderName = %s, QualificationsOfPositionHolder = %s, Status = 'Approval Pending' WHERE Position=%s"
            adr2 = (y[0], l ,role)
            mycursor.execute(sql2, adr2)
            mydb.commit()
            print(f"my adr2 is {adr2}")

        dispatcher.utter_message("Thank You For Applying. Please check you status in 24 hours")

        return []

class ActionCreate(Action):

    def name(self) -> Text:
        return "action_create"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username_new")[0]
        password = tracker.get_slot("password_new")[0]
        re_password = tracker.get_slot("re_password")[0]
        name = tracker.get_slot("name")[0]

        mycursor = mydb.cursor()

        sql2 = "SELECT Username FROM Account"
        mycursor.execute(sql2)

        myresult = mycursor.fetchall()

        print(f"My results is {myresult}")

        if (username not in myresult[0]):
            if (password == re_password):
                sql = "INSERT INTO Account (Username, Password, Name) VALUES (%s, %s, %s) "
                adr = (username, password, name)

                mydb.commit()

                mycursor.execute(sql, adr)

                dispatcher.utter_message("Welcome To Sirius! Please start from beginning to apply")
        
            else:
                dispatcher.utter_message("Password do not match, Please start from the beginning")
        else:
            dispatcher.utter_message("User Already Exists, Please Start From Beginning")

        return []

class ActionLogintSatusCheck(Action):

    def name(self) -> Text:
        return "action_login_status_check"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username")[0]
        password = tracker.get_slot("password")[0]

        mycursor = mydb.cursor()
        sql = "SELECT Password FROM Account WHERE Username = %s "
        adr = (username, )

        mycursor.execute(sql, adr)

        myresult = mycursor.fetchall()

        if (len(myresult) == 0):
            dispatcher.utter_message("User does not exist, would you like to create an account?")
        
        else:
            if(password in myresult[0]):
                sql3 = "SELECT Name FROM Account WHERE Username = %s "
                adr2 = (username, )

                mycursor.execute(sql3, adr2)

                myresult2 = mycursor.fetchall()

                for i in myresult2:
                    sql2 = "Select Status FROM Positions WHERE PositionHolderName = %s"
                    adr = (i[0],)
                    mycursor.execute(sql2, adr)
                    myresults3 = mycursor.fetchall()
                
                for i in myresults3:
                     dispatcher.utter_message("Your Application Status Is: {}".format(i[0]))

            else:
                dispatcher.utter_message("Password Incorrect, Please start from the beginning")

        return []