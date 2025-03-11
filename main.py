import json
import os
import requests
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))