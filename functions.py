from data_structures import * 

from typing import Optional
from openai import OpenAI
import os
import logging
from datetime import datetime
from google_calendar import create_google_calendar_event
from dotenv import load_dotenv

load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"


def route_calendar_request(user_input: str) -> CalendarRequestType:
    """Router LLM call to determine the type of calendar request"""
    logger.info("Routing calendar request")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Determine if this is a request to create a new calendar event or modify an existing one.",
            },
            {"role": "user", "content": user_input},
        ],
        response_format=CalendarRequestType,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Request routed as: {result.request_type} with confidence: {result.confidence_score}"
    )
    return result


def handle_new_event(description: str) -> CalendarResponse:
    """Process a new event request"""
    logger.info("Processing new event request")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."


    # Get event details
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract details for creating a new calendar event. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {"role": "user", "content": description},
        ],
        response_format=NewEventDetails,
    )
    details = completion.choices[0].message.parsed
    event = details.model_dump()
    logger.info(f"New event: {details.model_dump_json(indent=2)}")

    created = create_google_calendar_event(
        summary = event['name'], 
        description = "Scheduled by Martin's AIssistant",
        start_time= event['date'],
        duration= event['duration_minutes'],
        attendees= event['participants']
    )

    # Generate response
    return CalendarResponse(
        success=True,
        message=f"Created new event '{details.name}' for {details.date} with {', '.join(details.participants)}",
        calendar_link=f"{created['event_link']}",
        meet_link=f"{created['meet_link']}"
    )

def handle_modify_event(description: str) -> CalendarResponse:
    """Process an event modification request"""
    logger.info("Processing event modification request")

    # Get modification details
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Extract details for modifying an existing calendar event.",
            },
            {"role": "user", "content": description},
        ],
        response_format=ModifyEventDetails,
    )
    details = completion.choices[0].message.parsed

    logger.info(f"Modified event: {details.model_dump_json(indent=2)}")

    # Generate response
    return CalendarResponse(
        success=True,
        message=f"Modified event '{details.event_identifier}' with the requested changes",
        calendar_link=f"calendar://modify?event={details.event_identifier}",
    )

def process_calendar_request(user_input: str) -> Optional[CalendarResponse]:
    """Main function implementing the routing workflow"""
    logger.info("Processing calendar request")

    # Route the request
    route_result = route_calendar_request(user_input)

    # Check confidence threshold
    if route_result.confidence_score < 0.7:
        logger.warning(f"Low confidence score: {route_result.confidence_score}")
        return None

    # Route to appropriate handler
    if route_result.request_type == "new_event":
        return handle_new_event(route_result.description)
    elif route_result.request_type == "modify_event":
        return handle_modify_event(route_result.description)
    else:
        logger.warning("Request type not supported")
        return None