from openai import OpenAI


def get_user_response(request, rdf_response, sdd_response):

    client = OpenAI()

    system_content = """
        Use the provided information delimited by triple quotes to answer the question
    """

    user_content = f"""
        '''user request: {request}'''
        '''dataset publisher(s): {rdf_response.publishers}'''
        '''dataset description(s): {rdf_response.descriptions}'''
        '''Does the dataset contain pii?: {'Yes.' if sdd_response.pii else 'No.'}'''

        Question: 
        Can you validate that you understand the user request, then list the relevant publishers and descriptions, and then state presence of pii?
    """

    assistant_content = f"""
        To retrieve your requested data, you will need the following:
        - Dataset {rdf_response.publishers}: {rdf_response.descriptions}

        The dataset you requested {'contains' if sdd_response.pii else 'does not contain'} any personally identifiable information.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
            {"role": "user", "content": user_content}
        ]
    )

    return completion.choices[0].message.content
