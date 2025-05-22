from typing import List, Optional, Dict
from github import Github, GithubException
from app.core.config import settings
from app.models.business import Business, business_users
from app.models.users import User
from app.services.ticket import TicketService
from datetime import datetime
import json

class GitHubService:
    def __init__(self, access_token: str):
        self.github = Github(access_token)
        self.ticket_service = None  # Will be initialized with db session

    def set_ticket_service(self, ticket_service):
        self.ticket_service = ticket_service

    def get_repository(self, repo_name: str):
        """Get repository by name"""
        try:
            return self.github.get_repo(repo_name)
        except GithubException as e:
            raise Exception(f"Failed to get repository: {str(e)}")

    def create_code_review(self, repo_name: str, pr_number: int, review_data: Dict):
        """Create a code review for a pull request"""
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Create review comment
            review = pr.create_review(
                body=review_data["comment"],
                event=review_data["event"],  # APPROVE, REQUEST_CHANGES, COMMENT
                comments=review_data.get("comments", [])
            )
            
            # Create ticket for follow-up tasks if needed
            if review_data.get("create_ticket", False):
                self._create_followup_ticket(repo_name, pr, review_data)
            
            return review
        except GithubException as e:
            raise Exception(f"Failed to create review: {str(e)}")

    def _create_followup_ticket(self, repo_name: str, pr, review_data: Dict):
        """Create a follow-up ticket based on review feedback"""
        if not self.ticket_service:
            raise Exception("Ticket service not initialized")

        ticket_data = {
            "title": f"Follow-up: {pr.title}",
            "description": review_data.get("ticket_description", ""),
            "priority": review_data.get("priority", "medium"),
            "type": review_data.get("ticket_type", "task"),
            "assignee_id": pr.user.id,  # Assign to PR creator
            "labels": review_data.get("labels", ["code-review", "follow-up"]),
            "metadata": {
                "pr_url": pr.html_url,
                "repo_name": repo_name,
                "review_id": review_data.get("review_id")
            }
        }
        
        return self.ticket_service.create_ticket(ticket_data)

    def get_commit_history(self, repo_name: str, branch: str = "main"):
        """Get commit history for a branch"""
        try:
            repo = self.get_repository(repo_name)
            branch = repo.get_branch(branch)
            commits = repo.get_commits(sha=branch.commit.sha)
            return [commit for commit in commits]
        except GithubException as e:
            raise Exception(f"Failed to get commit history: {str(e)}")

    def analyze_commit(self, repo_name: str, commit_sha: str):
        """Analyze a commit and provide feedback"""
        try:
            repo = self.get_repository(repo_name)
            commit = repo.get_commit(commit_sha)
            
            analysis = {
                "sha": commit.sha,
                "author": commit.author.login,
                "message": commit.commit.message,
                "files_changed": len(commit.files),
                "additions": commit.stats.additions,
                "deletions": commit.stats.deletions,
                "changes": commit.stats.total,
                "files": [{
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes
                } for file in commit.files]
            }
            
            # Add recommendations based on changes
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            return analysis
        except GithubException as e:
            raise Exception(f"Failed to analyze commit: {str(e)}")

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on commit analysis"""
        recommendations = []
        
        # Check for large changes
        if analysis["changes"] > 500:
            recommendations.append("Consider breaking down large changes into smaller, focused commits")
        
        # Check for test coverage
        if not any(f["filename"].endswith(("_test.py", "test_")) for f in analysis["files"]):
            recommendations.append("Consider adding tests for the changes")
        
        # Check for documentation
        if not any(f["filename"].endswith((".md", ".rst")) for f in analysis["files"]):
            recommendations.append("Consider updating documentation for the changes")
        
        return recommendations

    def assign_next_module(self, user_id: str, current_module: str):
        """Assign next module based on user's progress and role"""
        try:
            # Get user's role and progress
            user = self.github.get_user(user_id)
            user_repos = user.get_repos()
            
            # Analyze user's contributions
            contributions = self._analyze_user_contributions(user)
            
            # Determine next module based on role and progress
            next_module = self._determine_next_module(contributions, current_module)
            
            # Create ticket for next module
            if self.ticket_service:
                ticket_data = {
                    "title": f"Next Module Assignment: {next_module['name']}",
                    "description": next_module["description"],
                    "priority": "high",
                    "type": "task",
                    "assignee_id": user_id,
                    "labels": ["module", "assignment"],
                    "metadata": {
                        "module_name": next_module["name"],
                        "estimated_hours": next_module.get("estimated_hours"),
                        "prerequisites": next_module.get("prerequisites", [])
                    }
                }
                self.ticket_service.create_ticket(ticket_data)
            
            return next_module
        except GithubException as e:
            raise Exception(f"Failed to assign next module: {str(e)}")

    def _analyze_user_contributions(self, user) -> Dict:
        """Analyze user's GitHub contributions"""
        contributions = {
            "total_commits": 0,
            "total_prs": 0,
            "total_issues": 0,
            "languages": set(),
            "repositories": []
        }
        
        for repo in user.get_repos():
            contributions["repositories"].append(repo.name)
            contributions["total_commits"] += repo.get_commits().totalCount
            contributions["total_prs"] += repo.get_pulls().totalCount
            contributions["total_issues"] += repo.get_issues().totalCount
            
            # Get repository languages
            try:
                languages = repo.get_languages()
                contributions["languages"].update(languages.keys())
            except GithubException:
                continue
        
        return contributions

    def _determine_next_module(self, contributions: Dict, current_module: str) -> Dict:
        """Determine next module based on user's contributions and current module"""
        # This is a simplified example - you would want to implement more sophisticated logic
        modules = {
            "backend": {
                "name": "Advanced API Development",
                "description": "Implement advanced API features including caching, rate limiting, and optimization",
                "estimated_hours": 20,
                "prerequisites": ["Basic API Development", "Database Design"]
            },
            "frontend": {
                "name": "Advanced UI Components",
                "description": "Create reusable UI components with advanced features and animations",
                "estimated_hours": 15,
                "prerequisites": ["Basic UI Development", "State Management"]
            },
            "devops": {
                "name": "CI/CD Pipeline Optimization",
                "description": "Optimize and secure CI/CD pipelines with advanced features",
                "estimated_hours": 25,
                "prerequisites": ["Basic CI/CD", "Container Orchestration"]
            }
        }
        
        # Determine role based on contributions
        role = self._determine_role(contributions)
        
        # Get next module based on role and current module
        if role == "backend":
            return modules["backend"]
        elif role == "frontend":
            return modules["frontend"]
        else:
            return modules["devops"]

    def _determine_role(self, contributions: Dict) -> str:
        """Determine user's role based on contributions"""
        # This is a simplified example - you would want to implement more sophisticated logic
        if "Python" in contributions["languages"] or "Java" in contributions["languages"]:
            return "backend"
        elif "JavaScript" in contributions["languages"] or "TypeScript" in contributions["languages"]:
            return "frontend"
        else:
            return "devops" 