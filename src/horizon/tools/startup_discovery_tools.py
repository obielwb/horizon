from crewai.tools import BaseTool
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path
from horizon.utils.database import StartupDB

# Initialize built-in CrewAI tools
scrape_tool = ScrapeWebsiteTool()
website_search_tool = WebsiteSearchTool()

class StartupSearchInput(BaseModel):
    """Input schema for startup search tool."""
    country: str = Field(..., description="Country to search for startups (e.g., 'Brazil', 'Mexico')")
    industry: str = Field(default="AI", description="Industry focus (e.g., 'AI', 'FinTech', 'HealthTech')")
    specific_ventures: Optional[List[str]] = Field(default=None, description="List of specific venture names to search for")
    funding_stage: str = Field(default="all", description="Funding stage filter (e.g., 'Series A', 'Seed', 'all')")

class CompanyAnalysisInput(BaseModel):
    """Input schema for company analysis tool."""
    website_url: str = Field(..., description="Company website URL to analyze")
    analysis_type: str = Field(default="full", description="Type of analysis: 'full', 'technology', 'funding', 'team'")

class FundingResearchInput(BaseModel):
    """Input schema for funding research tool."""
    company_name: str = Field(..., description="Company name to research funding for")
    website_url: Optional[str] = Field(None, description="Company website URL if available")

class LinkedInSearchInput(BaseModel):
    """Input schema for LinkedIn profile search."""
    person_name: str = Field(..., description="Person's name to search for")
    company_name: str = Field(..., description="Company name for context")
    role_title: str = Field(default="CTO", description="Role title to search for (e.g., 'CTO', 'Founder')")

