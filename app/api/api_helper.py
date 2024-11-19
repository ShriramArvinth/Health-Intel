from typing import List
from app.response_retriever import response_retriever
import json
import itertools
import re
import random

def handle_streaming_response(response):
  collecting = False  # Flag to track if we're between the start and end markers
  collected_text = ""  # To store lines between the markers
  buffer = ""  # To store leftover text that may contain partial markers

  start_marker = "#####relevant articles begin"
  end_marker = "#####relevant articles end"
  max_marker_length = max(len(start_marker), len(end_marker))
  collection_done_flag = False

  for chunk in response:
      buffer += chunk  # Add the new chunk to the buffer

      if not collection_done_flag:

        if not collecting:
            index = buffer.find(start_marker)

            if index != -1:
                collecting = True

                # dont yield if buffer is empty
                if (buffer[:index]):
                  yield buffer[:index] # print(buffer[:index])
                else:
                  pass
                buffer = buffer[index + len(start_marker):] # buffer is cutting everything before and including "#####relevant articles begin" it has chance to be empty here
            else:
                if len(buffer) > max_marker_length:

                    # eg: (123456######relevant articles beg)
                    safe_output = buffer[:-max_marker_length]
                    yield safe_output # print(safe_output, end="")

                    # eg: (3456######relevant artiles beg)
                    buffer = buffer[-max_marker_length:]
        else:
            index = buffer.find(end_marker)

            if index != -1:
                collected_text += buffer[:index]
                buffer = buffer[index + len(end_marker):] # buffer is cutting everything before and including "#####relevant articles end" it has chance to be empty here
                collecting = False

                # set the state to print the collected text, and proceed normally
                collection_done_flag = True
                yield "$relevant_articles_begin$"
                yield collected_text.strip("\n") # print(collected_text)
                yield "$relevant_articles_end$"
                if buffer: # handle buffer empty case
                  yield buffer # print(buffer, end = "")
                else:
                  pass
                buffer = "" # clean buffer

            else:
                if len(buffer) > max_marker_length:
                    collected_text += buffer[:-max_marker_length]
                    buffer = buffer[-max_marker_length:]
      else:
        yield buffer # print(buffer, end = "")
        buffer = "" # clean buffer

  # handle the fact that the buffer might have something left over if the loop exits from inside the not collecting "if condition"
  #(this can happen only if the collection done flag is not True -- meaning, the start marker is not found, or, the end marker is not found even though the start marker
  # has been found)
  if buffer:
    yield buffer
    buffer = ""

def parse_streaming_response(response):
    parsed_stream = handle_streaming_response(response = response)
    first_chunk = next(parsed_stream)
    question_exception = False

    start_marker = "$relevant_articles_begin$"
    relevant_articles = []
    if start_marker not in first_chunk:
        question_exception = True

    if question_exception:
        parsed_stream = itertools.chain([first_chunk], parsed_stream)
    else:
        relevant_articles = next(parsed_stream).split("\n")
        relevant_articles = {
            "relevant_articles": list(filter(lambda x: not(x in ["", "articles/no-article"]), relevant_articles))
        }
        if relevant_articles["relevant_articles"]:
            yield first_chunk # start marker "$relevant_articles_begin$"
            yield json.dumps(relevant_articles) # json.dumps() is needed here as everything in streaming response should be in string format. But in normal responses, json.dumps() is not needed.
            yield next(parsed_stream) # end marker "$relevant_articles_end$"
        else:
            next(parsed_stream) # end marker "$relevant_articles_end$"

        # handle \n at the start of the answer
        answer_first_chunk = next(parsed_stream)
        answer_first_chunk = answer_first_chunk.lstrip()
        parsed_stream = itertools.chain([answer_first_chunk], parsed_stream)
    
    for _ in parsed_stream:
        yield(_)

def ask_query_helper(all_queries: List[str], startup_variables, specialty):
    anthropic_client = startup_variables["anthropic_client"]

    ans_ref_stream = response_retriever.ans_ref(
        anthropic_client = anthropic_client,
        all_prompts = startup_variables["global_resources"],
        query = all_queries[-1],
        specialty = specialty
    )
    parsed_stream = parse_streaming_response(response = ans_ref_stream)

    ans = ""
    chunk_flag = True
    for chunk in parsed_stream:
        if "$relevant_articles_begin$" in chunk:
            chunk_flag = not(chunk_flag)
        elif "$relevant_articles_end$" in chunk:
            chunk_flag = not(chunk_flag)
        if chunk_flag:
            ans += re.sub(r'\$.*?\$', '', chunk)
        # print(chunk, end = "")
        # print('\n')
        yield chunk

    yield "$end_of_answer_stream$"


    followup_questions = response_retriever.followup(
       anthropic_client = anthropic_client,
       all_prompts = startup_variables["global_resources"],
       last_question = all_queries[-1], 
       last_answer = ans
    )
    yield followup_questions

    # return chat title, if its the first question in the chat window
    if(len(all_queries) == 1):
        yield "$end_of_followup_stream$"
        chat_title = response_retriever.chat_title(
            anthropic_client = anthropic_client,
            all_prompts = startup_variables["global_resources"],
            first_question = all_queries[0], 
        )
        yield chat_title

def generate_dummy_response_for_testing(all_prompts, specialty):
    json_data = getattr(all_prompts, specialty).pre_def_response

    for key in json_data.keys():
        yield json_data[key]