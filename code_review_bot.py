# AI Code Review Bot
# Analyzes Python code for bugs, style issues, security vulnerabilities, and improvements

import ast
import re
import openai
from datetime import datetime

openai.api_key = "YOUR_OPENAI_API_KEY"

# ============================================================
# 1. STATIC CODE ANALYZER (rule-based)
# ============================================================
def static_analyze(code: str) -> list:
    """Perform rule-based static code analysis."""
    issues = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        # Check for hardcoded passwords/keys
        if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']{4,}', line, re.IGNORECASE):
            issues.append({"line": i, "severity": "HIGH", "type": "Security",
                           "message": "Hardcoded credential detected. Use environment variables."})

        # Check for bare except
        if re.match(r'\s*except\s*:', line):
            issues.append({"line": i, "severity": "MEDIUM", "type": "Best Practice",
                           "message": "Bare 'except:' clause catches all exceptions. Specify exception type."})

        # Check for print statements (should use logging)
        if re.match(r'\s*print\s*\(', line):
            issues.append({"line": i, "severity": "LOW", "type": "Style",
                           "message": "Use logging module instead of print() for production code."})

        # Check for TODO comments
        if 'TODO' in line or 'FIXME' in line or 'HACK' in line:
            issues.append({"line": i, "severity": "LOW", "type": "Maintenance",
                           "message": f"Found TODO/FIXME comment: {line.strip()}"})

        # Check for very long lines
        if len(line) > 120:
            issues.append({"line": i, "severity": "LOW", "type": "Style",
                           "message": f"Line too long ({len(line)} chars). PEP8 recommends max 79."})

    return issues


# ============================================================
# 2. AST SYNTAX CHECKER
# ============================================================
def check_syntax(code: str) -> dict:
    """Check Python syntax validity using AST."""
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}


# ============================================================
# 3. AI REVIEW using LLM (optional - requires API key)
# ============================================================
def ai_review(code: str) -> str:
    """Use GPT to provide intelligent code review feedback."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a senior software engineer. Review the following Python code. Identify: 1) Bugs, 2) Security issues, 3) Performance issues, 4) Style violations. Be specific with line references. Format as a structured review."},
            {"role": "user", "content": f"Review this Python code:\n```python\n{code}\n```"}
        ]
    )
    return response.choices[0].message.content


# ============================================================
# 4. FULL REVIEW PIPELINE
# ============================================================
def review_code(code: str, filename: str = "code.py") -> dict:
    """Run complete code review pipeline."""
    print(f"\nAI CODE REVIEWER - Analyzing: {filename}")
    print(f"{'='*60}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Lines of Code: {len([l for l in code.split(chr(10)) if l.strip()])}")

    # Syntax check
    syntax = check_syntax(code)
    print(f"\n[SYNTAX CHECK]")
    print(f"  Status: {'PASS' if syntax['valid'] else 'FAIL - ' + str(syntax['error'])}")

    # Static analysis
    issues = static_analyze(code)
    print(f"\n[STATIC ANALYSIS] - {len(issues)} issue(s) found")
    for issue in issues:
        severity_symbol = {"HIGH": "[!]", "MEDIUM": "[~]", "LOW": "[-]"}[issue['severity']]
        print(f"  {severity_symbol} Line {issue['line']:3d} | {issue['severity']:6s} | {issue['type']:15s} | {issue['message']}")

    return {"syntax": syntax, "issues": issues}


# ============================================================
# DEMO OUTPUT
# ============================================================
if __name__ == "__main__":
    SAMPLE_CODE = '''
import requests

api_key = "sk-secret1234567890"  # TODO: move to env

def get_user_data(user_id):
    try:
        response = requests.get(f"https://api.example.com/users/{user_id}")
        data = response.json()
        print(f"Fetched user: {data['name']}")
        return data
    except:
        print("Error occurred")
        return None

def process_users(user_ids):
    results = []
    for uid in user_ids:
        user = get_user_data(uid)
        if user != None:  # FIXME: use 'is not None'
            results.append(user)
    return results
'''

    result = review_code(SAMPLE_CODE, "sample_code.py")

    print(f"\n{'='*60}")
    print("REVIEW SUMMARY")
    print(f"{'='*60}")
    high = sum(1 for i in result['issues'] if i['severity'] == 'HIGH')
    med  = sum(1 for i in result['issues'] if i['severity'] == 'MEDIUM')
    low  = sum(1 for i in result['issues'] if i['severity'] == 'LOW')
    print(f"  HIGH   issues: {high}  (Must fix immediately)")
    print(f"  MEDIUM issues: {med}  (Should fix)")
    print(f"  LOW    issues: {low}  (Nice to fix)")
    print(f"  TOTAL  issues: {len(result['issues'])}")
    total_score = max(0, 100 - (high * 20 + med * 10 + low * 2))
    print(f"\n  CODE QUALITY SCORE: {total_score}/100")
    print(f"{'='*60}")
