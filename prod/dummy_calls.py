from datetime import datetime, timedelta
from prompt_builder import build_prompt_sonnet
from infer import infer_sonnet
import pytz
import anthropic
from threading import Event

def run_dummy_calls(client: anthropic, start_time_str: str, end_time_str: str, interval_minutes: int, timezone_str: str, stop_event: Event):
    """
    Runs dummy calls to the model between a specified time range with a set interval, ensuring timing in the given time zone.
    Handles shutdown gracefully when the stop_event is set.

    Args:
    client: The Anthropic client object.
    start_time_str: The start time in HH:MM format (24-hour clock) in the given timezone.
    end_time_str: The end time in HH:MM format (24-hour clock) in the given timezone.
    interval_minutes: The interval between calls in minutes.
    timezone_str: The string representing the desired timezone (e.g., 'America/New_York').
    stop_event: A threading event to signal when to stop the thread.
    """
    # Define timezone
    tz = pytz.timezone(timezone_str)

    # Parse start and end times, assuming the given timezone
    start_time = tz.localize(datetime.strptime(start_time_str, "%H:%M"))
    end_time = tz.localize(datetime.strptime(end_time_str, "%H:%M"))

    # Adjust end_time if it's before start_time (indicating next day)
    if end_time <= start_time:
        end_time += timedelta(days=1)

    while not stop_event.is_set():
        now = datetime.now(tz)
        # Check if current time is within the schedule
        if start_time <= now <= end_time:
            dummy_query = "dummy question"
            prompt = build_prompt_sonnet(query=dummy_query)
            prompt["user_query"] = f'''
                {dummy_query}
                If the user's question == "{dummy_query}", respond with "dummy".
            '''

            dummy_response = infer_sonnet(prompt=prompt, client=client)
            for response in dummy_response:
                print(f"Dummy call at {now.strftime('%H:%M:%S %Z')}: {response.text}")

            # Wait for the interval or stop event
            if stop_event.wait(interval_minutes * 60):
                break  # Stop event was set, exit the loop
        else:
            # Calculate the time until the next start time or until the stop_event is set
            next_start = (start_time + timedelta(days=1)) if now.time() > end_time.time() else start_time
            sleep_duration = (next_start - now).total_seconds()

            # Wait for the calculated sleep duration or stop event
            if stop_event.wait(sleep_duration):
                break  # Stop event was set, exit the loop

    # Final task before shutting down
    print("Shutting down run dummy calls")
