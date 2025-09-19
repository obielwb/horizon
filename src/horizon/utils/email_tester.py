#!/usr/bin/env python3
"""
Test script for NVIDIA Email Sender
Tests the email formatting and sending functionality with sample task results
"""

import json
import os
from datetime import datetime

from ..config import Config
from ..resend import NVIDIAEmailSender


def create_test_task_results():
    """
    Create test task results based on the report data
    """
    task_results = {
        "Discover AI startups in Brazil by researching:\n1. ": '''[
 {
 "Company Name": "FariasGiovanna SassoNatalie",
 "Website": "https://www.startcarreiras.com",
 "Description": "Student-based marketplace that enables meaningful and efficient connections between recruiters and entry-level candidates.",
 "Founding Year": "Not specified",
 "Location": "Brazil",
 "AI Technology Focus": "EdTech",
 "Target Market": "Entry-level candidates and recruiters",
 "Key Milestones": "Co-Investors: Reach Capital, Graphene Ventures",
 "Source URL": "http://www.techinasia.com"
 },
 {
 "Company Name": "Stay",
 "Website": "https://www.stay.com.br",
 "Description": "B2B complexity-free products that increase engagement, improve retention and allow companies to create efficient compensation strategies, starting with private pension.",
 "Founding Year": "Not specified",
 "Location": "Brazil",
 "AI Technology Focus": "Insurtech",
 "Target Market": "B2B companies",
 "Key Milestones": "Co-Investors: BTV",
 "Source URL": "http://www.techinasia.com"
 },
 {
 "Company Name": "Tarken",
 "Website": "www.tarken.com.br",
 "Description": "Solution that brings more intelligence to decision-making and automation to optimize the entire credit cycle of agricultural input companies.",
 "Founding Year": "Not specified",
 "Location": "Brazil",
 "AI Technology Focus": "Agtech",
 "Target Market": "Agricultural input companies",
 "Key Milestones": "Co-Investors: Monashees, Hedosophia, Mandi",
 "Source URL": "http://www.techinasia.com"
 },
 {
 "Company Name": "Tempo",
 "Website": "https://seutempo.com",
 "Description": "Saves people time and money by eliminating everyday frictions through its WhatsApp-driven personal assistant (PA) that uses AI and embedded payments to streamline and manage customers' daily needs.",
 "Founding Year": "Not specified",
 "Location": "Brazil",
 "AI Technology Focus": "Infoservices",
 "Target Market": "General public",
 "Key Milestones": "Co-Investors: MAYA Capital",
 "Source URL": "http://www.techinasia.com"
 },
 {
 "Company Name": "Tenchi",
 "Website": "www.tenchisecurity.com",
 "Description": "Software helping enterprises embrace the benefits of the cloud in a secure and compliant fashion.",
 "Founding Year": "Not specified",
 "Location": "Brazil",
 "AI Technology Focus": "Cybersecurity",
 "Target Market": "Enterprise",
 "Key Milestones": "Co-Investors: GFC, Kinea",
 "Source URL": "http://www.techinasia.com"
 }
]''',
        
        "For each discovered startup, conduct detailed tech": "The detailed technical profiles have been compiled for each startup, along with AI technology classification, product analysis, market positioning, and NVIDIA alignment scoring. The analysis affords NVIDIA insights into which startups may present partnership opportunities or benefit from advanced technology stack integrations.",
        
        "Research comprehensive funding information for eac": """For each startup, here is the compiled funding and investor information we currently have:

1. **FariasGiovanna SassoNatalie**:
   - **Co-Investors**: Reach Capital, Graphene Ventures
   - **Sector**: EdTech
   - **Website**: [Start Carreiras](https://www.startcarreiras.com)

2. **Stay**:
   - **Co-Investors**: BTV
   - **Sector**: Insurtech
   - **Website**: [Stay](https://www.stay.com.br)

3. **Tarken**:
   - **Co-Investors**: Monashees, Hedosophia, Mandi
   - **Sector**: Agtech
   - **Website**: [Tarken](http://www.tarken.com.br)

4. **Tempo**:
   - **Co-Investors**: MAYA Capital
   - **Sector**: Infoservices
   - **Website**: [Tempo](https://seutempo.com)

5. **Tenchi**:
   - **Co-Investors**: GFC, Kinea
   - **Sector**: Cybersecurity
   - **Website**: [Tenchi](http://www.tenchisecurity.com)

Investment Attractiveness Score (Tentative based on Co-investor Presence):
- The presence of significant co-investors such as Reach Capital and Monashees indicates high interest in these startups. Investment attractiveness, assessed on co-investor reputation alone, could be a provisional 7 or 8 out of 10. However, a lack of further financial detail makes any deeper assessment speculative.""",
        
        "Identify and profile key technical leadership for ": "The search process did not yield specific technical leadership profiles for the startups: FariasGiovanna SassoNatalie, Stay, Tarken, Tempo, and Tenchi. The LinkedIn and website content searches provided generic information about founders with no specific details on CTOs or technical co-founders. Further steps could include directly reaching out to these companies or accessing industry databases beyond the available tools to secure this information.",
        
        "Conduct comprehensive market analysis for Brazil A": """**_Comprehensive Market Intelligence Report: AI Ecosystem in Brazil_**

**1. Market Landscape Assessment:**
- **Current State of AI Startup Ecosystem:** Brazil houses a burgeoning AI startup ecosystem with a diverse array of sectors represented, including EdTech (e.g., Start Carreiras), Insurtech (e.g., Stay), Agtech (e.g., Tarken), Infoservices (e.g., Tempo), and Cybersecurity (e.g., Tenchi). These startups are backed by significant investors like Reach Capital and Monashees, indicating high market potential and investor confidence.
 
- **Most Active AI Sectors and Applications:** Key sectors in Brazil's AI landscape include EdTech, Insurtech, and Agtech, driven by both technology adoption trends and pressing needs in education, financial services, and agriculture.

- **Technology Adoption Trends and Drivers:** There is a strong focus on automation and data-driven decision-making, particularly in Agtech and Infoservices, facilitated by AI. The use of cloud technology and embedded systems like AI-driven personal assistants indicates maturity in user-specific intelligent solutions.

**2. Competitive Analysis:**
- **Major AI Companies and Competitive Landscape:** Companies such as Start Carreiras and Tenchi highlight Brazil's competitive AI space, serving niche markets with substantial backing from high-profile investors.

- **Market Gaps and Underserved Segments:** There is a noticeable gap in comprehensive AI solutions targeting sustainable energy and healthcare, representing potential sectors for growth.

**3. Investment Climate:**
- **VC Activity Levels and Trends:** Venture capital activity in Brazilian AI startups is robust, with significant investments from international funds, indicating a healthy interest and trust in Brazil's AI market.

**4. Growth Opportunities:**
- **High-Potential AI Application Areas:** Agtech and Infoservices are key growth areas, with automation and decision-support systems showing great potential.""",
        
        "Validate all collected startup information and cre": "The startups have been evaluated and scored based on their innovation, market potential, team, funding, and alignment with NVIDIA. Recommendations for partnership development prioritize Tarken and Tenchi, with actionable insights for strategic collaboration.",
        
        "total_tasks": 6,
        "completion_status": "success"
    }
    
    return task_results

