from langchain_google_community import GmailToolkit 
from langchain_google_community import CalendarToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service as build_gmail_service,
    get_gmail_credentials,
)
from langchain_google_community.calendar.utils import (
    build_calendar_service,
)
from langchain_core.tools import tool
from typing import Any

def get_tools():
    """
    Get Gmail and Calendar tools from toolkits.
    Returns all tools from Gmail and Calendar toolkits.
    """
    try:
        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=[
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/calendar"
            ],
            client_sercret_file="credentials.json",
        )
        
        # Build separate service resources for Gmail and Calendar
        gmail_resource = build_gmail_service(credentials=credentials)
        calendar_resource = build_calendar_service(credentials=credentials)
        
        gmail_toolkit = GmailToolkit(api_resource=gmail_resource)
        calendar_toolkit = CalendarToolkit(api_resource=calendar_resource)

        # Get all tools from both toolkits
        gmail_tools = gmail_toolkit.get_tools()
        calendar_tools = calendar_toolkit.get_tools()

        # Filter out problematic tools
        essential_tools = []
        
        # Add Gmail tools
        for tool in gmail_tools:
            if tool.name in ["send_gmail_message", "create_gmail_draft"]:
                essential_tools.append(tool)
        
        # Add Calendar tools (excluding get_current_datetime which causes SSL issues)
        for tool in calendar_tools:
            if tool.name in ["create_calendar_event", "search_events", "get_calendars_info"]:
                essential_tools.append(tool)
        
        all_tools = essential_tools
        
        print(f"Loaded {len(all_tools)} tools: {[t.name for t in all_tools]}")
        return all_tools
        
    except Exception as e:
        print(f"Error getting tools: {e}")
        return []


def get_my_own_tools():
    """
    Return simplified, custom-wrapped tools for:
    - sending emails
    - creating calendar events
    - searching calendar events (auto-fetches calendars info)
    """
    try:
        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=[
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/calendar",
            ],
            client_sercret_file="credentials.json",
        )

        gmail_resource = build_gmail_service(credentials=credentials)
        calendar_resource = build_calendar_service(credentials=credentials)

        gmail_toolkit = GmailToolkit(api_resource=gmail_resource)
        calendar_toolkit = CalendarToolkit(api_resource=calendar_resource)

        gmail_tools = {t.name: t for t in gmail_toolkit.get_tools()}
        cal_tools = {t.name: t for t in calendar_toolkit.get_tools()}

        send_tool = gmail_tools.get("send_gmail_message") or gmail_tools.get("gmail_send_message")
        create_event_tool = cal_tools.get("create_calendar_event")
        search_events_tool = cal_tools.get("search_events")
        get_cals_info_tool = cal_tools.get("get_calendars_info")


        @tool
        def create_calendar_event_ist(
            summary: str,
            start_datetime: str,
            end_datetime: str,
            location: str = "",
            attendees: str = "",
            description: str = "",
            send_notifications: bool = True,
            conference_data: bool = True,
        ) -> str:
            """
            Create a calendar event in IST timezone with Google Meet link and guest notifications.
            Datetimes as 'YYYY-MM-DD HH:MM:SS' (e.g., '2025-10-28 16:00:00' for 4:00 PM IST).
            """
            if not create_event_tool:
                return "create_calendar_event tool not available"
            
            payload: dict[str, Any] = {
                "summary": summary,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "timezone": "Asia/Kolkata",  # IST timezone
                "send_notifications": send_notifications,  # Notify guests
            }
            
            if location:
                payload["location"] = location
            if attendees:
                # Toolkit expects attendees as list of email strings
                payload["attendees"] = [e.strip() for e in attendees.split(",") if e.strip()]
            if description:
                payload["description"] = description
            
            # Enable Google Meet via boolean flag per tool schema
            if conference_data:
                payload["conference_data"] = True
            
            try:
                result = create_event_tool.invoke(payload)
                return f"Event created with Google Meet link and guest notifications: {result}"
            except Exception as e:
                return f"Error creating event: {e}"

        @tool
        def search_calendar_events(
            min_datetime: str,
            max_datetime: str,
            timezone: str = "Asia/Kolkata",
        ) -> str:
            """
            Search events between min_datetime and max_datetime.
            Datetimes as 'YYYY-MM-DD HH:MM:SS' (e.g., '2025-10-28 14:30:00').
            Defaults to IST timezone.
            """
            if not search_events_tool or not get_cals_info_tool:
                return "search_events or get_calendars_info tool not available"
            try:
                calendars_info = get_cals_info_tool.invoke({})
                if calendars_info:
                    payload = {
                        "min_datetime": min_datetime,
                        "max_datetime": max_datetime,
                        "timezone": timezone,
                        "calendars_info": calendars_info,
                    }
                    result = search_events_tool.invoke(payload)
                    return f"Events: {result}"
                else:
                    return "No calendars info found"
            except Exception as e:
                return f"Error searching events: {e}"

        return [send_tool, create_calendar_event_ist, search_calendar_events]

    except Exception as e:
        print(f"Error building custom tools: {e}")
        return []