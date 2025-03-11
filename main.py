import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
import google_calendar as gc 
import functions as fn 
import voice_reader as vr

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def main(): 
    user_input = vr.record_audio()
    fn.process_calendar_request(user_input) 



if __name__ == "__main__":
    main()