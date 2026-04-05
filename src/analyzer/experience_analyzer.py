from src.models.resume import ResumeData
from typing import Tuple

class ExperienceAnalyzer:
    """Analyzes experience level and generates candidate summary."""

    @staticmethod
    def calculate_experience_level(resume_data: ResumeData) -> str:
        years = resume_data.total_experience_years or 0.0
        if years < 2:
            return "Junior"
        elif years < 5:
            return "Mid-level"
        else:
            return "Senior"

    @staticmethod
    def generate_candidate_summary(resume_data: ResumeData) -> str:
        name = resume_data.full_name or "Candidate"
        level = resume_data.experience_level
        years = resume_data.total_experience_years or 0
        skills = ", ".join(resume_data.skills[:8]) if resume_data.skills else "various technologies"
        
        summary = f"{name} is a {level} professional with approximately {years:.1f} years of experience. "
        summary += f"Strong expertise in {skills}. "
        
        if resume_data.experience and len(resume_data.experience) > 0:
            latest = resume_data.experience[0]
            summary += f"Most recently worked as {latest.role} at {latest.company}."
        
        return summary.strip()

    def analyze(self, resume_data: ResumeData) -> Tuple[ResumeData, str]:
        if not resume_data.experience_level or resume_data.experience_level in ["Unknown", "Senior ("]:
            resume_data.experience_level = self.calculate_experience_level(resume_data)
        
        if resume_data.total_experience_years is None and resume_data.experience:
            resume_data.total_experience_years = len(resume_data.experience) * 2.0
        
        summary = self.generate_candidate_summary(resume_data)
        return resume_data, summary