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
Act as Professional HR who has experience 10 years in Technical Software Development HR Field, 
I want you to suggest minimum 3 skill that required based on provided title relevan below, 
Ensure the skill suggested is not listed on information below,

skills: {skills}
year_of_experience: {year_of_experience}
job_title_relevan: {job_title_relevan}

Generate the result without additional description or 'Here is the result:' or 'Based on the given text',
skill_suggest: ['', '', '']
"""
prompt_cover_letter = \
"""
Generate a professional and personalized cover letter using the following information:

Applicant's Background: {text_resume}

Company Information:
Company Name: {company_name}
Job Title: {job_title}
Job Description: {job_description}


Instructions:
- Create a compelling opening paragraph that grabs attention and mentions the specific position.
- In the body paragraphs, highlight how the applicant's experience and skills align with the job requirements. Use specific examples from the CV to demonstrate qualifications.
- Show enthusiasm for the role and company, incorporating the personalization details provided.
- Conclude with a strong closing paragraph, expressing interest in further discussion and providing contact information.
- Keep the tone professional yet personable, and limit the letter to one page (about 300-400 words).
- Do not include any information that is not provided in the inputs above or commonly found in standard cover letters.

Please generate a cover letter based on this information, tailored to the specific job and company while highlighting the applicant's unique qualifications and enthusiasm for the role.
Please response start with 'Dear Hiring Manager'
"""
prompt_salary_estimation = \
"""
Generate salary estimation in IDR currency based on user skill, job title, and year of experience information below:

skills: {skills}
year_of_experience: {year_of_experience}
job_title_relevan: {job_title_relevan}

note: please consider salary estimation based on tech winter condition in Indonesia
please only mention the monthly estimate salary without any additional information.

Rp. ...
"""