import requests
import json
from collections import defaultdict
requests.packages.urllib3.disable_warnings()

QUIZ_URL = "https://jsonkeeper.com/b/LLQT"
SUBMISSION_URL = "https://api.jsonserve.com/rJvd7g"
HISTORICAL_URL = "https://api.jsonserve.com/XgAgFJ"
def fetch_data(url):
    try:
        print(f"\n🔍 Attempting to fetch data from: {url}")
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ Successfully fetched data")
            return response.json()
        else:
            print(f"❌ Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"🚨 Error fetching {url}: {str(e)}")
        return None




def analyze_performance(quiz_data, submission_data):
    print("\n🔬 Starting performance analysis")
    print("📦 Quiz data type:", type(quiz_data))
    print("📦 Submission data type:", type(submission_data))
    
    if not all([quiz_data, submission_data]):
        print("❌ Missing data for analysis")
        return None


    try:
      
        questions = []
        
        if isinstance(quiz_data, dict):
            if 'quiz' in quiz_data:
                quiz_data = quiz_data['quiz']
            
            if 'questions' in quiz_data:
                questions = quiz_data['questions']
            else:
                questions = [quiz_data]
                
        elif isinstance(quiz_data, list):
            questions = quiz_data
        else:
            print("⚠️ Unsupported quiz data format")
            return None

        question_id_map = {}
        for idx, q in enumerate(questions, 1):
            if not isinstance(q, dict):
                print(f"⚠️ Skipping invalid question format at position {idx}")
                continue

            q_id = str(q.get('question_id') or q.get('id') or q.get('qid') or f"generated_{idx}").strip()
            
            
            clean_id = ''.join(c for c in q_id if c.isalnum())
            variants = {clean_id, clean_id.lower(), clean_id.upper()}
            
            for variant in variants:
                if variant:
                    question_id_map[variant] = q

            

        print(f"\n📋 Total Mapped Questions: {len(question_id_map)}")
        print("Sample Question IDs:", list(question_id_map.keys())[:3])

        response_map = submission_data.get('response_map') or \
                      submission_data.get('responses') or \
                      submission_data.get('answers', {})
        
        print("\n🔍 Response Map Sample:")
        print(dict(list(response_map.items())[:3]))

        analysis = defaultdict(lambda: {'correct': 0, 'total': 0, 'accuracy': 0.0})
        matched_questions = 0

        for q_id_str, selected_option in response_map.items():
            clean_response_id = ''.join(c for c in str(q_id_str) if c.isalnum()).strip()
            
            question = None
            for variant in [clean_response_id, 
                           clean_response_id.lower(), 
                           clean_response_id.upper()]:
                question = question_id_map.get(variant)
                if question: break

            if not question:
                print(f"⚠️ No match for response ID: {clean_response_id}")
                continue

            correct_id = None
            if 'options' in question:
                correct_option = next(
                    (opt for opt in question['options'] 
                     if opt.get('is_correct') or opt.get('correct')), 
                    None
                )
                if correct_option:
                    correct_id = str(correct_option.get('id') or 
                                    correct_option.get('option_id'))
            else:
                for k in ['correct_option_id', 'correct_answer_id', 
                         'correctId', 'answer']:
                    if k in question:
                        correct_id = str(question[k]).strip()
                        break

            if not correct_id:
                print(f"⚠️ Couldn't find correct answer for QID: {clean_response_id}")
                continue

            matched_questions += 1
            is_correct = str(selected_option).strip() == correct_id
            
            topic = question.get('topic') or \
                   question.get('subject') or \
                   question.get('tags', {}).get('topic', 'General')
                   
            difficulty = question.get('difficulty', 'Medium').capitalize()

            analysis['overall']['total'] += 1
            analysis['overall']['correct'] += int(is_correct)
            
            analysis[topic]['total'] += 1
            analysis[topic]['correct'] += int(is_correct)
            
            analysis[difficulty]['total'] += 1
            analysis[difficulty]['correct'] += int(is_correct)

        for key in analysis:
            if analysis[key]['total'] > 0:
                analysis[key]['accuracy'] = round(
                    (analysis[key]['correct'] / analysis[key]['total']) * 100, 2
                )

        print(f"\n🔍 Final Match Results: {matched_questions}/{len(response_map)}")

        print("\n📊 Processed Questions Metadata:")
        print(f"Total questions: {len(questions)}")
        print("First question keys:", list(questions[0].keys()) if questions else "None")

        print("\n📊 Response Map Analysis:")
        print(f"Total responses: {len(response_map)}")
        print("Sample response entry:", {k: response_map[k] for k in list(response_map.keys())[:1]})


        return dict(analysis) if matched_questions > 0 else None

    except Exception as e:
        print(f"⚠️ Critical analysis error: {str(e)}")
        return None
    

def generate_recommendations(analysis):
    """Generate AI-powered recommendations with performance insights"""
    if not analysis:
        return []
    
    recommendations = []
    
    topic_performance = [
        (k, v) for k, v in analysis.items() 
        if k not in ['overall', 'difficulty', 'Unknown']
    ]
    
    weak_topics = sorted(
        [t for t in topic_performance if t[1]['accuracy'] < 65],
        key=lambda x: x[1]['accuracy']
    )[:3]
    
    if weak_topics:
        rec = "🔴 Critical Weaknesses:\n" + "\n".join(
            [f"- {t[0]} ({t[1]['accuracy']}%)" for t in weak_topics]
        )
        recommendations.append(rec)
    
    difficulty_levels = ['Easy', 'Medium', 'Hard']
    diff_performance = [
        (d, analysis.get(d, {'accuracy': 0})) 
        for d in difficulty_levels
    ]
    
    weakest_diff = min(diff_performance, key=lambda x: x[1]['accuracy'])
    recommendations.append(
        f"⚡ Max Improvement Potential: {weakest_diff[0]} level questions "
        f"(Current accuracy: {weakest_diff[1]['accuracy']}%)"
    )
    
    recommendations.append(
        "⏳ Practice Recommendation: Schedule focused study sessions "
        "3 times weekly for weak topics"
    )
    

    return recommendations


import requests
import json
from collections import defaultdict
from statistics import mean

def analyze_historical(historical_data):
    trends = {
        'accuracy': [],
        'topics': defaultdict(lambda: {'accuracy': [], 'attempts': []}),
        'difficulty': defaultdict(lambda: {'accuracy': [], 'attempts': []}),
        'time_series': []
    }

    for quiz in historical_data[-5:]:
        if not isinstance(quiz, dict):
            continue
            
        accuracy = float(quiz.get('accuracy', '0%').strip('% '))
        
        topic = quiz.get('type') or quiz.get('topic', 'General')
        
        trends['accuracy'].append(accuracy)
        trends['topics'][topic]['accuracy'].append(accuracy)
        trends['time_series'].append({
            'date': quiz.get('submitted_at'),
            'accuracy': accuracy
        })

    trends['avg_accuracy'] = round(mean(trends['accuracy']), 2) if trends['accuracy'] else 0
    return trends


def self_calculate_improvement(accuracy_list):
    if len(accuracy_list) < 2:
        return 0
    return round(((accuracy_list[-1] - accuracy_list[0]) / accuracy_list[0]) * 100, 2)

def self_calculate_trend(values, window=3):
    if len(values) < window:
        return 'insufficient data'
    
    recent = mean(values[-window:])
    previous = mean(values[:-window]) if len(values) > window else recent
    return 'improving' if recent > previous else 'declining' if recent < previous else 'stable'


def generate_recommendations(analysis, historical_trends):
    recs = []
    
    weak_topics = [t for t in analysis.items() 
                  if t[1]['accuracy'] < 70 and t[0] != 'overall']
    if weak_topics:
        recs.append("🔴 Immediate Focus Areas:")
        recs.extend([f"- {t[0]} ({t[1]['accuracy']}%)" for t in weak_topics[:3]])
    
    if historical_trends:
        current_acc = analysis['overall']['accuracy']
        trend = "↑ Improving" if current_acc > historical_trends['avg_accuracy'] else "↓ Needs Work"
        recs.append(f"\n📈 Performance Trend: {trend}")
        recs.append(f"   Current: {current_acc}% | Average: {historical_trends['avg_accuracy']}%")
    
    recs.append("\n🎯 Recommended Strategy:")
    recs.append("- 30 mins daily on weak topics")
    recs.append("- Weekly mixed difficulty quizzes")
    
    return recs



from groq import Groq
import os
import textwrap

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_ai_recommendations(analysis, historical_trends):
    """Generate AI-powered recommendations using Groq API"""
    if not analysis:
        return []
    
    performance_data = {
        "current_performance": {
            "weak_topics": [
                {"topic": k, "accuracy": v['accuracy']} 
                for k, v in analysis.items() 
                if v['accuracy'] < 70 and k not in ['overall', 'Easy', 'Medium', 'Hard']
            ],
            "difficulty_performance": {
                level: analysis.get(level, {}).get('accuracy', 0)
                for level in ['Easy', 'Medium', 'Hard']
            },
            "overall_accuracy": analysis['overall']['accuracy']
        },
        "historical_insights": {
            "average_accuracy": historical_trends.get('avg_accuracy', 0),
            "accuracy_trend": self_calculate_trend(historical_trends.get('accuracy', [])),
            "improvement_rate": self_calculate_improvement(historical_trends.get('accuracy', []))
        },
        "metadata": {
            "total_questions_attempted": analysis['overall']['total'],
            "recent_quiz_count": len(historical_trends.get('accuracy', []))
        }
    }

    prompt = textwrap.dedent(f"""
    **Student Performance Analysis Report**
    
    Analyze this quiz performance data and generate personalized recommendations:
    {json.dumps(performance_data, indent=2)}
    
    Consider these aspects:
    1. Identify patterns in weak topics and suggest specific study strategies
    2. Recommend difficulty-level adjustments based on current performance
    3. Propose time management strategies based on historical trends
    4. Suggest resource types (videos, practice questions, diagrams) for weak areas
    5. Create a weekly study plan template based on the findings
    
    Format recommendations with:
    - Clear section headers
    - Bullet points for actions
    - Emoji icons for visual organization
    - Measurable goals and timelines
    """)

    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        recommendations = chat_completion.choices[0].message.content
        return recommendations.split("\n")
    
    except Exception as e:
        print(f"⚠️ AI Recommendation Error: {str(e)}")
        return []

if __name__ == "__main__":
    current_quiz = fetch_data(QUIZ_URL)
    current_submission = fetch_data(SUBMISSION_URL)
    historical_data = fetch_data(HISTORICAL_URL) or []
    
    current_analysis = analyze_performance(current_quiz, current_submission)
    historical_trends = analyze_historical(historical_data)
    
    print(f"\n📊 Current Accuracy: {current_analysis['overall']['accuracy']}%")
    recommendations = generate_recommendations(current_analysis, historical_trends)
    
    print("\n🚀 Actionable Recommendations:")
    print('\n'.join(recommendations))
    current_quiz = fetch_data(QUIZ_URL)
    current_submission = fetch_data(SUBMISSION_URL)
    
    print("\n📚 Fetching historical data...")
    raw_historical = fetch_data(HISTORICAL_URL)
    
    if isinstance(raw_historical, list):
        historical_data = raw_historical  
    elif isinstance(raw_historical, dict):
        historical_data = raw_historical.get('historical', [])  
    else:
        historical_data = []
    
    print(f"Loaded {len(historical_data)} historical quizzes")

    
    current_analysis = analyze_performance(current_quiz, current_submission)
    historical_trends = analyze_historical(historical_data)
    
    if current_analysis:
        print(f"\n📊 Current Accuracy: {current_analysis['overall']['accuracy']}%")
        recommendations = generate_recommendations(current_analysis, historical_trends)
        
        print("\n🚀 Personalized Recommendations:")
        for rec in recommendations:
            print(f"• {rec}")

    ai_recommendations = generate_ai_recommendations(current_analysis, historical_trends)
    
    print("\n🤖 AI-Powered Recommendations:")
    for line in ai_recommendations:
        print(line)