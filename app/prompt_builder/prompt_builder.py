from textwrap import dedent

# another function to define the sources paths (knowledge source, system prompt, user prompt ..)

def ans_ref_prompts(query: str):

    # book data
    knowlege_source_file_path = '../datasource/Google_docs_extract_data.txt'
    with open(knowlege_source_file_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    book_data = ''.join(lines)

    # system
    system_prompt_path = '../prompt_builder/prompts/wld/ans_ref_sys_prompt.txt'
    with open(system_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    system_prompt = ''.join(lines)

    # user
    user_prompt_path = '../prompt_builder/prompts/wld/ans_ref_usr_prompt.txt'
    with open(user_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    user_prompt = {
        "instructions": ''.join(lines),
        "user_question": dedent(f'''
            -> User's Question:
            {query}
        ''').strip("\n")
    }

    return_obj = {
        "system_prompt": system_prompt,
        "user_query": user_prompt,
        "book_data": book_data
    }

    return return_obj

def followup_prompts(last_question: str, last_answer: str):

    # system
    system_prompt_path = '../prompt_builder/prompts/follow_up.txt'
    with open(system_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    system_prompt = ''.join(lines)

    # user
    user_prompt = dedent(f'''
        This is the last question the user has asked:
        {last_question}

        This is the answer provided for that question:
        {last_answer}

        Respond with only 3 questions
        Output in JSON format with keys: "questions" (list).
    ''').strip("\n")

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": user_prompt 
    }

    return response_obj

def chat_title_prompts(first_question: str):
    
    # system
    system_prompt_path = '../prompt_builder/prompts/chat_title.txt'
    with open(system_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    system_prompt = ''.join(lines)

    # user
    user_prompt = dedent(f'''
        This is the first question the user asked in the chat:
        {first_question}

        Respond with a concise topic for the chat.
    ''').strip("\n")

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": user_prompt 
    }

    return response_obj

def dummy_call_prompts():

    # book data
    book_file_path = '../datasource/Google_docs_extract_data.txt'
    with open(book_file_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    book_data = ''.join(lines)

    # system
    system_prompt_path = '../prompt_builder/prompts/wld/ans_ref_sys_prompt.txt'
    with open(system_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    system_prompt = ''.join(lines)

    # user
    user_prompt_path = '../prompt_builder/prompts/wld/ans_ref_usr_prompt.txt'
    with open(user_prompt_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
    user_prompt = {
        "instructions": ''.join(lines),
        "user_question": dedent(f'''
            This is just a test question. Just respond with "dummy" and nothing else.
        ''').strip("\n")
    }

    response_obj = {
        "system_prompt": system_prompt,
        "user_query": user_prompt,
        "book_data": book_data
    }

    return response_obj