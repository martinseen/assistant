import os
from openai import OpenAI
import functions as fn 
import voice_reader as vr
from dotenv import load_dotenv

# Set the current working directory to the folder that main.py is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main(): 
    user_input = vr.record_audio()
    print(f"You said: {user_input}")
    # user_input = "Schedule a meeting with Martin and Martin Mailsoar and Dude at 2pm the day after tomorrow that lasts 45 minutes and it's called 'Brainstorming'"
    response = fn.process_calendar_request(user_input) 
    print(response) 

if __name__ == "__main__":
    main()