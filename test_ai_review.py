# test_ai_review.py

import argparse
import json
import re
import time
import sys
from datetime import datetime
from pathlib import Path

# Import primary functions (assuming they're in ai_review.py)
from ai_review import (
    scrape_vendor_documentation,
    extract_document_text,
    analyze_ai_capabilities
)

# Import test data
from test_vendors import (
    TEST_VENDORS,
    SYNTHETIC_SAMPLES,
    get_test_vendor_by_name,
    get_synthetic_sample,
    get_combined_synthetic_test
)

def create_test_directory():
    """Create a directory for test outputs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = Path(f"test_results_{timestamp}")
    test_dir.mkdir(exist_ok=True)
    return test_dir

def test_synthetic_samples():
    """Test the analysis algorithm with synthetic text samples"""
    print("\n==== Testing Analysis with Synthetic Samples ====")
    test_dir = create_test_directory()
    
    results = {}
    
    # Test individual synthetic samples
    for key, sample in SYNTHETIC_SAMPLES.items():
        print(f"\nTesting sample: {key}")
        doc_texts = {"synthetic": sample}
        analysis = analyze_ai_capabilities(doc_texts)
        
        results[key] = {
            "sample": sample[:100] + "..." if len(sample) > 100 else sample,
            "analysis": analysis
        }
        
        # Print key results based on the sample type
        if "opt_out" in key:
            print(f"Opt-out available: {analysis['opt_out_available']}")
            print(f"Enterprise opt-out: {analysis['enterprise_opt_out']}")
        elif "native" in key:
            print(f"Native AI: {analysis['native_ai']}")
        elif "third_party" in key:
            print(f"Third-party providers: {analysis['third_party_providers']}")
            print(f"Native AI: {analysis['native_ai']}")
        elif "data_retention" in key:
            print(f"Data retention: {analysis['data_retention']}")
            print(f"Model training: {analysis['model_training']}")
        elif "model_sharing" in key:
            print(f"Model sharing: {analysis['model_sharing']}")
        elif "contractual" in key:
            print(f"Contractual protections: {analysis['contractual_protections']}")
    
    # Test combined scenarios
    scenarios = ["enterprise_opt_out_native", "third_party_with_protection", "high_risk_scenario"]
    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario}")
        sample = get_combined_synthetic_test(scenario)
        doc_texts = {"scenario": sample}
        analysis = analyze_ai_capabilities(doc_texts)
        
        results[f"scenario_{scenario}"] = {
            "sample": sample[:100] + "..." if len(sample) > 100 else sample,
            "analysis": analysis
        }
        
        print(f"Opt-out available: {analysis['opt_out_available']}")
        print(f"Enterprise opt-out: {analysis['enterprise_opt_out']}")
        print(f"Native AI: {analysis['native_ai']}")
        print(f"Third-party providers: {analysis['third_party_providers']}")
        print(f"Model sharing: {analysis['model_sharing']}")
        print(f"Contractual protections: {analysis['contractual_protections']}")
    
    # Save results
    with open(test_dir / "synthetic_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSynthetic test results saved to {test_dir / 'synthetic_test_results.json'}")
    return results

def test_live_vendors(vendors=None, max_vendors=3):
    """Test with live vendor websites"""
    print("\n==== Testing with Live Vendor Websites ====")
    test_dir = create_test_directory()
    
    if not vendors:
        vendors = TEST_VENDORS[:max_vendors]  # Limit to avoid long test times
    
    results = {}
    
    for vendor in vendors:
        vendor_name = vendor["name"]
        vendor_url = vendor["url"]
        print(f"\nTesting vendor: {vendor_name} ({vendor_url})")
        
        # Step 1: Scrape documentation
        print("  Scraping documentation...")
        try:
            doc_urls = scrape_vendor_documentation(vendor_url)
            print(f"  Found {sum(1 for v in doc_urls.values() if v)} document links")
            
            # Validate expected documents
            expected_docs = vendor.get("expected_docs", [])
            found_expected = sum(1 for doc in expected_docs if doc in doc_urls and doc_urls[doc])
            print(f"  Found {found_expected}/{len(expected_docs)} expected documents")
            
            # Step 2: Extract content
            print("  Extracting content...")
            doc_texts = {}
            for doc_type, url in doc_urls.items():
                if url:
                    try:
                        print(f"    Extracting {doc_type}...")
                        text = extract_document_text(url)
                        doc_texts[doc_type] = text
                        print(f"    Extracted {len(text)} characters")
                        
                        # Validate content with keywords
                        validation_keywords = vendor.get("validation_keywords", {}).get(doc_type, [])
                        if validation_keywords:
                            matches = sum(1 for kw in validation_keywords if kw.lower() in text.lower())
                            print(f"    Found {matches}/{len(validation_keywords)} validation keywords")
                    except Exception as e:
                        print(f"    Error extracting {doc_type}: {str(e)}")
            
            # Step 3: Analyze capabilities
            if doc_texts:
                print("  Analyzing AI capabilities...")
                analysis = analyze_ai_capabilities(doc_texts)
                
                print("  Analysis results:")
                print(f"    Opt-out available: {analysis['opt_out_available']}")
                print(f"    Enterprise opt-out: {analysis['enterprise_opt_out']}")
                print(f"    Native AI: {analysis['native_ai']}")
                print(f"    Third-party providers: {analysis['third_party_providers']}")
                print(f"    Data retention: {analysis['data_retention']}")
                print(f"    Model training: {analysis['model_training']}")
                print(f"    Model sharing: {analysis['model_sharing']}")
                print(f"    Contractual protections: {analysis['contractual_protections']}")
                print(f"    Concerns found: {len(analysis['concerns'])}")
                
                results[vendor_name] = {
                    "url": vendor_url,
                    "doc_urls": doc_urls,
                    "analysis": analysis
                }
            else:
                print("  No document content to analyze")
                results[vendor_name] = {
                    "url": vendor_url,
                    "doc_urls": doc_urls,
                    "error": "No document content extracted"
                }
        except Exception as e:
            print(f"  Error processing {vendor_name}: {str(e)}")
            results[vendor_name] = {
                "url": vendor_url,
                "error": str(e)
            }
        
        # Add a delay between vendor tests to avoid rate limiting
        if vendor != vendors[-1]:
            time.sleep(2)
    
    # Save results
    with open(test_dir / "vendor_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nVendor test results saved to {test_dir / 'vendor_test_results.json'}")
    return results

def test_keyword_extraction(vendor_name=None, doc_type=None, keyword_type=None):
    """Test and debug keyword extraction from vendor documentation"""
    print("\n==== Testing Keyword Extraction ====")
    
    if not vendor_name:
        # Use the first vendor as default
        vendor = TEST_VENDORS[0]
        vendor_name = vendor["name"]
        vendor_url = vendor["url"]
    else:
        vendor = get_test_vendor_by_name(vendor_name)
        if not vendor:
            print(f"Vendor '{vendor_name}' not found in test data")
            return
        vendor_url = vendor["url"]
    
    print(f"Testing keyword extraction for {vendor_name} ({vendor_url})")
    
    # Scrape documentation
    try:
        doc_urls = scrape_vendor_documentation(vendor_url)
        
        if doc_type and doc_type not in doc_urls:
            print(f"Document type '{doc_type}' not found for vendor {vendor_name}")
            return
        
        # If doc_type is specified, only extract that document
        urls_to_extract = {doc_type: doc_urls[doc_type]} if doc_type else doc_urls
        
        doc_texts = {}
        for dtype, url in urls_to_extract.items():
            if url:
                try:
                    print(f"Extracting {dtype}...")
                    text = extract_document_text(url)
                    doc_texts[dtype] = text
                    print(f"Extracted {len(text)} characters")
                except Exception as e:
                    print(f"Error extracting {dtype}: {str(e)}")
        
        if not doc_texts:
            print("No document content extracted")
            return
        
        # Define patterns used in analyze_ai_capabilities
        patterns = {
            "opt_out": r'opt[-\s]?out|disable|turn off|deactivate',
            "enterprise": r'enterprise|admin|administrator|organization|tenant',
            "ai_native": r'built[-\s]?in|native|proprietary|our (own|model)',
            "third_party": r'third[-\s]?party|partner|OpenAI|Azure|Google|AWS|Amazon',
            "data_retention": r'retain|store|save|keep|preserve',
            "model_training": r'train|learn|improve|enhance',
            "model_sharing": r'share|distribute|provide to|made available',
            "contractual": r'contract|agreement|prohibit|restrict|prevent|not (allowed|permitted)',
        }
        
        # If keyword_type is specified, only check that pattern
        patterns_to_check = {keyword_type: patterns[keyword_type]} if keyword_type else patterns
        
        # Check each document for the specified patterns
        for dtype, text in doc_texts.items():
            print(f"\nAnalyzing {dtype}:")
            
            for pattern_name, pattern in patterns_to_check.items():
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                print(f"\n  Pattern '{pattern_name}' ({pattern}):")
                print(f"  Found {len(matches)} matches")
                
                # Show context for up to 5 matches
                for i, match in enumerate(matches[:5], 1):
                    matched_text = match.group(0)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    context = context.replace(matched_text, f"**{matched_text}**")
                    print(f"\n  Match {i}: '{matched_text}'")
                    print(f"  Context: \"...{context}...\"")
                
                if len(matches) > 5:
                    print(f"\n  ... and {len(matches) - 5} more matches")
    
    except Exception as e:
        print(f"Error: {str(e)}")

def test_execution_time():
    """Test execution time for each component"""
    print("\n==== Testing Execution Time ====")
    
    # Use first vendor for testing
    vendor = TEST_VENDORS[0]
    vendor_name = vendor["name"]
    vendor_url = vendor["url"]
    
    print(f"Testing performance with {vendor_name} ({vendor_url})")
    
    # Test scraping
    print("\nTesting scrape_vendor_documentation:")
    start_time = time.time()
    doc_urls = scrape_vendor_documentation(vendor_url)
    scrape_time = time.time() - start_time
    print(f"  Time: {scrape_time:.2f} seconds")
    print(f"  Found {sum(1 for v in doc_urls.values() if v)} document links")
    
    # Test extraction (one document)
    doc_to_test = next((url for doc, url in doc_urls.items() if url), None)
    if doc_to_test:
        print("\nTesting extract_document_text (one document):")
        start_time = time.time()
        text = extract_document_text(doc_to_test)
        extract_time = time.time() - start_time
        print(f"  Time: {extract_time:.2f} seconds")
        print(f"  Extracted {len(text)} characters")
    
    # Test extraction (all documents)
    print("\nTesting extract_document_text (all documents):")
    start_time = time.time()
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                doc_texts[doc_type] = extract_document_text(url)
            except Exception:
                pass
    all_extract_time = time.time() - start_time
    print(f"  Time: {all_extract_time:.2f} seconds")
    print(f"  Extracted {len(doc_texts)} documents")
    
    # Test analysis
    if doc_texts:
        print("\nTesting analyze_ai_capabilities:")
        start_time = time.time()
        analysis = analyze_ai_capabilities(doc_texts)
        analysis_time = time.time() - start_time
        print(f"  Time: {analysis_time:.2f} seconds")
    
    # Test end-to-end
    print("\nTesting end-to-end process:")
    start_time = time.time()
    doc_urls = scrape_vendor_documentation(vendor_url)
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                doc_texts[doc_type] = extract_document_text(url)
            except Exception:
                pass
    if doc_texts:
        analysis = analyze_ai_capabilities(doc_texts)
    end_to_end_time = time.time() - start_time
    print(f"  Time: {end_to_end_time:.2f} seconds")
    
    print("\nPerformance Summary:")
    print(f"  Scraping: {scrape_time:.2f}s")
    print(f"  Single document extraction: {extract_time:.2f}s")
    print(f"  All documents extraction: {all_extract_time:.2f}s")
    print(f"  Analysis: {analysis_time:.2f}s")
    print(f"  End-to-end: {end_to_end_time:.2f}s")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test AI capability review tool")
    parser.add_argument("--test", choices=["synthetic", "vendors", "keyword", "time", "all"], 
                       default="all", help="Test type to run")
    parser.add_argument("--vendor", help="Specific vendor to test")
    parser.add_argument("--doc-type", help="Specific document type to test")
    parser.add_argument("--keyword", help="Specific keyword pattern to test")
    parser.add_argument("--max-vendors", type=int, default=3, 
                       help="Maximum number of vendors to test")
    return parser.parse_args()

def main():
    """Main entry point for testing"""
    args = parse_args()
    
    print("==== AI Capability Review Tool Testing ====")
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.test == "synthetic" or args.test == "all":
        test_synthetic_samples()
    
    if args.test == "vendors" or args.test == "all":
        if args.vendor:
            vendor = get_test_vendor_by_name(args.vendor)
            if vendor:
                test_live_vendors([vendor])
            else:
                print(f"Vendor '{args.vendor}' not found in test data")
        else:
            test_live_vendors(max_vendors=args.max_vendors)
    
    if args.test == "keyword" or args.test == "all":
        test_keyword_extraction(args.vendor, args.doc_type, args.keyword)
    
    if args.test == "time" or args.test == "all":
        test_execution_time()
    
    print("\n==== Testing Complete ====")

if __name__ == "__main__":
    main()