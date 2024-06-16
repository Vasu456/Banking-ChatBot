import json
import pyttsx3
import speech_recognition as sr
import streamlit as st
import time
from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
from torch.utils.data import Dataset, DataLoader
import torch
   
import re

save_path = "model"
# Load the saved model and tokenizer
loaded_model = GPT2ForSequenceClassification.from_pretrained(save_path, num_labels=3)
loaded_tokenizer = GPT2Tokenizer.from_pretrained(save_path)

# Example inference using the loaded model and tokenizer
def predict_intent(text):
    inputs = loaded_tokenizer(text, truncation=True, padding=True, max_length=32, return_tensors='pt')
    outputs = loaded_model(**inputs)
    predicted_class = torch.argmax(outputs.logits).item()
    if predicted_class == 0:
        return "User wants to transfer money."
    elif predicted_class == 1:
        return "User wants to get account details."
    elif predicted_class == 2:
        return "User wants to get account balance."
    else:
        return "Unable to determine user's intent."
    
def convert_to_numbers(s):
   
    words_to_numbers = {
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',
        'zero': '0'
    }
 
    pattern = re.compile(r'\b(' + '|'.join(words_to_numbers.keys()) + r')\b')
    return re.sub(pattern, lambda x: words_to_numbers[x.group()], s)
def text_to_speech(text):
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    
    # Set properties (optional)
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)   # Volume (0.0 to 1.0)
    
    # Convert the text to speech and speak it
    engine.say(text)
    
    # Wait for speech to finish
    engine.runAndWait()


def speech_to_text():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        st.write("Recognizing...")
        # Convert speech to text
        user_input = recognizer.recognize_google(audio)
        l = user_input.split(" ")
        if l[0].isdigit():
            user_input = "".join(l)
        st.write("User said:", user_input)
        return user_input
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand what you said.")
    except sr.RequestError as e:
        st.error("Sorry, I couldn't request results. Please check your internet connection.")

# def speech_to_text():
#     # Initialize recognizer
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
        
#         st.write("Listening...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         st.write("Recognizing...")
#         # Convert speech to text
#         user_input = recognizer.recognize_google(audio)
#         st.write("User said:", user_input)
#         return user_input
#     except sr.UnknownValueError:
#         st.error("Sorry, I couldn't understand what you said.")
#     except sr.RequestError as e:
#         st.error("Sorry, I couldn't request results. Please check your internet connection.")

def insert_user(name, account_number, balance):
    # Load existing user data from JSON file
    with open('users.json', 'r') as file:
        users = json.load(file)

    # Append new user data
    new_user = {
        "name": name,
        "account_number": account_number,
        "balance": balance
    }
    st.write(name)
    st.write(balance)
    users.append(new_user)

    # Write updated user data back to JSON file
    with open('users.json', 'w') as file:
        json.dump(users, file)
    
    print("New user added:", new_user)  # Adding print statement for debugging purposes


def get_user(account_numbe):
    # Load existing user data from JSON file
    with open('users.json', 'r') as file:
        users = json.load(file)

    # Find user by account number
    for user in users:
        if user["account_number"] == account_numbe:
            return user

    # Return None if user not found
    return None

def banking_chatbot(existing_user):
    # Introduction
    text_to_speech("Hello, Welcome to Banking Chatbot.")
    
    if existing_user:
        # Ask for existing user details
        text_to_speech("Please enter your account number for authentication.")
        account_numb = speech_to_text()
        time.sleep(5)
        
        # Get user data
        user = get_user(account_numb)
        
        if user:
            # Ask for authentication code
            text_to_speech("Please enter your authentication code.")
            authentication_code = speech_to_text()
            time.sleep(7)
            
            # Dummy authentication check (replace with actual authentication mechanism)
            if authentication_code == "1234":
                text_to_speech("Authentication successful.")
                
                # Present service options to the user
                text_to_speech("I provide three types of services: transfer money, get account details, and get account balance. What type of service do you want?")
                
                # Get user's desired service
                st.write("Please say the service type to proceed.")
                service_type = service_type = predict_intent(speech_to_text())
                
                # Process the service type
                if service_type:
                    if "transfer money" in service_type:
                        text_to_speech("You have chosen to transfer money.")
                        # Ask for recipient account number
                        text_to_speech("Please say the recipient account number.")
                        recipient_account_number = speech_to_text()
                        # Get recipient user data
                        recipient_user = get_user(recipient_account_number)
                        if recipient_user:
                            # Ask for transfer amount
                            text_to_speech("Please say the transfer amount.")
                            transfer_amount = speech_to_text()
                            if transfer_amount:
                                transfer_amount = int(convert_to_numbers(transfer_amount))
                                # Check if the transfer amount is greater than account balance
                                if transfer_amount <= user["balance"]:
                                    # Perform the transaction
                                    user["balance"] -= transfer_amount
                                    recipient_user["balance"] += transfer_amount
                                    # Update user data in JSON file
                                    with open('users.json', 'w') as file:
                                        json.dump(user, file)
                                        json.dump(recipient_user,file)
                                    text_to_speech("Transaction successful.")
                                else:
                                    text_to_speech("Transaction failed. Insufficient balance.")
                            else:
                                text_to_speech("Sorry, I didn't get the transfer amount. Please try again later.")
                        else:
                            text_to_speech("Transaction failed. Recipient account does not exist.")
                    elif "get account details" in service_type:
                        text_to_speech("You have chosen to get account details.")
                        # Retrieve and display account details
                        text_to_speech(f"Name: {user['name']}")
                        text_to_speech(f"Account Number: {user['account_number']}")
                        text_to_speech(f"Account Balance: {user['balance']}")
                    elif "get account balance" in service_type:
                        text_to_speech("You have chosen to get account balance.")
                        # Display account balance
                        text_to_speech(f"Your account balance is {user['balance']}.")
                    else:
                        text_to_speech("Sorry, I couldn't understand your service choice.")
            else:
                text_to_speech("Sorry, authentication failed. Please try again.")
        else:
            text_to_speech("Sorry, the account number provided does not exist.")


# Streamlit app
st.title("Banking Chatbot")
existing_user_voice_input = st.checkbox("Enable Voice Input for Existing User")
if existing_user_voice_input:
    st.write("Please say 'existing user' to proceed.")
    user_option = speech_to_text()
    if user_option:
        if "existing" in user_option:
            banking_chatbot(True)
        else:
            st.error("Invalid input. Please say 'existing user' to proceed.")
else:
    banking_chatbot(True)