class StartupDiscoveryTool(BaseTool):
    name: str = "startup_discovery_tool"
    description: str = (
        "Discover AI startups in Latin American countries by searching through "
        "various online sources including VC portfolios, startup databases, and tech news. "
        "Can search for specific ventures if provided."
    )
    args_schema: Type[BaseModel] = StartupSearchInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = StartupDB(Path("outputs/discovered_startups.json"))

    def _run(self, country: str, industry: str = "AI", specific_ventures: Optional[List[str]] = None, funding_stage: str = "all") -> str:
        """Discover startups by searching multiple online sources"""
        
        # If specific ventures are provided, prioritize searching for them
        if specific_ventures:
            return self._search_specific_ventures(specific_ventures, country, industry)
        
        # Default search for general startup discovery
        startup_sources = [
            f"{country} {industry} startups 2024 2023",
            f"site:crunchbase.com {country} {industry} startups",
            f"{country} artificial intelligence companies",
            f"{country} tech startups funding rounds",
            f"Kaszek Ventures {country} portfolio",
            f"ALLVP {country} investments" if country in ["Mexico", "Colombia"] else f"{country} VC investments",
            f"{country} startup accelerators companies"
        ]
        
        discovered_startups = []
        existing_startups = self.db.load_startups()
        
        for search_query in startup_sources[:5]:  # Limit searches
            try:
                search_result = website_search_tool.run(search_query)
                if search_result:
                    companies = self._extract_companies_from_text(search_result, country, industry)
                    discovered_startups.extend(companies)
                    time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Search error for query '{search_query}': {e}")
                continue
        
        unique_startups = self._deduplicate_startups(discovered_startups, existing_startups)
        self.db.add_startups(unique_startups)
        
        return json.dumps({
            "country": country,
            "industry": industry,
            "search_type": "general_discovery",
            "total_found": len(unique_startups),
            "startups": unique_startups[:20],
            "sources_searched": len(startup_sources)
        }, indent=2)
    
    def _search_specific_ventures(self, ventures: List[str], country: str, industry: str) -> str:
        """Search for specific venture names"""
        venture_results = []
        
        for venture in ventures:
            venture_data = {
                "name": venture,
                "country": country,
                "industry": industry,
                "found_info": [],
                "websites": [],
                "funding_info": []
            }
            
            # Multiple search strategies for each venture
            search_queries = [
                f'"{venture}" {country} startup',
                f'"{venture}" artificial intelligence {country}',
                f'"{venture}" company website',
                f'"{venture}" funding investment',
                f'site:crunchbase.com "{venture}"'
            ]
            
            for query in search_queries:
                try:
                    result = website_search_tool.run(query)
                    if result:
                        info = self._extract_venture_specific_info(result, venture)
                        if info:
                            venture_data["found_info"].extend(info)
                    time.sleep(1.5)  # Shorter delay for specific searches
                except Exception as e:
                    print(f"Error searching for {venture}: {e}")
                    continue
            
            # Deduplicate and clean venture data
            venture_data["found_info"] = self._deduplicate_venture_info(venture_data["found_info"])
            venture_results.append(venture_data)
        
        return json.dumps({
            "country": country,
            "industry": industry,
            "search_type": "specific_ventures",
            "ventures_searched": len(ventures),
            "results": venture_results
        }, indent=2)
    
    def _extract_venture_specific_info(self, text: str, venture_name: str) -> List[Dict]:
        """Extract information specific to a venture"""
        info_entries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if venture_name.lower() in line.lower() and len(line) > 20:
                
                # Extract website URLs
                website_match = re.search(r'https?://[^\s]+', line)
                
                # Look for funding information
                funding_match = re.search(r'\$[\d.,]+[MBK]|\d+\s*(million|billion)', line, re.IGNORECASE)
                
                info_entry = {
                    "description": line[:300],
                    "website": website_match.group(0) if website_match else None,
                    "funding_mention": funding_match.group(0) if funding_match else None,
                    "relevance_score": self._calculate_venture_relevance(line, venture_name)
                }
                
                if info_entry["relevance_score"] > 0:
                    info_entries.append(info_entry)
        
        return info_entries
    
    def _calculate_venture_relevance(self, text: str, venture_name: str) -> int:
        """Calculate relevance score for venture information"""
        score = 0
        text_lower = text.lower()
        venture_lower = venture_name.lower()
        
        # Exact name match
        if venture_lower in text_lower:
            score += 3
        
        # AI/tech keywords
        ai_keywords = ['artificial intelligence', 'ai', 'machine learning', 'startup', 'technology', 'innovation']
        for keyword in ai_keywords:
            if keyword in text_lower:
                score += 1
        
        # Business keywords
        business_keywords = ['company', 'founded', 'ceo', 'funding', 'investment', 'series']
        for keyword in business_keywords:
            if keyword in text_lower:
                score += 1
        
        return score
    
    def _deduplicate_venture_info(self, info_list: List[Dict]) -> List[Dict]:
        """Remove duplicate venture information"""
        unique_info = []
        seen_descriptions = set()
        
        # Sort by relevance score
        info_list.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        for info in info_list:
            desc = info.get("description", "")[:100].lower()
            if desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_info.append(info)
        
        return unique_info[:10]  # Top 10 most relevant
    
    def _extract_companies_from_text(self, text: str, country: str, industry: str) -> List[Dict]:
        """Extract company information from search results text"""
        companies = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 15 and any(keyword in line.lower() for keyword in ['startup', 'company', 'ai', 'tech', 'founded']):
                company_name = self._extract_company_name(line)
                if company_name and len(company_name) > 2:
                    potential_company = {
                        "name": company_name,
                        "description": line[:200],
                        "country": country,
                        "industry": industry,
                        "source_line": line
                    }
                    companies.append(potential_company)
        
        return companies
    
    def _extract_company_name(self, text: str) -> str:
        """Extract potential company name from text"""
        words = text.split()
        
        # Look for company indicators
        for i, word in enumerate(words):
            if word.lower() in ['company', 'startup', 'founded', 'inc', 'ltd']:
                if i > 0:
                    name_parts = words[max(0, i-2):i]
                    return ' '.join(name_parts).strip('.,;:"')
        
        # Fallback: take first few capitalized words
        capitalized_words = [word for word in words[:5] if word and word[0].isupper() and len(word) > 1]
        return ' '.join(capitalized_words[:2]) if capitalized_words else ""
    
    def _deduplicate_startups(self, startups: List[Dict], existing_startups: List[str]) -> List[Dict]:
        """Remove duplicate startups based on name similarity and existing database."""
        unique_startups = []
        seen_names = set(existing_startups)
        
        for startup in startups:
            name = startup.get("name", "").lower().strip()
            if name and name not in seen_names and len(name) > 2:
                seen_names.add(name)
                unique_startups.append(startup)
        
        return unique_startups

