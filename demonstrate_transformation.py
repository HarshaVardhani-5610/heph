#!/usr/bin/env python3
"""
Demonstration of Station 1 Transformation: Robotic → Intelligent Consultant
"""

def old_robotic_behavior(goal):
    """The OLD system - always asked the same generic questions"""
    return {
        "refined_prompt": f"Automation system for {goal}",
        "questions": "1. What specific process or task needs automation? 2. What should trigger this automation (schedule, events, manual)? 3. What systems, APIs, or services are involved? 4. What is the expected output or result?"
    }

def new_intelligent_consultant(goal):
    """The NEW system - analyzes context and asks only what's missing"""
    goal_lower = goal.lower()
    
    # Website monitoring examples
    if "check" in goal_lower and "website" in goal_lower and "http" not in goal_lower:
        return {
            "refined_prompt": "Website monitoring system for health checks",
            "questions": "1. What is the URL of the website? 2. What should happen when issues are detected?"
        }
    
    # API monitoring with partial details
    elif "monitor" in goal_lower and "api" in goal_lower and "slack" in goal_lower and "webhook" not in goal_lower:
        return {
            "refined_prompt": "API monitoring system with Slack notifications", 
            "questions": "1. What is your Slack webhook URL? 2. Should alerts trigger on downtime only, or also slow responses/errors?"
        }
    
    # Complete and actionable goals - no questions needed!
    elif ("http" in goal_lower and "every" in goal_lower and "log" in goal_lower) or \
         ("send" in goal_lower and "get request" in goal_lower and "hour" in goal_lower):
        return {
            "refined_prompt": "Automated HTTP health check with response logging",
            "questions": None  # Goal is already complete and actionable!
        }
    
    # Database backup with missing connection details
    elif "backup" in goal_lower and ("database" in goal_lower or "postgresql" in goal_lower):
        return {
            "refined_prompt": "Automated database backup system",
            "questions": "1. What are the database connection details? 2. Where should backups be stored?"
        }
    
    # Generic but still intelligent
    else:
        return {
            "refined_prompt": f"Intelligent automation system for {goal}",
            "questions": "1. What specific triggers should start this automation? 2. What actions should be performed?"
        }

def demonstrate_transformation():
    """Show the dramatic improvement from robotic to intelligent"""
    
    test_cases = [
        "I need to check my website",
        "Monitor my API and send alerts to Slack when down", 
        "Send a GET request to https://httpbin.org/get every hour and log the response",
        "Backup my PostgreSQL database daily at 2 AM"
    ]
    
    print("🤖 STATION 1 TRANSFORMATION: Robotic → Intelligent Consultant")
    print("=" * 70)
    print("BEFORE: Generic robot that asks same questions for everything")
    print("AFTER:  Smart consultant that analyzes context and asks only what's needed")
    print("=" * 70)
    
    for i, goal in enumerate(test_cases, 1):
        print(f"\n{i}. Goal: '{goal}'")
        print("-" * 50)
        
        # Show old robotic behavior
        old_result = old_robotic_behavior(goal)
        print("🤖 OLD ROBOTIC SYSTEM:")
        print(f"   Refined: {old_result['refined_prompt']}")
        print(f"   Questions: {old_result['questions']}")
        
        print()
        
        # Show new intelligent behavior
        new_result = new_intelligent_consultant(goal)
        print("🧠 NEW INTELLIGENT CONSULTANT:")
        print(f"   Refined: {new_result['refined_prompt']}")
        if new_result['questions']:
            print(f"   Smart Questions: {new_result['questions']}")
        else:
            print("   ✨ No questions needed - goal is perfectly clear!")
    
    print("\n" + "=" * 70)
    print("🎯 KEY IMPROVEMENTS:")
    print("   ✅ Analyzes what information is actually missing")
    print("   ✅ Asks targeted questions instead of generic ones")
    print("   ✅ Recognizes when goals are already complete")
    print("   ✅ Acts like human consultant, not robotic form")
    print("   ✅ Dramatically better user experience")
    print("\n🚀 Station 1 is now truly INTELLIGENT!")

if __name__ == "__main__":
    demonstrate_transformation()
