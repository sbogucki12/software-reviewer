# debug_evidence.py
from ai_review import get_vendor_documentation, extract_document_text, fix_analyze_ai_capabilities

def debug_evidence_collection(vendor_url):
    print(f"Debugging evidence collection for {vendor_url}")
    
    # Get documents
    doc_urls = get_vendor_documentation(vendor_url)
    
    # Extract text
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                doc_texts[doc_type] = extract_document_text(url)
                print(f"Extracted {len(doc_texts[doc_type])} chars from {doc_type}")
                
                # Check for AI-related terms directly
                text = doc_texts[doc_type].lower()
                ai_terms = ['ai', 'artificial intelligence', 'machine learning', 
                           'model', 'algorithm', 'neural', 'chat', 'copilot']
                
                found_terms = [term for term in ai_terms if term in text]
                print(f"  AI terms in {doc_type}: {found_terms if found_terms else 'NONE FOUND'}")
                
                # Sample the text for review
                print(f"  First 200 chars: {text[:200].replace(chr(10), ' ')}")
                
            except Exception as e:
                print(f"Error extracting {doc_type}: {e}")
    
    # Analyze with specific debugging
    print("\nRunning analysis with explicit pattern matching debug...")
    
    # Define common patterns from the analysis function
    patterns = {
        "opt_out": r'opt[-\s]?out|disable|turn off|deactivate',
        "enterprise": r'enterprise|admin|administrator|organization|tenant',
        "ai_native": r'built[-\s]?in|native|proprietary|our (own|model)',
        "third_party": r'third[-\s]?party|partner|OpenAI|Azure|Google|AWS',
        "data_retention": r'retain|store|save|keep|preserve',
        "model_training": r'train|learn|improve|enhance',
        "model_sharing": r'share|distribute|provide to|made available',
        "contractual": r'contract|agreement|prohibit|restrict|prevent'
    }
    
    # Check direct pattern matches in documents
    import re
    for doc_type, text in doc_texts.items():
        if not text:
            continue
            
        print(f"\nChecking pattern matches in {doc_type}:")
        for pattern_name, pattern in patterns.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            print(f"  {pattern_name}: {len(matches)} matches")
            
            # Show first match context if found
            if matches:
                match = matches[0]
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')
                print(f"    First match context: \"{context}\"")
    
    # Now run the full analysis
    analysis = fix_analyze_ai_capabilities(doc_texts)
    
    # Check evidence collection
    print("\nEvidence collected:")
    for key, evidence_list in analysis["_evidence"].items():
        print(f"  {key}: {len(evidence_list)} items")
        # Show first item if any
        if evidence_list:
            first_item = evidence_list[0][:100] + "..." if len(evidence_list[0]) > 100 else evidence_list[0]
            print(f"    First item: {first_item}")
    
    # Print confidence scores
    print("\nConfidence scores:")
    for key, value in analysis["confidence_levels"].items():
        print(f"  {key}: {value}")
    
    return analysis

if __name__ == "__main__":
    debug_evidence_collection("https://www.microsoft.com")