class CompanyAnalysisTool(BaseTool):
    name: str = "company_analysis_tool"
    description: str = (
        "Analyze a company's website to extract information about their technology stack, "
        "products, team, and business model."
    )
    args_schema: Type[BaseModel] = CompanyAnalysisInput

    def _run(self, website_url: str, analysis_type: str = "full") -> str:
        """Analyze company website for detailed information"""
        
        try:
            website_content = scrape_tool.run(website_url)
            
            if not website_content:
                return json.dumps({"error": "Could not access website", "url": website_url})
            
            analysis = {
                "website_url": website_url,
                "analysis_type": analysis_type,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "company_info": {},
                "technology": {},
                "products": {},
                "team": {}
            }
            
            # Extract information based on analysis type
            if analysis_type in ["full", "company"]:
                analysis["company_info"] = self._extract_company_info(website_content)
            
            if analysis_type in ["full", "technology"]:
                analysis["technology"] = self._extract_technology_info(website_content)
            
            if analysis_type in ["full", "products"]:
                analysis["products"] = self._extract_product_info(website_content)
            
            if analysis_type in ["full", "team"]:
                analysis["team"] = self._extract_team_info(website_content)
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e), "url": website_url})
    
    def _extract_company_info(self, content: str) -> Dict:
        """Extract basic company information"""
        info = {}
        content_lower = content.lower()
        
        # Extract company description
        if "about" in content_lower or "mission" in content_lower:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in ['about us', 'our mission', 'what we do']):
                    description_lines = lines[i:i+3]
                    info["description"] = ' '.join(description_lines).strip()[:500]
                    break
        
        # Extract founding year
        founded_match = re.search(r'founded.{0,20}(\d{4})', content_lower)
        if founded_match:
            info["founded_year"] = founded_match.group(1)
        
        # Extract location
        location_patterns = ['headquarters', 'based in', 'located in', 'hq']
        for pattern in location_patterns:
            if pattern in content_lower:
                location_match = re.search(f'{pattern}.{{0,50}}', content_lower)
                if location_match:
                    info["location_hint"] = location_match.group(0)
                    break
        
        return info
    
    def _extract_technology_info(self, content: str) -> Dict:
        """Extract technology stack information"""
        tech_info = {}
        content_lower = content.lower()
        
        # AI/ML technologies
        ai_techs = ['artificial intelligence', 'machine learning', 'deep learning', 
                   'neural network', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
                   'transformer', 'llm', 'generative ai']
        
        found_techs = [tech for tech in ai_techs if tech in content_lower]
        tech_info["ai_technologies"] = found_techs
        
        # Development frameworks
        frameworks = ['react', 'python', 'javascript', 'node.js', 
                     'django', 'flask', 'fastapi', 'kubernetes', 'docker']
        
        found_frameworks = [framework for framework in frameworks if framework in content_lower]
        tech_info["frameworks"] = found_frameworks
        
        return tech_info
    
    def _extract_product_info(self, content: str) -> Dict:
        """Extract product and service information"""
        product_info = {}
        content_lower = content.lower()
        
        # Product descriptions
        if "product" in content_lower or "service" in content_lower:
            lines = content.split('\n')
            product_descriptions = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['our product', 'our service', 'platform', 'solution']):
                    product_descriptions.append(line.strip()[:200])
            
            product_info["descriptions"] = product_descriptions[:3]
        
        # Business model hints
        if any(keyword in content_lower for keyword in ['pricing', 'subscription', 'saas', 'api']):
            product_info["business_model_hint"] = "SaaS/API based"
        
        return product_info
    
    def _extract_team_info(self, content: str) -> Dict:
        """Extract team and leadership information"""
        team_info = {}
        content_lower = content.lower()
        
        leadership_titles = ['ceo', 'cto', 'founder', 'co-founder', 'president']
        found_leaders = []
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for title in leadership_titles:
                if title in line_lower and len(line.strip()) > 10:
                    found_leaders.append(line.strip()[:150])
                    break
        
        team_info["leadership_mentions"] = found_leaders[:5]
        return team_info

