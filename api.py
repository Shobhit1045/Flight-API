import openai
import datetime
from dateutil import parser
from datetime import date
import os
import json
from mongo_db_s import db_ses_fetch,db_ses_response,bd_ses_append_user
from flask import Flask, request, render_template

openai.api_key = os.getenv("OPENAI_API_KEY")
def get_todays_date():
    today = date.today()
    return today.strftime("%Y-%m-%d")

live_date = get_todays_date()

flight_booking_prompt = "You are now chatting with the Flight Booking Assistant. Please provide your flight booking details or ask questions related to flight booking."

instructions_non_mand = '''As a Flight Booking Assistant, your main job is to help users with flight bookings. Follow these guidelines when responding to user queries:

Rule -1: Focus on Flight Booking: Your primary role is to assist with flight booking and flight-related queries. Ignore any non-flight-related questions and do not respond to them.
 
Rule -2: Extract Specific Information: If the user provides any of the following details, extract and return them in JSON format:
 
Class: Economy/Premium Economy/Business/First class

Trip type: One-way/Round trip

Number of stops: 0/1/2

Airlines: Air India/AirAsia India/IndiGo/SpiceJet/Vistara

Price range: (minimum price is 2,000)

Refundable: True/False

Number of passengers
 
Rule -3: Ignore Other Information: Only focus on the 6 pieces of information mentioned above. Ignore all other details, including departure city, destination city, and travel date.
 
Rule -4: JSON Response Format: Return extracted details in JSON format. Include only the keys with corresponding values. Do not include keys without values.
 
Rule -5: Multiple Message Handling: If a user provides any of the above details in a previous message, keep that information in mind for subsequent messages. Even if the user doesn't provide any new information, continue to include the details from prior messages in the JSON response.
 
Rule -6: No User Prompts: Do not prompt the user for additional information. Only respond based on the user's input.
 
Rule -7: Example Conversations: Here are some examples of how to respond to user queries and extract information:
 
Hello, How can I help you ?

user: Book a economy class flight to Delhi

Assistant: {

  "Class": "Economy"

}

user: Mumbai, 9th June

Assistant: {

  "Class": "Economy"

}

user: Bye

Have a happy and calm Journey!

 

example-1:

Hello, How can I help you ?

user: book a first class ticket to delhi

Assistant: {
  "Class": "first class"
}

user: Mumbai, 9th November, Vistara Airlines

Assistant: {
  "Class": "first class",
  "Airlines": "Vistara"
}

user: bye

example-2:

Hello, How can I help you ?

user: Book a flight from Delhi

Assistant: { }

user: Mumbai, economy class

Assistant: {
  "Class": "economy"
}

You: Coming sunday

Assistant: {
  "Class": "economy"
}

user: Bye

 

example-3:

Hello, How can I help you ?

user: book a business class ticket to goa

Assistant: {

  "Class": "Business"

}

user: mumbai on 10th september

Assistant: {

  "Class": "Business"

}

user: bye

example-4:

Hello, How can I help you ?

user: Goa to London

Assistant: { }

user: business class, 9th November

Assistant: {
  "Class": "business"
}
user: bye

Rule -8: No Default Values: Extract information only from user input; do not ever use any default value for any key or information.
 
Rule -9: Clear JSON: Return extracted information only in JSON format with proper key-value pairs. Do not include keys with blank or None values.
'''


def chat_with_flight_booking_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

