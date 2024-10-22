import json
import itertools

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

  # handle the fact that the buffer might have something left over if the loop exits from the not collecting state
  #(this can happen only if the collection done flag is not True -- meaning, the start marker is not found, or the end marker is not found even though the start marker
  # has been found)
  if buffer:
    yield buffer
    buffer = ""

def parse_streaming_response(response):
    file_path = './section_article_map.json'

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
        with open(file_path, 'r') as json_file:
            map_obj = json.load(json_file)

        # map article name with slugs -- handle keyerror exceptions
        try:
            relevant_articles = {
                "relevant_articles": list(map(lambda x: map_obj[x], list(filter(lambda x: not(x == "Article: No Article"), relevant_articles))))
            }
        except Exception:
            relevant_articles["relevant_articles"] = []
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