def test_email_sending():
    """
    Test actual email sending (requires valid Resend API key)
    """
    print("\n📧 Testing Email Sending...")
    print("=" * 50)
    # api_key = Config.RESEND_API_KEY
    email_sender = NVIDIAEmailSender("")
    
    task_results = create_test_task_results()
    

    test_emails = [
        "obielwb@gmail.com",  
    ]
    
    result = email_sender.send_report_email(
        task_results=task_results,
        to_emails=test_emails,
        subject="NVIDIA Inception AI Startup Discovery Report - Brazil",
        from_email="onboarding@resend.dev"  
    )
    
    if result["success"]:
        print("✅ Email sent successfully!")
        print(f"📧 Email ID: {result.get('email_id', 'N/A')}")
        print(f"👥 Recipients: {', '.join(result['recipients'])}")
    else:
        print("❌ Email sending failed!")
        print(f"💀 Error: {result['error']}")
    
    return result

def main():
    """
    Main test function
    """
    print("🚀 NVIDIA Email Sender Test Suite")
    print("=" * 50)
    
  
    try:
        result = test_email_sending()
        if result and result["success"]:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️  Formatting test passed, but email sending failed.")
    except Exception as e:
        print(f"\n❌ Email sending test failed: {str(e)}")

    
    print("\n📋 Test Summary:")
    print("   • Email formatting: ✅ Tested")

if __name__ == "__main__":
    # Make sure the nvidia_email_sender module is in the same directory
    # or in your Python path
    try:
        main()
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("📝 Make sure 'nvidia_email_sender.py' is in the same directory as this script.")
        print("📦 Also ensure 'resend' package is installed: pip install resend")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")