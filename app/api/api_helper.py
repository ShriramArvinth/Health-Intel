from typing import List
import json
import itertools
import re
import random

from app.response_retriever.src import response_retriever
from app.api.api_init import (
    global_resources,
    specialty as spc
)

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
            "relevant_articles": list(filter(lambda x: not(x in ["", "articles/no-article"]), relevant_articles))[:3]
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
       last_answer = ans,
       specialty = specialty
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

def generate_dummy_response_for_testing(all_prompts: global_resources, specialty: str, all_queries: List[str]):
   
    # specialty specific data inside global_resources
    if specialty in ["wld", "t1d", "gerd"]:
        specialty_obj: spc = getattr(all_prompts, specialty)
        json_data = specialty_obj.pre_def_response
    else:
        query_length = len(all_queries)

        if specialty == "rx_next":
            json_data_list = [
                {
                    "actual_answer": "Vyalev delivers continuous 24-hour relief via subcutaneous infusion. Chat with our bot for quick insights into its clinical benefits.",
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [\n    \"What are the key highlights of the FDA-approved drugs in August 2024?\",\n    \"Which FDA-approved drug is making headlines for advanced breast cancer treatment?\",\n    \"What's the newest biosimilar for autoimmune conditions like psoriasis?\"\n  ],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq RxNext - AI Agent for Latest FDA Updates"
                },
                {
                    "actual_answer": "By mapping FDA-approved treatments to patient conditions, our chatbot equips HCPs with tailored options in seconds.",
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [\n    \"What are the key highlights of the FDA-approved drugs in August 2024?\",\n    \"Which FDA-approved drug is making headlines for advanced breast cancer treatment?\",\n    \"What's the newest biosimilar for autoimmune conditions like psoriasis?\"\n  ],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq RxNext - AI Agent for Latest FDA Updates"
                },
                {
                    "actual_answer": "It's the first FDA-approved abuse-deterrent immediate-release Oxycodone formulation.",
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [\n    \"What are the key highlights of the FDA-approved drugs in August 2024?\",\n    \"Which FDA-approved drug is making headlines for advanced breast cancer treatment?\",\n    \"What's the newest biosimilar for autoimmune conditions like psoriasis?\"\n  ],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq RxNext - AI Agent for Latest FDA Updates"
                },
                {
                    "actual_answer": "In October 2024, the FDA approved several notable drugs, including Itovebi ( Inavolisib) and Scemblix (Asciminib), each projected to achieve peak sales exceeding $2 billion.",
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [\n    \"What are the key highlights of the FDA-approved drugs in August 2024?\",\n    \"Which FDA-approved drug is making headlines for advanced breast cancer treatment?\",\n    \"What's the newest biosimilar for autoimmune conditions like psoriasis?\"\n  ],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq RxNext - AI Agent for Latest FDA Updates"
                }
            ]
            json_data_list_length = len(json_data_list)

            if (query_length % json_data_list_length) == 1:
                json_data = json_data_list[0]
            elif (query_length % json_data_list_length) == 2:
                json_data = json_data_list[1]
            elif (query_length % json_data_list_length) == 3:
                json_data = json_data_list[2]
            elif (query_length % json_data_list_length) == 0:
                json_data = json_data_list[3]

        elif specialty == "empower":
            json_data = {
                "actual_answer": str('Understood. Let\'s make sure you ask all the key questions to get the most out of your consultation. We\'ll cover your symptoms, treatment adjustments, and overall care plan.  \n\n**1. Understanding Your Diagnosis**\n\n - What does metastatic prostate cancer mean in my case?\n - How far has the cancer spread, and what are the implications?\n - Are there specific tests or scans I should undergo to understand my condition better?\n\n**2. Exploring Treatment Options**\n\n- What are the recommended treatments for metastatic prostate cancer?\n- Can you explain how Xtandi works and its role in my treatment plan?\n- Are there alternative medications or therapies I should consider?\n- How does this treatment compare to others in terms of effectiveness and side effects?\n\n**3. Managing Side Effects**\n\n-   What are the common side effects of Xtandi, and how can I manage them?\n-   Will Xtandi affect my energy levels, appetite, or overall quality of life?\n-   Are there specific symptoms or side effects I should report immediately?\n\n**4. Treatment Monitoring and Progress**\n\n-   How will we track the effectiveness of Xtandi during treatment?\n-   What follow-up tests or appointments will I need?\n-   How will I know if the treatment is working or if adjustments are needed?\n\n**5. Impact on Daily Life**\n\n-   Will Xtandi affect my ability to work, exercise, or engage in other activities?\n-   Are there dietary or lifestyle changes I should make while on this treatment?\n-   How can I balance treatment with maintaining my mental and emotional well-being?\n\n**6. Family and Genetic Considerations**\n\n-   Should my family members be screened for prostate cancer risks?\n-   Are there genetic factors I should consider for my children or relatives?\n-   How can I involve my family in understanding and supporting my treatment?\n\n**7. Financial and Logistical Questions**\n\n-   What is the cost of Xtandi, and will my insurance cover it?\n-   Are there financial assistance programs available for this treatment?\n-   Where and how will I receive the medication? Is it a daily oral pill or something else?\n\n**8. Preparing for Long-Term Care**\n\n-   What does my long-term care plan look like for metastatic prostate cancer?\n-   Are there clinical trials or new treatments I should be aware of?\n-   What can I expect in terms of overall prognosis with this treatment?\n\n**9. Emotional Support and Resources**\n\n-   What support resources are available for patients with metastatic prostate cancer?\n-   Can you recommend any counseling services, patient groups, or online forums?\n-   How can I stay positive and motivated during treatment?\n\n**10. Next Steps**\n\n-   What should I do next to get started on this treatment?\n-   Can I have written materials or trusted online resources to review?\n-   When should we meet next to discuss progress or any new developments?\n\nWrite these questions down or save them to your phone. During your appointment, make sure to bring up all your concerns so the doctor can provide the best guidance. After your consultation, let us know if you\'d like help updating your case history or tracking your progress!'),
                "end_of_answer_stream": "$end_of_answer_stream$",
                "followup_questions": "'{\n  \"questions\": [],\n  \"askDoctorOnline\": false\n}'",
                "end_of_followup_stream": "$end_of_followup_stream$",
                "chat title": "iCliniq Empower: AI powered Doctor Discussion Guide"
            }

        elif specialty == "med_prep":
            json_data_list = [
                {
                    "actual_answer": str('A 32-year-old biologically female patient presents to the primary care office for an initial visit after learning she is HIV-positive from a screening test. Which of the following is the most appropriate next step in management?\n\n**Option (A)**\nInitiate antiretroviral therapy immediately\n\n---\n\n**Option (B)**\nPerform a confirmatory HIV test\n\n---\n\n**Option \\(C\\)**\nSchedule a follow-up visit in six months\n\n---\n\n**Option (D)**\nAdvise the patient to inform all previous sexual partners.'),
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq MedPrep: AI Powered Training for Physicians"
                },
                {
                    "actual_answer": str('The correct answer is Option (B) Perform a confirmatory HIV test.\n\nAfter a positive HIV screening test, it is essential to perform a confirmatory test to establish the diagnosis before initiating treatment.\n\nA 60-year-old male with a history of type 2 diabetes and hypertension presents with worsening renal function. His current medications include metformin and lisinopril. Which of the following is the most appropriate next step in management?\n\n**Option (A)**\nDiscontinue metformin\n___\n**Option (B)**\nIncrease the dose of lisinopril\n___\n**Option \\(C\\)**\nAdd a thiazide diuretic\n___\n**Option (D)**\nRefer for renal biopsy'),
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq MedPrep: AI Powered Training for Physicians"
                },
                {
                    "actual_answer": str('The correct answer is Option (A) Discontinue metformin.\n\nMetformin is contraindicated in patients with significant renal impairment due to the risk of lactic acidosis. Discontinuing metformin is appropriate in this scenario.\n\nA 68-year-old male with a history of heavy smoking presents with newly diagnosed stage IIIB non-small cell lung cancer (NSCLC). Molecular profiling reveals PD-L1 expression in 60% of tumor cells, and there are no actionable EGFR mutations or ALK rearrangements. Which of the following treatment regimens is most appropriate for this patient according to current guidelines?\n\n**Option (A)**\nCisplatin and pemetrexed\n___\n**Option (B)**\nCarboplatin and paclitaxel\n___\n**Option \\(C\\)**\nKeytruda (pembrolizumab) combined with platinum-doublet chemotherapy\n___\n**Option (D)** \nErlotinib monotherapy'),
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq MedPrep: AI Powered Training for Physicians"                
                },
                {
                    "actual_answer": str('The correct answer is Option (C) Keytruda (pembrolizumab) combined with platinum-doublet chemotherapy.\n\nFor stage IIIB NSCLC with high PD-L1 expression (≥50%) and no EGFR mutations or ALK rearrangements, the recommended treatment is the combination of pembrolizumab (Keytruda) with platinum-doublet chemotherapy. This regimen has shown improved overall survival compared to chemotherapy alone in such patients.'),
                    "end_of_answer_stream": "$end_of_answer_stream$",
                    "followup_questions": "'{\n  \"questions\": [],\n  \"askDoctorOnline\": false\n}'",
                    "end_of_followup_stream": "$end_of_followup_stream$",
                    "chat title": "iCliniq MedPrep: AI Powered Training for Physicians"                 
                }
            ]

            json_data_list_length = len(json_data_list)

            if (query_length % json_data_list_length) == 1:
                json_data = json_data_list[0]
            elif (query_length % json_data_list_length) == 2:
                json_data = json_data_list[1]
            elif (query_length % json_data_list_length) == 3:
                json_data = json_data_list[2]
            elif (query_length % json_data_list_length) == 0:
                json_data = json_data_list[3]
                            

    for key in json_data.keys():
        yield json_data[key]