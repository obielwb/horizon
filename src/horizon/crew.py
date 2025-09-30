from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any, Optional
import json
import pandas as pd
from datetime import datetime

# Import our custom tools
from .tools.startup_discovery_tools import (
    StartupDiscoveryTool, CompanyAnalysisTool, FundingResearchTool,
    LinkedInSearchTool, scrape_tool, website_search_tool
)
from .config import Config

@CrewBase
class Horizon():
    """NVIDIA Inception AI Startup Discovery System - Unified Class"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        super().__init__()
        # Initialize custom tools
        self.startup_discovery_tool = StartupDiscoveryTool()
        self.company_analysis_tool = CompanyAnalysisTool()
        self.funding_research_tool = FundingResearchTool()
        self.linkedin_search_tool = LinkedInSearchTool()
        
        # Tool collections for different agent types
        self.discovery_tools = [self.startup_discovery_tool, website_search_tool]
        self.analysis_tools = [self.company_analysis_tool, scrape_tool, website_search_tool]
        self.research_tools = [self.funding_research_tool, self.linkedin_search_tool, website_search_tool]
        self.market_tools = [website_search_tool, scrape_tool]
        
        # Storage for results
        self.results_storage = {}

    # =============================================================================
    # CrewAI Framework Methods (Agents, Tasks, Crew)
    # =============================================================================

    @agent
    def discovery_agent(self) -> Agent:
        """AI Startup Discovery Specialist"""
        return Agent(
            config=self.agents_config['discovery_agent'],
            tools=self.discovery_tools,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def qualification_agent(self) -> Agent:
        """AI Technology Assessment Analyst"""
        return Agent(
            config=self.agents_config['qualification_agent'],
            tools=self.analysis_tools,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def funding_intelligence_agent(self) -> Agent:
        """Investment Research Analyst"""
        return Agent(
            config=self.agents_config['funding_intelligence_agent'],
            tools=self.research_tools,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def leadership_scout_agent(self) -> Agent:
        """Technical Leadership Researcher"""
        return Agent(
            config=self.agents_config['leadership_scout_agent'],
            tools=self.research_tools,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def market_intelligence_agent(self) -> Agent:
        """Latin America AI Market Analyst"""
        return Agent(
            config=self.agents_config['market_intelligence_agent'],
            tools=self.market_tools,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def validation_agent(self) -> Agent:
        """Startup Data Validation Specialist"""
        return Agent(
            config=self.agents_config['validation_agent'],
            tools=[scrape_tool, website_search_tool],
            verbose=True,
            allow_delegation=False
        )

    @task
    def discovery_task(self) -> Task:
        """Discover AI startups in target country"""
        return Task(
            config=self.tasks_config['discovery_task'],
            output_file='discovered_startups.json'
        )

    @task
    def qualification_task(self) -> Task:
        """Analyze and qualify discovered startups"""
        return Task(
            config=self.tasks_config['qualification_task'],
            output_file='startup_qualifications.json'
        )
    
    @task
    def funding_research_task(self) -> Task:
        """Research funding information for qualified startups"""
        return Task(
            config=self.tasks_config['funding_research_task'],
            output_file='funding_analysis.json'
        )
    
    @task
    def leadership_research_task(self) -> Task:
        """Research technical leadership for startups"""
        return Task(
            config=self.tasks_config['leadership_research_task'],
            output_file='leadership_profiles.json'
        )
    
    @task
    def market_analysis_task(self) -> Task:
        """Analyze market trends and ecosystem"""
        return Task(
            config=self.tasks_config['market_analysis_task'],
            output_file='market_analysis.json'
        )
    
    @task
    def validation_and_scoring_task(self) -> Task:
        """Validate data and create comprehensive scoring"""
        return Task(
            config=self.tasks_config['validation_and_scoring_task'],
            output_file='validated_startup_database.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NVIDIA Inception Startup Discovery crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    # =============================================================================
    # Business Logic Methods (Discovery Operations)
    # =============================================================================
    
    def discover_country(self, country: str, specific_ventures: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run complete startup discovery for a specific country"""
        
        print(f"\nStarting AI Startup Discovery for {country}")
        print(f"Target: NVIDIA Inception Program Candidates")
        
        if specific_ventures:
            print(f"📋 Specific ventures to research: {', '.join(specific_ventures)}")
        
        # Prepare inputs for the crew
        inputs = {
            'country': country,
            'current_year': str(datetime.now().year),
            'target_technologies': self._get_config_value('AI_TECHNOLOGIES', 'AI, ML, Deep Learning'),
            'target_sectors': self._get_config_value('MARKET_SECTORS', 'FinTech, HealthTech, EdTech'),
            'funding_stages': self._get_config_value('FUNDING_STAGES', 'Series A, Series B, Series C'),
            'specific_ventures': ', '.join(specific_ventures) if specific_ventures else 'None specified'
        }
        
        try:
            # Execute the crew
            crew_results = self.crew().kickoff(inputs=inputs)
            
            # Process and store results
            processed_results = self._process_crew_results(crew_results, country)
            self.results_storage[country] = processed_results
            
            # Export results
            self._export_to_formats(processed_results, country)
            
            print(f"✅ Successfully completed discovery for {country}")
            return processed_results
            
        except Exception as e:
            error_msg = f"❌ Error processing {country}: {str(e)}"
            print(error_msg)
            self.results_storage[country] = {"error": error_msg}
            return {"error": error_msg}
    
    def discover_multiple_countries(self, countries: List[str], 
                                   specific_ventures_per_country: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """Run discovery for multiple countries"""
        
        print("🌎 Starting Multi-Country AI Startup Discovery")
        print(f"📍 Target Countries: {', '.join(countries)}")
        
        all_results = {}
        
        for country in countries:
            specific_ventures = None
            if specific_ventures_per_country and country in specific_ventures_per_country:
                specific_ventures = specific_ventures_per_country[country]
            
            result = self.discover_country(country, specific_ventures)
            all_results[country] = result
            
            # Add delay between countries to be respectful to APIs
            import time
            time.sleep(30)  # 30 second delay between countries
        
        # Create consolidated report
        self._create_consolidated_report(all_results)
        
        return all_results

    # =============================================================================
    # Private Helper Methods
    # =============================================================================
    
    def _get_config_value(self, attr_name: str, default_value: str) -> str:
        """Get config value with fallback"""
        if hasattr(Config, attr_name):
            attr_value = getattr(Config, attr_name)
            if isinstance(attr_value, list):
                return ', '.join(attr_value[:10])  # Take first 10 items
            return str(attr_value)
        return default_value
    
    def _process_crew_results(self, crew_results, country: str) -> Dict[str, Any]:
        """Process and structure the crew results"""
        
        if hasattr(crew_results, 'tasks_output'):
            task_results = {}
            for task_output in crew_results.tasks_output:
                task_name = task_output.description[:50] if hasattr(task_output, 'description') else 'unknown_task'
                task_results[task_name] = str(task_output)
        else:
            task_results = {"crew_output": str(crew_results)}
        
        return {
            "country": country,
            "discovery_date": datetime.now().isoformat(),
            "task_results": task_results,
            "summary": {
                "total_tasks": len(task_results),
                "completion_status": "success"
            }
        }
    
    def _export_to_formats(self, results: Dict[str, Any], country: str) -> None:
        """Export results to multiple formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"nvidia_inception_{country.lower()}_{timestamp}"
        
        # Export comprehensive JSON
        with open(f"{base_filename}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Extract startup data for CSV export
        startup_data = []
        for task_name, task_result in results.items():
            if isinstance(task_result, str):
                try:
                    parsed_result = json.loads(task_result)
                    if isinstance(parsed_result, dict) and 'startups' in parsed_result:
                        startup_data.extend(parsed_result['startups'])
                except json.JSONDecodeError:
                    continue
        
        # Create DataFrame and export to CSV
        if startup_data:
            df = pd.DataFrame(startup_data)
            df.to_csv(f"{base_filename}.csv", index=False)
        
        # Create summary report
        self._create_summary_report(results, country, base_filename)
        
        print(f"\n✅ Results exported:")
        print(f"   - JSON: {base_filename}.json")
        print(f"   - CSV: {base_filename}.csv")
        print(f"   - Summary: {base_filename}_summary.md")
    
    def _create_summary_report(self, results: Dict[str, Any], country: str, base_filename: str) -> None:
        """Create a markdown summary report"""
        
        report_content = f"""# NVIDIA Inception AI Startup Discovery Report
## Country: {country}
## Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Executive Summary

This report contains comprehensive AI startup discovery and analysis for {country}.

## Methodology

Six specialized AI agents analyzed:
1. **Discovery Agent**: Startup identification
2. **Qualification Agent**: Technical capabilities assessment
3. **Funding Intelligence Agent**: Investment history research
4. **Leadership Scout Agent**: Technical leadership profiling
5. **Market Intelligence Agent**: Market trends analysis
6. **Validation Agent**: Data validation and scoring

## Detailed Results

"""
        
        for task_name, task_result in results.items():
            report_content += f"### {task_name.replace('_', ' ').title()}\n\n"
            
            if isinstance(task_result, str):
                truncated_result = task_result[:1000] + "..." if len(task_result) > 1000 else task_result
                report_content += f"```\n{truncated_result}\n```\n\n"
            else:
                report_content += f"{str(task_result)}\n\n"
        
        report_content += f"""
## Data Files

- Complete data: `{base_filename}.json`
- Startup database: `{base_filename}.csv`
- This summary: `{base_filename}_summary.md`

---

*Report generated by NVIDIA Inception AI Startup Discovery System*
"""
        
        with open(f"{base_filename}_summary.md", "w", encoding="utf-8") as f:
            f.write(report_content)
    
    def _create_consolidated_report(self, all_results: Dict[str, Any]) -> None:
        """Create a consolidated report across all countries"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nvidia_inception_consolidated_{timestamp}"
        
        # Export consolidated JSON
        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        # Create consolidated markdown report
        report_content = f"""# NVIDIA Inception: Multi-Country AI Startup Discovery
## Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Countries Analyzed

"""
        
        for country, results in all_results.items():
            status = "✅ Success" if "error" not in results else "❌ Error"
            report_content += f"- **{country}**: {status}\n"
        
        report_content += f"""

## Summary Statistics

- Total countries analyzed: {len(all_results)}
- Successful discoveries: {len([r for r in all_results.values() if 'error' not in r])}
- Failed discoveries: {len([r for r in all_results.values() if 'error' in r])}

---

*Consolidated report generated by NVIDIA Inception AI Startup Discovery System*
"""
        
        with open(f"{filename}_consolidated.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"\n📊 Consolidated Report Created:")
        print(f"   - JSON: {filename}.json")
        print(f"   - Summary: {filename}_consolidated.md")