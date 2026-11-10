from datetime import date
from typing import Optional, Tuple

from src.models.resume import ResumeData
from src.utils.experience_dates import parse_experience_ranges, years_from_ranges

VALID_LEVELS = ("Junior", "Mid-level", "Senior")


class ExperienceAnalyzer:
    """Analyzes experience level and generates candidate summary."""

    @staticmethod
    def calculate_experience_level(resume_data: ResumeData) -> str:
        years = resume_data.total_experience_years
        if years is None:
            llm_level = (resume_data.experience_level or "").strip()
            return llm_level if llm_level in VALID_LEVELS else "Unknown"
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
        who = f"a {level} professional" if level in VALID_LEVELS else "a professional"
        years = resume_data.total_experience_years
        skills = ", ".join(resume_data.skills[:8]) if resume_data.skills else "various technologies"

        if years:
            summary = f"{name} is {who} with approximately {years:.1f} years of experience. "
        else:
            summary = f"{name} is {who} (experience duration could not be determined from the resume). "
        summary += f"Strong expertise in {skills}. "
        
        if resume_data.experience and len(resume_data.experience) > 0:
            latest = resume_data.experience[0]
            summary += f"Most recently worked as {latest.role} at {latest.company}."
        
        return summary.strip()

    @staticmethod
    def calculate_total_years(
        resume_data: ResumeData, *, today: Optional[date] = None
    ) -> Optional[float]:
        """Career length in years, most trustworthy source first.

        1. Every entry's dates parse  -> union of the date ranges (overlaps counted once).
        2. Only some entries parse    -> parsed union + duration_years of the rest,
           raised to the resume's stated total if that is larger (the dates undercount).
        3. Nothing parses             -> summed duration_years, then the stated total.
        """
        stated = resume_data.total_experience_years
        stated = float(stated) if stated and stated > 0 else None

        if resume_data.experience:
            ranges, unparsed = parse_experience_ranges(resume_data.experience, today=today)
            from_dates = years_from_ranges(ranges)
            unparsed_durations = sum(
                float(e.duration_years) for e in unparsed if e.duration_years
            )

            if from_dates:
                if not unparsed:
                    return from_dates
                partial = from_dates + unparsed_durations
                return round(max(partial, stated or 0.0), 2)

            if unparsed_durations > 0:
                return round(unparsed_durations, 2)

        return round(stated, 2) if stated else None

    def analyze(
        self, resume_data: ResumeData, *, today: Optional[date] = None
    ) -> Tuple[ResumeData, str]:
        resume_data.total_experience_years = self.calculate_total_years(resume_data, today=today)

        resume_data.experience_level = self.calculate_experience_level(resume_data)

        summary = self.generate_candidate_summary(resume_data)
        return resume_data, summary