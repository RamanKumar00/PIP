from typing import Dict, List, Any

class RecruiterSimulator:
    """Simulates recruiter screening logic, assesses readiness, and generates contextual practice questions.
    """
    def simulate(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the simulation based on extracted resume parameters.

        Args:
            text: Resume plain text.
            data: Compiled metrics dictionary (skills, scores, role specs).

        Returns:
            Dict[str, Any]: Recruiter screening dashboard payload.
        """
        detected_skills = data.get("detected_skills", {})
        missing_skills = data.get("missing_skills", [])
        ats_score = data.get("ats_score", 50)
        project_analyses = data.get("project_analyses", [])
        
        # Calculate Skill Match Count
        total_detected = sum(len(lst) for lst in detected_skills.values())
        
        # 1. Compute Interview Readiness Score (0-100)
        # Weighted metric: 40% ATS Score + 30% Skill Coverage + 30% Projects Quality
        skill_coverage_score = min(int((total_detected / 12) * 100), 100) if total_detected > 0 else 30
        
        avg_project_quality = 50
        if project_analyses:
            avg_project_quality = sum(p.get("score", 50) for p in project_analyses) / len(project_analyses)
            
        readiness_score = int(ats_score * 0.4 + skill_coverage_score * 0.3 + avg_project_quality * 0.3)
        readiness_score = min(max(readiness_score, 10), 100)

        # 2. Determine Screening Decision
        if readiness_score >= 80:
            screening_decision = "Shortlist for Interview"
        elif readiness_score >= 60:
            screening_decision = "Borderline (Manual Screen Required)"
        else:
            screening_decision = "Reject (Does not satisfy threshold)"

        # 3. Dynamic Strengths and Reservations
        strengths = []
        reservations = []

        # Evaluate skills
        if total_detected >= 8:
            strengths.append(f"Technical portfolio is broad, containing {total_detected} parsed skills across multiple domains.")
        else:
            reservations.append("Skill index is thin; could benefit from learning more languages and tools.")

        # Evaluate projects
        if len(project_analyses) >= 2:
            strengths.append(f"Demonstrates hands-on engineering experience through {len(project_analyses)} documented projects.")
        else:
            reservations.append("Lacks multiple independent projects to validate coding skills.")

        # Evaluate metrics in projects
        metric_bullets = 0
        for p in project_analyses:
            # Simple heuristic checking if suggestions were empty (meaning it had metrics)
            if p.get("score", 50) >= 75:
                metric_bullets += 1
                
        if metric_bullets >= 1:
            strengths.append("Contains quantified impact indicators showing clear results of work.")
        else:
            reservations.append("Project writeups are purely descriptive; lacks quantifiable metrics showing project outcomes.")

        if missing_skills:
            reservations.append(f"Missing core technical target skills: {', '.join(missing_skills[:3])}.")

        # 4. Generate Customized Interview Prep Questions
        questions = []
        
        # Skill-based questions
        for skill in missing_skills[:2]:
            questions.append({
                "question": f"Our technical stack relies on {skill}. Can you describe any theoretical concepts or explain how you would learn and implement it in our environment?",
                "type": "technical",
                "reason": f"Target role demands {skill}, which was not detected in your resume."
            })
            
        # Project-based questions
        for proj in project_analyses[:2]:
            title = proj.get("title", "Project")
            questions.append({
                "question": f"In your project '{title}', what was the biggest architectural bottleneck you encountered and how did you resolve it?",
                "type": "technical",
                "reason": f"Direct follow-up to check depth of engineering in your project '{title}'."
            })

        # Behavioral questions
        questions.append({
            "question": "Can you describe a situation where you had to quickly learn a new technology to build a placement project under tight timelines?",
            "type": "behavioral",
            "reason": "Evaluates learning velocity and stress management for campus placements."
        })

        return {
            "screening_decision": screening_decision,
            "strengths": strengths if strengths else ["No major strengths detected."],
            "reservations": reservations if reservations else ["No major concerns detected."],
            "interview_readiness_score": readiness_score,
            "interview_questions": questions
        }
