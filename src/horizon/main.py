#!/usr/bin/env python
import sys
import warnings

from datetime import datetime


from .config import Config
from .crew import Horizon  

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    print("🤖 NVIDIA Inception AI Startup Discovery System")
    print("=" * 60)
    
    if Config.OPENAI_API_KEY == "your-openai-api-key":
        print("⚠️  Warning: OPENAI_API_KEY not configured")
        return
    
    resend_api_key = Config.RESEND_API_KEY
    if resend_api_key == 'your-resend-api-key':
        print("⚠️  Warning: RESEND_API_KEY not configured")
        print("     Set RESEND_API_KEY environment variable to enable email sending")
        print("     Proceeding without email functionality...")
    

    recipient_emails = [
        "gabriel.bartmanovicz@sou.inteli.edu.br",
    ]
    
    specific_ventures = [
        "MAYA Capital", "QED Investors",
    ]
    target_countries = ["Mexico", "Brazil"]
  
    
    print(f"✅ Proceeding with: {', '.join(target_countries)}")
    print()
    

    try:
        discovery_system = Horizon()
        
        if len(target_countries) == 1:
            # Single country discovery with optional specific ventures
            results = discovery_system.discover_country(
                target_countries[0], 
                specific_ventures=specific_ventures
            )
        else:
            # Multi-country discovery
            # For multiple countries, apply same ventures to all countries
            # You could enhance this to support per-country ventures
            specific_ventures_per_country = None
            if specific_ventures:
                specific_ventures_per_country = {
                    country: specific_ventures for country in target_countries
                }
            
            results = discovery_system.discover_multiple_countries(
                target_countries,
                specific_ventures_per_country=specific_ventures_per_country
            )
            


        if False:
            # Extract task results for email
            task_results = {}
            
            # Handle different result structures based on your crew implementation
            if hasattr(results, 'tasks_output') and results.tasks_output:
                # Process task outputs
                for i, task_output in enumerate(results.tasks_output):
                    # Use the task description as key, or create a generic one
                    if hasattr(task_output, 'description'):
                        task_key = task_output.description
                    else:
                        task_key = f"Task_{i + 1}"
                    
                    # Get the raw output
                    if hasattr(task_output, 'raw'):
                        task_results[task_key] = task_output.raw
                    elif hasattr(task_output, 'result'):
                        task_results[task_key] = task_output.result
                    else:
                        task_results[task_key] = str(task_output)
                
                # Add completion summary
                task_results['total_tasks'] = len(results.tasks_output)
                task_results['completion_status'] = 'success'
                
            elif hasattr(results, 'raw') and results.raw:
                # Handle single result with raw output
                task_results['Discovery Results'] = results.raw
                task_results['total_tasks'] = 1
                task_results['completion_status'] = 'success'
                
            elif isinstance(results, dict):
                # Handle results as dictionary
                task_results = results.copy()
                if 'total_tasks' not in task_results:
                    task_results['total_tasks'] = len([k for k in task_results.keys() if not k.startswith('_')])
                if 'completion_status' not in task_results:
                    task_results['completion_status'] = 'success'
                    
            else:
                # Fallback: convert results to string
                task_results = {
                    'Discovery Results': str(results),
                    'total_tasks': 1,
                    'completion_status': 'success'
                }
            
            # Send email only if we have meaningful task results
            if len(task_results) > 2:  # More than just total_tasks and completion_status
                print("📧 Sending email with formatted results...")
                
                email_sender = NVIDIAEmailSender(resend_api_key)
                
                email_result = email_sender.send_report_email(
                    task_results=task_results,
                    to_emails=recipient_emails,
                    subject=f"NVIDIA Inception AI Startup Discovery Report - {target_countries[0]} - {datetime.now().strftime('%Y-%m-%d')}",
                    from_email=Config.RESEND_FROM_EMAIL
                )
                
                if email_result['success']:
                    print(f"✅ Email sent successfully to: {', '.join(recipient_emails)}")
                    print(f"📧 Email ID: {email_result.get('email_id')}")
                else:
                    print(f"❌ Email sending failed: {email_result.get('error')}")
                    print("     Check your Resend API key and domain verification")
            else:
                print("⚠️  No meaningful task results found to email")
                print("     Results structure may have changed - check crew implementation")
        
        
        print("\n🎉 Startup Discovery Complete!")
        print("📁 Check the generated files for detailed results:")
        print("   - JSON files: Complete structured data")
        print("   - CSV files: Spreadsheet-friendly format") 
        print("   - Markdown files: Human-readable summaries")
        
        return results
        
    except Exception as e:
        print(f"❌ Error running startup discovery: {e}")
        raise
    
    
    


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        # CHANGED: Use StartupDiscoverySystem instead of Horizon
        Horizon().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        # CHANGED: Use StartupDiscoverySystem instead of Horizon
        Horizon().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        # CHANGED: Use StartupDiscoverySystem instead of Horizon
        Horizon().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")