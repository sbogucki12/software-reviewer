from ai_review import get_vendor_documentation, extract_document_text, fix_analyze_ai_capabilities

def test_vendor(vendor_url):
    # Get documents
    doc_urls = get_vendor_documentation(vendor_url)
    
    # Extract text
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                print(f"Extracting {doc_type}")
                doc_texts[doc_type] = extract_document_text(url)
            except Exception as e:
                print(f"Error: {e}")
    
    # Use the fixed analysis function
    analysis = fix_analyze_ai_capabilities(doc_texts)
    
    # Print confidence scores
    print("\nConfidence Scores:")
    for key, value in analysis["confidence_levels"].items():
        print(f"  {key}: {value}")
    
    return analysis

if __name__ == "__main__":
    test_vendor("https://www.microsoft.com")