def chat_with_bot_non_mandatory(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

def get_travel_date(user_input):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    try:
        date_obj = parser.parse(user_input, fuzzy=False)

        if (date_obj.year < today.year) or (date_obj.year == today.year and date_obj.month < today.month) or (date_obj.year == today.year and date_obj.month == today.month and date_obj.day < today.day):

            date_obj = date_obj.replace(year=today.year + 1)  # Adjust the year to the next year

        return date_obj.strftime("%Y/%m/%d")
    except ValueError:
        return None

#function to combine both the bots JSON response
def extract_dictionary_from_string(s):
    start_index = s.find('{')
    end_index = s.rfind('}') + 1
    dictionary_string = s[start_index:end_index]
    # dictionary = json.loads(dictionary_string)
    return dictionary_string
def extract_resp(s):
    if(s.find('Here is your updated JSON:')!=-1):
      start_index = s.find('Here is your updated JSON:')
      end_index = s.rfind('}') + 1
      dictionary_string1 = s[0:start_index] 
      dictionary_string2=s[end_index:]
      dictionary_string=dictionary_string1+dictionary_string2
      return dictionary_string
    else:
        return s

intent_bot_instructions = '''You're working as a intent classifier. Your duty is to understand the intent of user's input and carry forward the conversation according to following rules:
Rule - 1: There are two different bots for 2 different intents which will be working based on your response, one of the bot handles all flight bookings related query and second bot handles all other types of query.
Rule - 2: If you find the intent of the user's input as flight related query or anything related to flight, then just return a single word "flight", nothing other than that.
Rule - 3: If you find the intent of the user's input as anything other than flight related, then juist return a single word "non-flight", nothing other than that.
'''


def additional_instructions(extracted_json):
  additional_instructions = f'''Remember, as a Flight Booking Assistant, your primary focus is to assist with flight booking and flight booking-related questions. If the user asks non-flight booking-related questions, kindly ask them to rephrase the query to be flight booking-related.
  Today's date is ```{live_date}```.

  Tomorrow's date is just the next date of ```{live_date}```.

  

  - To accomplish this task, follow the following steps sequentially:

  

  ```

  Step 1: Analyze the user input and extract features for the keys mentioned in ```{extracted_json}``` and update it in ```{extracted_json}```.\

  

  Step 1: Next, check for keys with missing values in ```{extracted_json}``` and ask the user for that value. \

  

  Step 2: Respond the user with query to provide the value for keys having missing values in ```{extracted_json}```\

  Along with the query also provide this updated JSON. \

  

  Step 3: From the user input extract the features required to fill the corresponding values of ```{extracted_json}```, and update the JSON with information provided by user.\

  

  Step 4: Again check the updated JSON for missing values and respond with the query to ask for value of remaining keys, along with the updated JSON.\

  

  ```

  

  - Repeat the above steps until all the values of JSON are filled. Once all the values of JSON are filled, your task is done.\

  

  - Don't ask for any other information/features from the user. Extract the information (departure city, destination city and travel date only) from user input and update the JSON with extracted feature every time.\

  

  - Remeber to always respond with the updated JSON and query.\

  

  - If the user provides any extra information like class, trip type, price, no. of passengers, airlines etc. ignore all the other informations and strictly focus on only the 3 values (departure city, destination city and travel date) required to fill JSON.\

  

  - Never ask the user for values that are already filled in ```{extracted_json}```. You must refer and check ```{extracted_json}``` properly before asking user for the values and also while extracting values from user input.\

  

  - Please perform the feature extraction properly with 100% efficiency. For getting departure city and destination city focus on "to" and "from" and also analyze properly with your intelligence in all possible manners. Don't dissapoint user by asking again the already provided information.\

  

  - Please refer the examples below for better understanding:

  

  ```

  example 1:

  

  ```

  <User>: Book a flight to Delhi

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  

  1. Departure city?

  2. Travel date?

  

  Here is your updated JSON:

  {{

    'Departure City': ' ',

    'Destination City': 'Delhi',

    'Travel Date': ' '

  }}

  

  <User>: From Mumbai on 9th June

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  {{

    'Departure City': 'Mumbai',

    'Destination City': 'Delhi',

    'Travel Date': '2024-06-09'

  }}

  ```

  example-2:

  ```

  <User>: Book a flight to Delhi for tomorrow

  

  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:

  

  1. Departure city

  

  Here is your updated JSON:

  {{

      "Departure City": "",

      "Destination City": "Delhi",

      "Travel Date": "2023-09-14"

  }}

  

  <User>: From London

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  Here is your updated JSON:

  {{

    "Departure City": "London",

    "Destination City": "Delhi",

    "Travel Date": "2023-09-14"

  }}

  ```

  example-3:

  ```

  <User>: Book a flight from London to Mumbai on 11th June

  

  <Flight Booking Assistant>: Thank you for providing the information. Here is your updated JSON:

  

  {{

    "Departure City": "London",

    "Destination City": "Mumbai",

    "Travel Date": "2024-06-11"

  }}

  ```

  
  - Strictly avoid the following manner of conversation, you must analyze the user input carefully and update ```{extracted_json}``` before asking user for further information:

  

  ```

  <User>: Book a flight from Delhi to Mumbai for 11th December
  
  <Flight Booking Assistant>: Sure, I can assist you with that. Could you please provide me with the following information:
  
  1. Departure city?
  
  Here is your updated JSON:

  {{

    "Departure City": "",

    "Destination City": "Mumbai",

    "Travel Date": "2023-12-11"

  }}

  <User>: Already provided
  
  <Flight Booking Assistant>: Apologies for the confusion. Let's proceed with your flight booking.

  Here is your updated json:

  {{

    "Departure City": "Delhi",

    "Destination City": "Mumbai",

    "Travel Date": "2023-12-11"

  }}

  ```

  It's clearly understandable that user already provided Delhi as Departure city in the very first message, still you failed to extract that and asked it again from user. It must be strictly avoided. Do the feature extraction properly, focus on user input.\

  

  '''
  return additional_instructions
#intent classifier bot
def intent_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

intent_bot_msg = [
        {"role": "system", "content": intent_bot_instructions}
    ]

greetings_bot_instructions = "Your task is to keep the user engaged in a small talk"

#small talk/greetings bot
def greetings_bot(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    bot_response = response["choices"][0]["message"]["content"]
    return bot_response.strip()

greetings_bot_msg = [
        {"role": "system", "content": greetings_bot_instructions}
    ]

def main(user_input,last2,extracted_json,session_id):
  if user_input.lower() in ["exit", "quit", "bye"]:     
    return ({"response":"Have a happy and calm Journey!",
          "mandatory_json":extracted_json
          })
  print(type(last2))
  intent_bot_response = intent_bot(intent_bot_msg + last2+[{"role": "user", "content": user_input}])
  print("intent suc")


  if intent_bot_response == "non-flight":
    print("non f")
      
    greetings_bot_response = greetings_bot(greetings_bot_msg + last2+[{"role": "user", "content": user_input}])

    return ({
       "response":greetings_bot_response
       })

  else:
      print("flight")
      
      conversation = [
            {"role": "assistant", "content": flight_booking_prompt},
            {"role": "system", "content": additional_instructions(extracted_json)},
        ]

      travel_date = None
      check = ""

      check = check + " " + user_input


      if travel_date == None:
          prompt = flight_booking_prompt + "\nUser: " + user_input
      else:
          prompt = flight_booking_prompt + "\nUser: " + user_input + 'this is the scheduled date for departure:' + travel_date

      bot_response = chat_with_flight_booking_bot(conversation + last2 +[{"role": "system", "content": prompt}])
      print(bot_response)
      print(type(bot_response))
      extracted_data = (extract_dictionary_from_string(bot_response))
      print(extracted_data)
      print(type(extracted_data))

      extracted_json = json.loads(extracted_data)
      print(extracted_json)
      print(type(extracted_json))
      response=extract_resp(bot_response)
      print(response)
      history={"role": "assistant", "content": response}
      db_ses_response(extracted_json,history,session_id)
      return (
        {
          "response":response,
        }
      )

 

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def index():
  print(request.method)
  
  if request.method == "POST":
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
      data = json.loads(request.data)
      session_id=data['session_id']
      user_input= data['prompt']
      bd_ses_append_user(session_id,user_input)
      i=db_ses_fetch(session_id)
      last2=i[1]
      extracted_json=i[0]
      


    else:
      user_input= request.form['prompt']
      session_id="test"
      extracted_json={
            "Departure City":"",
            "Destination City": "",
            "Travel Date": ""
            }
      last2=[
        {
            "content": "book a flight",
            "role": "user"
        },
        {
            "content": "Sure, I can assist you with that. Please provide me with the following details:\n\n1. Departure City\n2. Destination City\n3. Travel Date",
            "role": "assistant"
        }
      ]
    return main(user_input,last2,extracted_json,session_id)
  return render_template("index.html")

     
    

if __name__ == "__main__":
     app.run(debug=True)
