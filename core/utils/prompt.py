prompt_extract = \
"""
Act as Linguistic who has expertise on Skill and Knowledge. Extract Skill and Knowledge from the given text maximum 2 words only.

text: {text}

Rule entity parsing:
  - Skill: Skill is a set of related knowledge that can be learned through experience. A skill is not an action or an activity. A skill is a set of knowledge that can be learned through experience.
  - Location: Location specific into city name is enough without country.
  - Year of Experience: Year of experience is a numerical value that represents the number of years of experience.
  - Job Title Relevan: Job title relevan is a general representation of title based on text provided.

Generate the result without additional description or 'Here is the result:' or 'Based on the given text', or 'I extracted the skills and knowledge as follows', 
use the following format as output of your response,

skill_extracted: ['', '']
location: ''
year_of_experience: ''
job_title_relevan: ''
"""
prompt_skill_required = \
"""
Act as Professional HR who has experience 10 years in General HR Field, 
I want you to suggest minimum 3 skill that required based on provided information below, 
Ensure the skill suggested is not listed on information below,

skills: {skills}
year_of_experience: {year_of_experience}
job_title_relevan: {job_title_relevan}

Generate the result without additional description or 'Here is the result:' or 'Based on the given text',
skill_suggest: ['', '', '']
"""