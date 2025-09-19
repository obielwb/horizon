import os

class Config:
    """Configuration settings for the startup discovery system"""
    
    # API Keys (get from environment variables)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    
    RESEND_API_KEY=os.getenv("RESEND_API_KEY", "your-resend-api-key")
    
    # Target Countries for startup discovery
    TARGET_COUNTRIES = [
        "Brazil", "Mexico", "Argentina", "Chile", "Colombia", 
        "Peru", "Uruguay", "Costa Rica", "Ecuador", "Panama"
    ]
    
    # AI Technologies to look for
    AI_TECHNOLOGIES = [
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Reinforcement Learning", "Neural Networks",
        "Generative AI", "LLMs", "Computer Graphics", "Data Analytics",
        "Predictive Analytics", "Speech Recognition", "Robotics",
        "Autonomous Systems", "AI Infrastructure", "MLOps"
    ]
    
    # Market Sectors
    MARKET_SECTORS = [
        "FinTech", "HealthTech", "EdTech", "AgTech", "RetailTech",
        "LegalTech", "PropTech", "InsurTech", "LogisticsTech",
        "MarketingTech", "HRTech", "Gaming", "Entertainment",
        "Manufacturing", "Energy", "Transportation", "Security"
    ]
    
    # Funding Stages
    FUNDING_STAGES = [
        "Pre-Seed", "Seed", "Series A", "Series B", "Series C",
        "Series D+", "Growth", "IPO", "Acquisition"
    ]
    
    # Key VC firms in Latin America
    LATAM_VCS = [
        "Kaszek Ventures", "Monashees", "MAYA Capital", "QED Investors",
        "Riverwood Capital", "Tiger Global", "SoftBank", "Andreessen Horowitz",
        "General Atlantic", "Goldman Sachs", "Sequoia Capital",
        "Battery Ventures", "Insight Partners"
    ]
    
    # Scoring weights for startup evaluation
    SCORING_WEIGHTS = {
        "technology_innovation": 0.25,
        "market_potential": 0.20,
        "team_strength": 0.20,
        "funding_attractiveness": 0.15,
        "nvidia_alignment": 0.10,
        "traction": 0.10
    }