from app.classification.classifier import classify, extract_entities

def test_urgent_classification():
    result = classify("Site is down!!", "This is critical, ASAP fix needed")
    assert result["category"] == "urgent"

def test_billing_classification():
    result = classify("Invoice question", "Can I get a refund on my last charge?")
    assert result["category"] == "billing"

def test_support_classification():
    result = classify("How do I reset my password", "having an issue logging in")
    assert result["category"] == "support"

def test_junk_classification():
    result = classify("Hey", "just saying hi")
    assert result["category"] == "junk"
    assert result["confidence"] == 0.0

def test_extract_entities_known_company():
    entities = extract_entities("jane@acme.com", "re: #4821", "body text")
    assert entities["company"] == "Acme Corp"
    assert entities["ticket_ref"] == "#4821"

def test_extract_entities_unknown_company_no_ticket():
    entities = extract_entities("bob@unknownco.com", "hey", "no ticket here")
    assert entities["company"] == "unknownco.com"
    assert entities["ticket_ref"] is None