class FundingResearchTool(BaseTool):
    name: str = "funding_research_tool"
    description: str = (
        "Research funding information for a company by searching through various "
        "funding databases and news sources."
    )
    args_schema: Type[BaseModel] = FundingResearchInput

    def _run(self, company_name: str, website_url: Optional[str] = None) -> str:
        """Research funding information for a company"""
        
        funding_queries = [
            f'"{company_name}" funding round investment',
            f'"{company_name}" Series A venture capital',
            f'"{company_name}" raised million funding',
            f'site:crunchbase.com "{company_name}"'
        ]
        
        funding_info = {
            "company_name": company_name,
            "website_url": website_url,
            "funding_data": [],
            "total_searches": len(funding_queries)
        }
        
        for query in funding_queries:
            try:
                search_result = website_search_tool.run(query)
                if search_result:
                    funding_data = self._extract_funding_info(search_result, company_name)
                    if funding_data:
                        funding_info["funding_data"].extend(funding_data)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Funding search error for {company_name}: {e}")
                continue
        
        funding_info["funding_data"] = self._deduplicate_funding_data(funding_info["funding_data"])
        
        return json.dumps(funding_info, indent=2)
    
    def _extract_funding_info(self, content: str, company_name: str) -> List[Dict]:
        """Extract funding information from search results"""
        funding_data = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if company_name.lower() in line.lower() and any(keyword in line.lower() for keyword in ['funding', 'raised', 'investment', 'million', 'series']):
                
                amount_match = re.search(r'\$?(\d+(?:\.\d+)?)\s*(million|billion|k)', line.lower())
                funding_round = re.search(r'(series [a-z]|seed|pre-seed)', line.lower())
                
                funding_entry = {
                    "description": line[:200],
                    "amount": amount_match.group(0) if amount_match else None,
                    "round_type": funding_round.group(0) if funding_round else None,
                    "source_line": line
                }
                
                funding_data.append(funding_entry)
        
        return funding_data
    
    def _deduplicate_funding_data(self, funding_data: List[Dict]) -> List[Dict]:
        """Remove duplicate funding entries - FIXED VERSION"""
        unique_data = []
        seen_descriptions = set()
        
        for entry in funding_data:
            desc = entry.get("description", "")[:100].lower()  # Initialize desc properly
            if desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_data.append(entry)
        
        return unique_data[:10]


class LinkedInSearchTool(BaseTool):
    name: str = "linkedin_search_tool"
    description: str = (
        "Search for LinkedIn profiles of company executives and technical leaders."
    )
    args_schema: Type[BaseModel] = LinkedInSearchInput

    def _run(self, person_name: str, company_name: str, role_title: str = "CTO") -> str:
        """Search for LinkedIn profiles of company leadership"""
        
        search_queries = [
            f'"{person_name}" {role_title} "{company_name}" site:linkedin.com',
            f'"{person_name}" "{company_name}" LinkedIn',
            f'{company_name} {role_title} team leadership'
        ]
        
        profile_info = {
            "person_name": person_name,
            "company_name": company_name,
            "role_title": role_title,
            "profiles_found": []
        }
        
        for query in search_queries:
            try:
                search_result = website_search_tool.run(query)
                if search_result:
                    profiles = self._extract_profile_info(search_result, person_name, company_name)
                    profile_info["profiles_found"].extend(profiles)
                time.sleep(2)
            except Exception as e:
                print(f"LinkedIn search error: {e}")
                continue
        
        profile_info["profiles_found"] = self._deduplicate_profiles(profile_info["profiles_found"])
        
        return json.dumps(profile_info, indent=2)
    
    def _extract_profile_info(self, content: str, person_name: str, company_name: str) -> List[Dict]:
        """Extract profile information from search results"""
        profiles = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if (person_name.lower() in line.lower() or company_name.lower() in line.lower()) and len(line) > 20:
                
                linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', line.lower())
                
                profile_entry = {
                    "description": line[:200],
                    "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
                    "relevance_score": self._calculate_profile_relevance(line, person_name, company_name)
                }
                
                if profile_entry["relevance_score"] > 0:
                    profiles.append(profile_entry)
        
        return profiles
    
    def _calculate_profile_relevance(self, text: str, person_name: str, company_name: str) -> int:
        """Calculate relevance score for a profile match"""
        score = 0
        text_lower = text.lower()
        
        if person_name.lower() in text_lower:
            score += 3
        if company_name.lower() in text_lower:
            score += 2
        
        role_keywords = ['cto', 'founder', 'ceo', 'technical', 'engineering', 'ai']
        for keyword in role_keywords:
            if keyword in text_lower:
                score += 1
        
        return score
    
    def _deduplicate_profiles(self, profiles: List[Dict]) -> List[Dict]:
        """Remove duplicate profile entries"""
        unique_profiles = []
        seen_urls = set()
        seen_descriptions = set()
        
        profiles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        for profile in profiles:
            url = profile.get("linkedin_url")
            desc = profile.get("description", "")[:100]
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
            elif not url and desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_profiles.append(profile)
        
        return unique_profiles[:5]


__all__ = [
    'StartupDiscoveryTool',
    'CompanyAnalysisTool', 
    'FundingResearchTool',
    'LinkedInSearchTool',
    'scrape_tool',
    'website_search_tool'
]