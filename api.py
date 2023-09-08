import openai
import datetime
from dateutil import parser
from datetime import date
import os
from collections import OrderedDict
import json
from flask import Flask, request, render_template

openai.api_key = os.getenv("OPENAI_API_KEY")
def get_todays_date():
    today = date.today()
    return today.strftime("%Y-%m-%d")

live_date = get_todays_date()

flight_booking_prompt = "You are now chatting with the Flight Booking Assistant. Please provide your flight booking details or ask questions related to flight booking."

additional_instructions = f'''Remember, as a Flight Booking Assistant, your primary focus is to assist with flight booking and flight booking-related questions.If the user asks non-flight booking-related questions, kindly ask them to rephrase the query to be flight booking-related.

Today's date is {live_date}.

Please strictly follow the following mentioned rules:

Rule-1: You only need to get the following 3 pieces of information from the user:

1. Departurture City
2. Destination City
3. Travel Date (Today's date is {live_date})

Rule-2: Please strictly follow the following points regarding Travel Date:

Point 1: If a user provides only date and month then instead of asking for complete date, by default consider year as the latest possible year, considering today's date, month and year.
Point 2: Instead of providing exact date, if a user provides travel date as today or tomorrow then accept it and consider date according to today's date.
Point 3: Never ask for complete date.
Point 4: Never ask for time.
Point 5: If no travel date is provided by user, ask the user to provide travel date. Never take any default date as travel date. Please consider the following example for better understanding.

Hello, How can I help you ?
user: Delhi to Mumbai, economy class
Flight Booking Assistant: That's a good choice, what is your scheduled date for departure?
user: 9th November
Flight Booking Assistant: {{
  "Departure City": "Delhi",
  "Destination City": "Mumbai",
  "Travel Date": "2023/11/09"
}}

Rule-3: Analyze properly the user's query, particularly the "to" and from" to decide Departure city and Destination city and check for the above mentioned 3 pieces of information. don't ask the same information again from the user for the already provided information.

Rule-4: If the user enters only one information ask the other two information one by one for example:

user: book a flight from delhi
flight assistant: where are you planning your next trip?
user: mumbai
flight assistant: That's a good choice, what is your scheduled date for departure?
user: 10th december
Flight Booking Assistant: {{
  "Departure City": "Delhi",
  "Destination City": "Mumbai",
  "Travel Date": "2023/12/10"
}}

Rule-5: Understand from the given example how to ask question for information and how to return the response:

example1:
Hello, How can I help you ?
user: book a flight to Delhi on 5th october
Flight Booking Assistant: city of departure?
user: mumbai
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Delhi",
  "Travel Date": "2023/10/05"
}}

example2:
Hello, How can I help you ?
user : book a flight from Mumbai on 23 october
Flight Booking Assistant: what's your choice of destination?
user: goa
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Goa",
  "Travel Date": "2023/10/23"
}}

example3:
Hello, How can I help you ?
user : book a flight from Mumbai to Patna
Flight Booking Assistant: what's your scheduled date of travel?
user: tomorrow
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Patna",
  "Travel Date": "{live_date} + 1"
}}

example4:
Hello, How can I help you ?
user : book a flight from Mumbai to Delhi
Flight Booking Assistant: what's your scheduled date of travel?
user: today
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Goa",
  "Travel Date": "{live_date}"
}}

example5:
Hello, How can I help you ?
user : book a flight from Mumbai to Delhi
Flight Booking Assistant: what's your scheduled date of travel?
user: a day after tomorrow
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Goa",
  "Travel Date": "{live_date} + 2"
}}

example6:
Hello, How can I help you ?
user : book a flight from Mumbai for tomorrow
Flight Booking Assistant: what's your choice of destination?
user: goa
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Goa",
  "Travel Date": "{live_date} + 1"
}}

example7:
Hello, How can I help you ?
user : book a flight from Mumbai for today
Flight Booking Assistant: what's your choice of destination?
user: goa
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Goa",
  "Travel Date": "{live_date}"
}}

example8:
Hello, How can I help you ?
user:  book a flight from Mumbai to Delhi for today
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}"
}}

example9:
Hello, How can I help you ?
user:  book a flight from Pune to Goa for tomorrow
Flight Booking Assistant: {{
  "Departure City": "Pune",
  "Destination City": "Goa",
  "Travel Date": "{live_date}+1"
}}

example10:
Hello, How can I help you ?
user:  Mumbai to Delhi for today
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}"
}}

example11:
Hello, How can I help you ?
user:  Goa to Delhi for tomorrow
Flight Booking Assistant: {{
  "Departure City": "Goa",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}+1"
}}

example12:
Hello, How can I help you ?
user:  Mumbai to Delhi
Flight Booking Assistant: Please provide the scheduled date of travel
user: tomorrow
Flight Booking Assistant: {{
  "Departure City": "Mumbai",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}+1"
}}

example13:
Hello, How can I help you ?
user: will like to book a ticket from delhi day after tomorrow
Flight Booking Assistant: What is your destination city?
user: Goa
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:

{{
  "Departure City": "Delhi",
  "Destination City": "Goa",
  "Travel Date": "{live_date}+2"
}}

example14:
Hello, How can I help you ?
user: book a ticket to goa today
Flight Booking Assistant: What is your departure city?
user: Pune
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Pune",
  "Destination City": "Goa",
  "Travel Date": "{live_date}"
}}

(Don't ask for the date or any other detail again. Travel date is provided as today so consider {live_date}.)

example15:
Hello, How can I help you ?
user: book a ticket to goa on day after tomorrow
Flight Booking Assistant: What is your departure city?
user: Pune
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Pune",
  "Destination City": "Goa",
  "Travel Date": "{live_date}+2"
}}

example16:
Hello, How can I help you ?
user: book a ticket to Mumbai for 3 passengers
Flight Booking Assistant: What is your departure city and travel date?
user: Delhi, today
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Delhi",
  "Destination City": "Mumbai",
  "Travel Date": "{live_date}"
}}

example17:
Hello, How can I help you ?
user: book a ticket from mumbai for tomorrow
Flight Booking Assistant: What is your destination city?
user: Delhi
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Mumbai",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}+1"
}}

example18:
Hello, How can I help you ?
user: book a ticket for tomorrow
Flight Booking Assistant: Sure! I can help you with that. Can you please provide the departure city and the destination city for your flight?
user: Delhi to Goa
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Delhi",
  "Destination City": "Goa",
  "Travel Date": "{live_date}+1"
}}

example19:
Hello, How can I help you ?
user: book a ticket to delhi day after toomorrow
Flight Booking Assistant: What is your departure city?
user: Goa
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Goa",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}+1"
}}

example20:
Hello, How can I help you ?
user: Book a flight to Delhi for tomorrow
Flight Booking Assistant: What is your departure city?
user: Pune in business class
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "Pune",
  "Destination City": "Delhi",
  "Travel Date": "{live_date}+1"
}}

example21:
Hello, How can I help you ?
user: Book a flight to Delhi in business class
Flight Booking Assistant: What is your departure city?
user: London
Flight Booking Assistant: What is your scheduled date of travel ?
user: 12th November
Flight Booking Assistant: Thank you for providing the information. Here are your flight details:
{{
  "Departure City": "London",
  "Destination City": "Delhi",
  "Travel Date": "2023/11/12"
}}

Rule-6: Once you recieve these 3 pieces of information mentioned above, you'll return these 3 pieces of information to user strictly in the form of JSON. Where in the keys of the JSON format would be "Departure City", "Destination City" and "Travel Date" and in the following format:

{{
  "Departurture City": ''
  "Destination City": ''
  "Travel Date":'yyyy/mm/dd'
}}

Rule-7: Don't return the JSON format, if you haven't recieved all the above mentioned 3 mandatory informations. If any of the information is missing, ask it from the user, once you recieve all the 3 informations, then only return the details in JSON. Never ever return blank in JSON format.

Rule-8: You will assist the user's request for booking flight.

Rule-9: If the user provides any extra information like class, trip type, price etc. along with the 3 mandatory informations, ignore all the other informations and strictly focus on only the 3 mandatory informations (departure city, destination city and travel date) to return in JSON format.

Rule-10: Once you returned the JSON format, your job is done. You will not assist further.

'''

