from datetime import datetime, timedelta
from prompt_builder import build_prompt_sonnet
from infer import infer_sonnet
import pytz
from typing import Generator
from threading import Event

def run_dummy_calls(client, start_time_str, end_time_str, interval_minutes, timezone_str, stop_event):
    """
    Runs dummy calls to the model between a specified time range with a set interval, ensuring timing in the given time zone.
    Handles shutdown gracefully when the stop_event is set.

    Args:
        client: The Anthropic client object.
        start_time_str: The start time in HH:MM format (24-hour clock) in the given timezone.
        end_time_str: The end time in HH:MM format (24-hour clock) in the given timezone.
        interval_minutes: The interval between calls in minutes.
        timezone_str: The string representing the desired timezone.
        stop_event: A threading event to signal when to stop the thread.
    """
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)
    today = now.date()
    
    start_time = tz.localize(datetime.combine(today, datetime.strptime(start_time_str, "%H:%M").time()))
    end_time = tz.localize(datetime.combine(today, datetime.strptime(end_time_str, "%H:%M").time()))
    
    if end_time <= start_time:
        end_time += timedelta(days=1)  # Handles end time crossing midnight
    
    while not stop_event.is_set():
        now = datetime.now(tz)
        if start_time <= now <= end_time:
            dummy_response = make_dummy_call(client=client)
            for response in dummy_response:
                print(f"Dummy call at {now.strftime('%H:%M:%S %Z')}: {response}")

            if stop_event.wait(interval_minutes * 60):
                break  # Stop event was set, exit the loop
        else:
            # Calculate time until the next start_time
            next_start = start_time + timedelta(days=1) if now > end_time else start_time
            sleep_duration = (next_start - now).total_seconds()
            if sleep_duration > 0:
                if stop_event.wait(sleep_duration):
                    break  # Stop event was set, exit the loop
            else:
                # This handles cases where sleep_duration is negative
                if stop_event.wait(interval_minutes * 60):
                    break
    print("Shutting down run dummy calls")


def make_dummy_call(client) -> Generator:
    dummy_query = "dummy question"
    prompt = build_prompt_sonnet(query=dummy_query)
    prompt["user_query"]["user_question"] = f'''
        {dummy_query}
        If the user's question == "{dummy_query}", respond with "dummy".
    '''
    dummy_response = infer_sonnet(prompt=prompt, client=client)
    return dummy_response    