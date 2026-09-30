from collections import defaultdict
import os
from app.classification.rules import KEYWORD_RULES, COMPANY_DOMAIN_MAP, TICKET_ID_PATTERN
from app.classification.llm_classifier import classify_llm
from dotenv import load_dotenv

load_dotenv()
def classify_rule_based(subject: str, body: str) -> dict[str, float]:
    """
    Score each category by counting how many of its keywords appear
    (case-insensitive) in `subject + " " + body`.
    Return (best_category, confidence) where confidence =
    matches / total_keywords_in_that_category, capped at 1.0.
    If nothing scores above 0, return ("junk", 0.0).
    """
    context= subject + " " + body
    count_dict=defaultdict(int)
    
    for category,keywords in KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword.lower() in context.lower():
                count_dict[category] += 1
        count_dict[category]= calculate_confidence(count_dict[category],len(keywords))
            
    max_key = max(count_dict, key=count_dict.get)
    if count_dict[max_key] == 0.0:
        return {"category": "junk" ,"confidence": 0.0 }
       
        
    return {"category": max_key,"confidence": count_dict[max_key]}

def calculate_confidence(score: int, n: int):
    confidence = score/n
    return confidence

def extract_entities(sender: str, subject: str, body: str) -> dict:
    """
    Pull `company` from COMPANY_DOMAIN_MAP using the sender's domain
    (fallback: the raw domain string if not in the map).
    Pull `ticket_ref` via TICKET_ID_PATTERN.search on subject+body
    (fallback: None).
    Return {"company": ..., "ticket_ref": ...}
    """
    domain = sender.split("@")[-1].lower()
    company = COMPANY_DOMAIN_MAP.get(domain, domain)

    match = TICKET_ID_PATTERN.search(subject + " " + body)
    ticket_ref = match.group() if match else None

    return {"company": company, "ticket_ref": ticket_ref}

def classify(subject: str, body: str) -> dict:
    """
    Read CLASSIFIER_BACKEND from the environment (default "rule").
    If it's "llm": try classify_llm(subject, body).
    If that raises ANY exception, log a warning (just print() is fine
    for now) with the exception message, then fall back to
    classify_rule_based(subject, body) instead of letting it crash.
    If CLASSIFIER_BACKEND is "rule" (or anything else/unset),
    just call classify_rule_based directly.
    """
    classifier=os.environ.get("CLASSIFIER_BACKEND")

    if classifier == "llm":
        try:
            response = classify_llm(subject,body)
        except Exception as e:
            print(f"There was an error reaching LLM {e}")
            response = classify_rule_based(subject,body)

    else:
        response = classify_rule_based(subject,body)

    return response