instructions_non_mand = '''As a Flight Booking Assistant, your main job is to help users with flight bookings. Follow these guidelines when responding to user queries:

Rule -1: Focus on Flight Booking: Your primary role is to assist with flight booking and flight-related queries. Ignore any non-flight-related questions and do not respond to them.

Rule -2: Extract Specific Information: If the user provides any of the following details, extract and return them in JSON format:

Class: Economy/Premium Economy/Business/First class
Trip type: One-way/Round trip
Number of stops: 0/1/2
Airlines: Air India/AirAsia India/IndiGo/SpiceJet/Vistara
Price range (minimum price is 2,000)
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
Assistant: {}
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
Assistant: {}
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
    dictionary = json.loads(dictionary_string)
    return dictionary

intent_bot_instructions = '''You're working as a intent classifier. Your duty is to understand the intent of user's input and carry forward the conversation according to following rules:
Rule - 1: There are two different bots for 2 different intents which will be working based on your response, one of the bot handles all flight bookings related query and second bot handles all other types of query.
Rule - 2: If you find the intent of the user's input as flight related query or anything related to flight, then just return a single word "flight", nothing other than that.
Rule - 3: If you find the intent of the user's input as anything other than flight related, then juist return a single word "non-flight", nothing other than that.
'''

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

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
      data = json.loads(request.data)
      greet=data['greet']
      conv1=data['conv1']
      conv2=data['conv2']
      last2=data['last2']
      print(type(last2))
      user_input= data['prompt']

    else:
      user_input= request.form['prompt']
      greet=[]
      conv1=[]
      conv2=[]
      last2=[{"content":"book a flight","role":"user"},{"content":"Sure, I can assist you with that. Please provide me with the following details:\n\n1. Departure City\n2. Destination City\n3. Travel Date","role":"assistant"}]
      # user_input = input("User: ")
    flag = 0
    if user_input.lower() in ["exit", "quit", "bye"]:
          greet=[]
          conv1=[]
          conv2=[]
          return ({"response":"Have a happy and calm Journey!",
               "greet":greet,
               "conv1":conv1,
               "conv2":conv2})
    intent_bot_response = intent_bot(intent_bot_msg + last2)

    if intent_bot_response == "non-flight":
      print("non f")
      # print("Hey, what's up ?") #testing
      # while True:



        
      # intent_bot_response1 = intent_bot(intent_bot_msg + [{"role": "system", "content": user_input}])
      # if intent_bot_response1 == 'flight':
      #   flag = 1
        
      greetings_bot_response = greetings_bot(greetings_bot_msg + [{"role": "user", "content": user_input}])
      # greetings_bot_msg.append({"role": "assistant", "content": user_input})
      # user_input = input("User: ")
      greet.append({"role": "user", "content": user_input})
      greet.append({"role": "assistant", "content": greetings_bot_response})
      return ({"response":greetings_bot_response,
               "greet":greet,
               "conv1":conv1,
               "conv2":conv2})

    if (intent_bot_response == "flight") or flag == 1:
        print("flight")

        print("Hello, I'm your flight booking assisant, tell me How can I help you today ?")
        conversation = [
              {"role": "assistant", "content": flight_booking_prompt},
              {"role": "system", "content": additional_instructions},
          ]
        conversation1 = [
            {"role": "system", "content": instructions_non_mand}
        ]
        travel_date = None
        flag = 0
        check = ""

        check = check + " " + user_input
        # print("Here is the check list: " +check)
        
        # if travel_date == None:
        #     travel_date = get_travel_date(user_input)
        # if travel_date and flag != 1:
        #     conversation.append({"role": "user", "content": user_input + " (Travel Date: " + travel_date + ")"})
        #     flag = 1
        # else:
        #     conversation.append({"role": "user", "content": user_input})

        if travel_date == None:
            prompt = flight_booking_prompt + "\nUser: " + user_input
        else:
            prompt = flight_booking_prompt + "\nUser: " + user_input + 'this is the scheduled date for departure:' + travel_date

        bot_response = chat_with_flight_booking_bot(conversation + conv1 +[{"role": "system", "content": prompt}])
        bot_response1 = chat_with_bot_non_mandatory(conversation1 + conv2+[{"role": "system", "content": user_input}])

        mand = [] #refreshing the list each time so as to have only last response i.e. JSON response only in the list
        n_mand = []
        mand.append(bot_response) #storing the JSON response of both the bots

        for entry in bot_response1:
          if 'Destination' in entry:
            entry.pop('Destination')
          if 'Departure Date' in entry:
            entry.pop('Departure Date')
          if 'Departure' in entry:
            entry.pop('Departure')

        n_mand.append(bot_response1)

        # if "{" and "}" in bot_response:
            # print("Here is your search result, Have a happy and calm Journey!")
            # return "Here is your search result, Have a happy and calm Journey!"

        # return ("Flight Booking Assistant:", bot_response)
        # print("Assistant:", bot_response1)
        conv1.append({"role": "user", "content": user_input})
        conv1.append({"role": "assistant", "content": bot_response})
        conv2.append({"role": "assistant", "content": user_input})
        
        if "{" and "}" not in bot_response:
          return ({"response":bot_response,
               "greet":greet,
               "conv1":conv1,
               "conv2":conv2})
        
        
        else:

          a = mand[0] 
          b = n_mand[0]

          lowercase_check = check.lower()
          check_stop = lowercase_check.split()
          

          if "{" and "}" in a:

            c = (extract_dictionary_from_string(a))
            d = (extract_dictionary_from_string(b))


            filtered_data = {key: value for key, value in d.items() if value is not None}

            default_values = {
              "Class": "Economy",
              "Trip type": "One-way",
              "Number of passengers": 1
              }
            if "Class" not in filtered_data:
                filtered_data["Class"] = default_values["Class"]
            if "Trip type" not in filtered_data:
                filtered_data["Trip type"] = default_values["Trip type"]
            if "Number of passengers" not in filtered_data:
                filtered_data["Number of passengers"] = default_values["Number of passengers"]
    
            check_list = ["stop", "halt", "stops", "non-stop", "nonstop", "direct flight", "without layovers"]
    
            if any(item in check_stop for item in check_list):
                # If yes, then don't pop "Number of stops"
                pass
            else:
                # If no, then pop "Number of stops"
                filtered_data.pop("Number of stops", None)

            (c.update(filtered_data))
            print(".............")

            travel_date_str = c['Travel Date']
            travel_date = parser.parse(travel_date_str)

            today_date = datetime.datetime.now().date()

            # Check if the travel date is in the past
            if travel_date.date() < today_date:
                # Update the travel date to next year
                new_travel_date = travel_date.replace(year=travel_date.year + 1)
                c['Travel Date'] = new_travel_date.strftime('%Y/%m/%d')
    #returning merged json
            return ({"response":"Here are your search results",
                "greet":greet,
                "conv1":conv1,
                "conv2":conv2,
                "json":c})
          else:
            return("No responses received.")
  return render_template("index.html")




if __name__ == "__main__":
  app.run(debug=False,host='0.0.0.0')
