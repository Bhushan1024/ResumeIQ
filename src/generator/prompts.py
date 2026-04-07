def get_interview_prompt(resume_data, num_questions=8):
    return f"""
You are an experienced technical interviewer. Generate {num_questions} relevant interview questions for the candidate.

Candidate Profile:
- Name: {resume_data.full_name}
- Experience Level: {resume_data.experience_level}
- Total Experience: {resume_data.total_experience_years or 0} years
- Skills: {', '.join(resume_data.skills[:15]) if resume_data.skills else 'None'}
- Summary: {resume_data.summary or 'Full Stack Developer'}

Recent Experience:
{chr(10).join([f"- {exp.role} at {exp.company}" for exp in resume_data.experience[:3]]) if resume_data.experience else 'None'}

Generate questions in 3 categories:
1. Technical Questions (based on skills and projects)
2. Behavioral Questions (using STAR method)
3. Situational / Project-based Questions

For each question, also provide a strong, concise expected answer based ONLY on the candidate's actual experience.

Return the output in clear markdown format with question and expected answer.
"""