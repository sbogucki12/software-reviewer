# ai_review.py

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import time
import random

def scrape_vendor_documentation(vendor_url):
    """
    Enhanced scraper with targeted approach for finding additional document types.
    
    Args:
        vendor_url: Base URL for the vendor website
        
    Returns:
        Dictionary mapping document types to URLs
    """
    # Dictionary to store discovered URLs
    documentation_urls = {
        # Core legal documents
        "privacy_policy": None,
        "terms_of_service": None,
        "data_processing": None,
        
        # AI specific documents
        "ai_trust": None,
        "ai_ethics": None,
        "responsible_ai": None,
        
        # Data protection documents
        "data_security": None,
        "gdpr_compliance": None,
        "ccpa_compliance": None,
        
        # Service-specific documents
        "acceptable_use": None,
        "data_retention": None,
        "subprocessors": None,
        
        # Developer-focused documentation
        "api_terms": None,
        "developer_policy": None,
        
        # Enterprise information
        "admin_guide": None,
        "enterprise_controls": None
    }
    
    # Normalize the vendor URL
    if not vendor_url.startswith(('http://', 'https://')):
        vendor_url = 'https://' + vendor_url
    
    # Remove trailing slash if present
    vendor_url = vendor_url.rstrip('/')
    
    # Enhanced anti-bot detection headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Function to make requests with retry
    def make_request(url, method='get', max_retries=2):
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(0.3, 0.7))  # Small delay
                
                if method == 'head':
                    response = requests.head(url, headers=headers, timeout=10)
                else:
                    response = requests.get(url, headers=headers, timeout=10)
                
                return response
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
                time.sleep(random.uniform(1, 2))
        
        return None
    
    # Create a known patterns dictionary for major vendors
    # This directly maps vendor domains to known document URLs
    known_vendor_documents = {
        "microsoft.com": {
            "privacy_policy": "https://privacy.microsoft.com/en-us",
            "terms_of_service": "https://www.microsoft.com/licensing/terms/",
            "data_processing": "https://www.microsoft.com/licensing/terms/product/PrivacyandSecurityTerms",
            "ai_trust": "https://www.microsoft.com/ai/responsible-ai",
            "ai_ethics": "https://www.microsoft.com/ai/responsible-ai-resources",
            "responsible_ai": "https://www.microsoft.com/ai/responsible-ai",
            "data_security": "https://www.microsoft.com/security",
            "gdpr_compliance": "https://www.microsoft.com/en-us/trust-center/privacy/gdpr-overview",
            "ccpa_compliance": "https://www.microsoft.com/en-us/trust-center/privacy/ccpa",
            "acceptable_use": "https://www.microsoft.com/servicesagreement",
            "data_retention": "https://privacy.microsoft.com/en-us/data-retention",
            "subprocessors": "https://www.microsoft.com/licensing/terms/product/PrivacyandSecurityTerms/all",
            "api_terms": "https://www.microsoft.com/licensing/terms/product/APITerms",
            "developer_policy": "https://learn.microsoft.com/legal/developer-policies",
            "admin_guide": "https://learn.microsoft.com/microsoft-365/admin/admin-overview/admin-center-overview",
            "enterprise_controls": "https://learn.microsoft.com/microsoft-365/admin/add-users/about-admin-roles"
        },
        "google.com": {
            "privacy_policy": "https://policies.google.com/privacy",
            "terms_of_service": "https://policies.google.com/terms",
            "data_processing": "https://cloud.google.com/terms/data-processing-terms",
            "ai_trust": "https://ai.google/responsibility/",
            "ai_ethics": "https://ai.google/principles/",
            "responsible_ai": "https://ai.google/responsibility/",
            "data_security": "https://safety.google/security/",
            "gdpr_compliance": "https://cloud.google.com/privacy/gdpr",
            "ccpa_compliance": "https://privacy.google.com/businesses/compliance/",
            "acceptable_use": "https://cloud.google.com/terms/aup",
            "data_retention": "https://policies.google.com/technologies/retention",
            "subprocessors": "https://cloud.google.com/terms/subprocessors",
            "api_terms": "https://developers.google.com/terms",
            "developer_policy": "https://developers.google.com/terms/api-services-user-data-policy",
            "admin_guide": "https://support.google.com/a/answer/182076",
            "enterprise_controls": "https://support.google.com/a/answer/9050643"
        },
        "apple.com": {
            "privacy_policy": "https://www.apple.com/privacy/",
            "terms_of_service": "https://www.apple.com/legal/internet-services/terms/site.html",
            "data_processing": "https://www.apple.com/legal/enterprise/data-transfer-agreements/",
            "ai_trust": "https://www.apple.com/newsroom/2023/07/apples-new-ai-ethics-and-policy-team/",
            "ai_ethics": "https://www.apple.com/newsroom/2023/07/apples-new-ai-ethics-and-policy-team/",
            "data_security": "https://www.apple.com/privacy/features/",
            "gdpr_compliance": "https://www.apple.com/legal/privacy/en-ww/",
            "ccpa_compliance": "https://www.apple.com/legal/privacy/california/",
            "developer_policy": "https://developer.apple.com/app-store/review/guidelines/"
        },
        "amazon.com": {
            "privacy_policy": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ",
            "terms_of_service": "https://www.amazon.com/gp/help/customer/display.html?nodeId=508088",
            "acceptable_use": "https://aws.amazon.com/aup/",
            "data_security": "https://aws.amazon.com/security/",
            "subprocessors": "https://aws.amazon.com/compliance/sub-processors/",
            "developer_policy": "https://developer.amazon.com/support/legal/da"
        },
        "aws.amazon.com": {
            "privacy_policy": "https://aws.amazon.com/privacy/",
            "terms_of_service": "https://aws.amazon.com/service-terms/",
            "data_processing": "https://aws.amazon.com/service-terms/data-processing-addendum/",
            "ai_trust": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "ai_ethics": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "responsible_ai": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "data_security": "https://aws.amazon.com/security/",
            "gdpr_compliance": "https://aws.amazon.com/compliance/gdpr-center/",
            "ccpa_compliance": "https://aws.amazon.com/compliance/california-consumer-privacy-act/",
            "acceptable_use": "https://aws.amazon.com/aup/",
            "subprocessors": "https://aws.amazon.com/compliance/sub-processors/",
            "api_terms": "https://aws.amazon.com/service-terms/",
            "developer_policy": "https://aws.amazon.com/service-terms/",
            "admin_guide": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts.html",
            "enterprise_controls": "https://aws.amazon.com/organizations/"
        },
        "salesforce.com": {
            "privacy_policy": "https://www.salesforce.com/company/privacy/",
            "terms_of_service": "https://www.salesforce.com/company/legal/sfdc-website-terms-of-service/",
            "data_processing": "https://www.salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/data-processing-addendum.pdf",
            "ai_trust": "https://www.salesforce.com/company/ethics/ai/",
            "ai_ethics": "https://www.salesforce.com/company/ethics/ai/",
            "responsible_ai": "https://www.salesforce.com/company/ethics/ai/",
            "data_security": "https://www.salesforce.com/company/privacy/security/",
            "gdpr_compliance": "https://www.salesforce.com/gdpr/overview/",
            "acceptable_use": "https://www.salesforce.com/company/legal/acceptable-use-policy/",
            "subprocessors": "https://www.salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/data-processing-addendum.pdf"
        },
        "adobe.com": {
            "privacy_policy": "https://www.adobe.com/privacy/policy.html",
            "terms_of_service": "https://www.adobe.com/legal/terms.html",
            "data_processing": "https://www.adobe.com/privacy/data-processing-terms.html",
            "ai_trust": "https://www.adobe.com/sensei/ethics.html",
            "ai_ethics": "https://www.adobe.com/sensei/ethics.html",
            "responsible_ai": "https://www.adobe.com/sensei/ethics.html",
            "data_security": "https://www.adobe.com/security.html",
            "gdpr_compliance": "https://www.adobe.com/privacy/general-data-protection-regulation.html",
            "ccpa_compliance": "https://www.adobe.com/privacy/ccpa.html",
            "acceptable_use": "https://www.adobe.com/legal/terms.html",
            "subprocessors": "https://www.adobe.com/privacy/sub-processors.html",
            "developer_policy": "https://www.adobe.io/policies/developer-terms.html"
        },
        "slack.com": {
            "privacy_policy": "https://slack.com/trust/privacy/privacy-policy",
            "terms_of_service": "https://slack.com/terms-of-service",
            "data_processing": "https://slack.com/terms-of-service/data-processing",
            "data_security": "https://slack.com/trust/security",
            "gdpr_compliance": "https://slack.com/trust/compliance/gdpr",
            "acceptable_use": "https://slack.com/policy-enforcement/acceptable-use-policy",
            "subprocessors": "https://slack.com/trust/compliance/subprocessors",
            "api_terms": "https://api.slack.com/terms-of-service",
            "developer_policy": "https://api.slack.com/developer-policy",
            "admin_guide": "https://slack.com/help/articles/115004071768-What-is-Slack-Enterprise-Grid-"
        },
        "snowflake.com": {
            "privacy_policy": "https://www.snowflake.com/privacy-policy/",
            "terms_of_service": "https://www.snowflake.com/legal/terms-of-service/",
            "data_processing": "https://www.snowflake.com/legal/dpaa/",
            "data_security": "https://www.snowflake.com/security/",
            "gdpr_compliance": "https://www.snowflake.com/wp-content/uploads/2023/01/gdprwhitepaper-snowflakedpaa.pdf",
            "acceptable_use": "https://www.snowflake.com/legal/acceptable-use-policy/",
            "subprocessors": "https://www.snowflake.com/legal/subprocessors/"
        }
    }
    
    # Check if this is a known vendor - direct mapping approach
    for domain, docs in known_vendor_documents.items():
        if domain in vendor_url:
            logger.info(f"Found known vendor: {domain}")
            # Copy known URLs to our results
            for doc_type, doc_url in docs.items():
                documentation_urls[doc_type] = doc_url
                logger.info(f"Set {doc_type}: {doc_url}")
            
            # For known vendors, still continue with normal scraping to find any missing documents
            break
    
    # Dictionary of document patterns - used to identify document types from links
    document_patterns = {
        "privacy_policy": [
            'privacy', 'privacy policy', 'privacy statement', 'privacy notice'
        ],
        "terms_of_service": [
            'terms', 'tos', 'terms of service', 'terms of use', 'terms and conditions',
            'service agreement'
        ],
        "data_processing": [
            'data processing', 'data processing agreement', 'dpa', 'data processor',
            'data processing addendum', 'processing terms'
        ],
        "ai_trust": [
            'ai trust', 'ai principles', 'artificial intelligence trust', 'ai governance',
            'trustworthy ai', 'trusted ai'
        ],
        "ai_ethics": [
            'ai ethics', 'ethical ai', 'ai guidelines', 'ethics of ai',
            'ethical artificial intelligence', 'ethical guidelines'
        ],
        "responsible_ai": [
            'responsible ai', 'responsible artificial intelligence', 'ai responsibility',
            'responsible ml', 'responsible machine learning'
        ],
        "data_security": [
            'data security', 'security', 'information security', 'security policy',
            'security controls', 'secure data'
        ],
        "gdpr_compliance": [
            'gdpr', 'general data protection regulation', 'european privacy', 'eu compliance',
            'data protection regulation'
        ],
        "ccpa_compliance": [
            'ccpa', 'california consumer privacy', 'california privacy', 'california compliance',
            'consumer privacy act'
        ],
        "acceptable_use": [
            'acceptable use', 'aup', 'usage policy', 'use policy',
            'usage terms', 'appropriate use'
        ],
        "data_retention": [
            'data retention', 'retention policy', 'retention schedule', 'information retention',
            'retain data'
        ],
        "subprocessors": [
            'subprocessors', 'sub-processors', 'subcontractors', 'vendors', 'third parties',
            'third-party vendors', 'service providers'
        ],
        "api_terms": [
            'api terms', 'api policy', 'api usage', 'developer terms', 'api agreement',
            'api license'
        ],
        "developer_policy": [
            'developer policy', 'developer guidelines', 'developer agreement',
            'developer terms', 'app developer'
        ],
        "admin_guide": [
            'admin guide', 'administrator', 'admin portal', 'admin console', 'admin controls',
            'administration guide', 'administrator guide'
        ],
        "enterprise_controls": [
            'enterprise controls', 'enterprise settings', 'enterprise configuration',
            'organizational controls', 'organization settings', 'company settings'
        ]
    }
    
    # Function to check if URL matches a document type
    def get_doc_type(url, link_text):
        if not url:
            return None
        
        url_lower = url.lower()
        text_lower = link_text.lower() if link_text else ""
        
        for doc_type, patterns in document_patterns.items():
            # Skip if we already found this document type
            if documentation_urls[doc_type]:
                continue
                
            # Check URL path and link text
            for pattern in patterns:
                if pattern in url_lower or (text_lower and pattern in text_lower):
                    return doc_type
        
        return None
    
    # Function to normalize URLs
    def normalize_url(href, base_url):
        if not href:
            return None
        
        if href.startswith('http'):
            return href
        elif href.startswith('//'):
            return 'https:' + href
        elif href.startswith('/'):
            # Get domain
            domain_parts = base_url.split('/')[:3]
            domain = '/'.join(domain_parts)
            return domain + href
        else:
            base_parts = base_url.rstrip('/').split('/')
            if len(base_parts) > 3:  # If URL has path components
                base_path = '/'.join(base_parts[:-1])  # Remove last path component
                return f"{base_path}/{href}"
            else:
                return f"{base_url.rstrip('/')}/{href}"
    
    # Initial places to check
    pages_to_check = [vendor_url]
    
    # Add common starting points
    starting_points = [
        "/legal", "/about", "/privacy", "/security", "/trust",
        "/compliance", "/terms", "/policies", "/resources",
        "/developers", "/documentation", "/enterprise"
    ]
    
    for point in starting_points:
        pages_to_check.append(f"{vendor_url}{point}")
    
    # Special case for common subdomains
    vendor_domain = vendor_url.split('//')[1].split('/')[0]
    if vendor_domain.startswith('www.'):
        base_domain = vendor_domain[4:]
    else:
        base_domain = vendor_domain
    
    common_subdomains = [
        f"https://trust.{base_domain}",
        f"https://legal.{base_domain}",
        f"https://privacy.{base_domain}",
        f"https://developer.{base_domain}",
        f"https://developers.{base_domain}",
        f"https://security.{base_domain}",
        f"https://compliance.{base_domain}",
        f"https://docs.{base_domain}"
    ]
    
    pages_to_check.extend(common_subdomains)
    
    # Track visited pages
    visited_pages = set()
    important_links = []
    
    # Scrape pages to find document links
    for page_url in pages_to_check:
        if page_url in visited_pages:
            continue
            
        visited_pages.add(page_url)
        logger.info(f"Checking page: {page_url}")
        
        response = make_request(page_url)
        if not response or response.status_code != 200:
            logger.info(f"Skipping - status: {response.status_code if response else 'No response'}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for document links on this page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href or href.startswith(('javascript:', '#', 'mailto:')):
                continue
                
            link_text = link.get_text(strip=True)
            normalized_url = normalize_url(href, page_url)
            
            if not normalized_url:
                continue
                
            # Check if link is for a document type
            doc_type = get_doc_type(normalized_url, link_text)
            if doc_type and not documentation_urls[doc_type]:
                documentation_urls[doc_type] = normalized_url
                logger.info(f"Found {doc_type}: {normalized_url}")
            
            # Save potentially important links to check later
            lower_href = href.lower()
            lower_text = link_text.lower()
            
            if any(term in lower_href or term in lower_text for term in [
                'legal', 'policy', 'policies', 'terms', 'privacy', 'security',
                'data', 'compliance', 'gdpr', 'ccpa', 'ai', 'artificial intelligence',
                'ethics', 'responsible', 'developer', 'admin', 'enterprise', 'trust'
            ]):
                if normalized_url not in visited_pages and normalized_url not in important_links:
                    important_links.append(normalized_url)
    
    # Check the important links we found
    for link_url in important_links:
        if link_url in visited_pages:
            continue
            
        visited_pages.add(link_url)
        logger.info(f"Checking important link: {link_url}")
        
        response = make_request(link_url)
        if not response or response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for document links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href or href.startswith(('javascript:', '#', 'mailto:')):
                continue
                
            link_text = link.get_text(strip=True)
            normalized_url = normalize_url(href, link_url)
            
            if not normalized_url:
                continue
                
            # Check if link is for a document type
            doc_type = get_doc_type(normalized_url, link_text)
            if doc_type and not documentation_urls[doc_type]:
                documentation_urls[doc_type] = normalized_url
                logger.info(f"Found {doc_type}: {normalized_url}")
    
    # Try common paths for missing documents
    common_path_patterns = {
        "privacy_policy": [
            "/privacy", "/privacy-policy", "/legal/privacy", "/privacy-notice",
            "/legal/privacy-policy", "/about/privacy", "/data-privacy"
        ],
        "terms_of_service": [
            "/terms", "/tos", "/terms-of-service", "/legal/terms", "/terms-of-use",
            "/legal/terms-of-service", "/about/terms", "/legal-terms"  
        ],
        "data_processing": [
            "/data-processing", "/dpa", "/legal/data-processing", "/data-processing-agreement",
            "/legal/dpa", "/gdpr/data-processing"
        ],
        "ai_trust": [
            "/ai-trust", "/ai/trust", "/trust/ai", "/ai-principles", "/ai/principles",
            "/ai/governance", "/about/ai-principles"
        ],
        "ai_ethics": [
            "/ai-ethics", "/ai/ethics", "/ethics/ai", "/ai-guidelines",
            "/about/ai-ethics", "/responsible-ai/ethics"
        ],
        "responsible_ai": [
            "/responsible-ai", "/ai/responsibility", "/ai/responsible",
            "/about/responsible-ai", "/trust/responsible-ai"
        ],
        "data_security": [
            "/security", "/data-security", "/information-security", "/security-policy",
            "/legal/security", "/trust/security"
        ],
        "gdpr_compliance": [
            "/gdpr", "/legal/gdpr", "/privacy/gdpr", "/compliance/gdpr",
            "/data-protection", "/eu-privacy"
        ],
        "ccpa_compliance": [
            "/ccpa", "/legal/ccpa", "/privacy/ccpa", "/compliance/ccpa",
            "/california-privacy", "/us-privacy"
        ],
        "acceptable_use": [
            "/acceptable-use", "/aup", "/legal/acceptable-use", "/usage-policy",
            "/use-policy", "/legal/aup"
        ],
        "data_retention": [
            "/data-retention", "/retention-policy", "/legal/data-retention",
            "/privacy/retention", "/information-retention"
        ],
        "subprocessors": [
            "/subprocessors", "/sub-processors", "/legal/subprocessors",
            "/vendors", "/third-parties", "/suppliers"
        ],
        "api_terms": [
            "/api-terms", "/developers/terms", "/api/terms", "/api-policy",
            "/legal/api-terms", "/developer/api-terms"
        ],
        "developer_policy": [
            "/developer-policy", "/developers/policy", "/developer-guidelines",
            "/legal/developer", "/developer-agreement"
        ],
        "admin_guide": [
            "/admin-guide", "/administrator", "/admin", "/admin-portal",
            "/docs/admin", "/help/admin", "/enterprise/admin"
        ],
        "enterprise_controls": [
            "/enterprise", "/enterprise-controls", "/enterprise-settings",
            "/org-controls", "/organization-settings", "/business-controls"
        ]
    }
    
    # Try common paths for missing documents
    for doc_type, paths in common_path_patterns.items():
        if documentation_urls[doc_type]:
            continue  # Skip if already found
            
        for path in paths:
            if not path.startswith('/'):
                path = '/' + path
                
            test_url = vendor_url + path
            
            if test_url in visited_pages:
                continue
                
            visited_pages.add(test_url)
            logger.info(f"Trying common path for {doc_type}: {test_url}")
            
            response = make_request(test_url, method='head')
            if response and response.status_code < 400:
                documentation_urls[doc_type] = test_url
                logger.info(f"Found {doc_type} through common path: {test_url}")
                break
    
    # Get only the populated document URLs
    found_docs = {k: v for k, v in documentation_urls.items() if v}
    
    logger.info(f"\nFound {len(found_docs)} document URLs for {vendor_url}:")
    for doc_type, url in found_docs.items():
        logger.info(f"  {doc_type}: {url}")
    
    return documentation_urls


def extract_document_text(url):
    if not url:
        return ""
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator=' ')
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def analyze_ai_capabilities(texts):
    analysis = {
        "opt_out_available": False,
        "enterprise_opt_out": False,
        "native_ai": None,  # True/False/Unknown
        "third_party_providers": [],
        "data_retention": False,
        "model_training": False,
        "model_sharing": False,
        "contractual_protections": False,
        "concerns": []
    }
    
    # Keywords and patterns to look for
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
    
    # Analyze each document
    for doc_type, text in texts.items():
        if not text:
            continue
        
        # Check for opt-out options
        opt_out_matches = re.finditer(patterns["opt_out"], text, re.IGNORECASE)
        for match in opt_out_matches:
            analysis["opt_out_available"] = True
            # Check context around opt-out (100 chars before and after)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            if re.search(patterns["enterprise"], context, re.IGNORECASE):
                analysis["enterprise_opt_out"] = True
        
        # Check for AI implementation details
        if re.search(patterns["ai_native"], text, re.IGNORECASE):
            analysis["native_ai"] = True
            
        third_party_matches = re.finditer(patterns["third_party"], text, re.IGNORECASE)
        for match in third_party_matches:
            # Extract the third-party name from context
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            # Try to identify the specific third party
            for provider in ["OpenAI", "Azure", "Google", "AWS", "Amazon"]:
                if provider.lower() in context.lower() and provider not in analysis["third_party_providers"]:
                    analysis["third_party_providers"].append(provider)
        
        if analysis["third_party_providers"]:
            analysis["native_ai"] = False
        
        # Check data retention and model training
        if re.search(patterns["data_retention"], text, re.IGNORECASE):
            analysis["data_retention"] = True
            
        if re.search(patterns["model_training"], text, re.IGNORECASE):
            analysis["model_training"] = True
        
        # Check model sharing
        if re.search(patterns["model_sharing"], text, re.IGNORECASE):
            model_sharing_context = []
            for match in re.finditer(patterns["model_sharing"], text, re.IGNORECASE):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                model_sharing_context.append(text[start:end])
            
            # If we find model sharing context, analyze it
            if model_sharing_context:
                if any("not" in ctx.lower() for ctx in model_sharing_context):
                    analysis["model_sharing"] = False
                else:
                    analysis["model_sharing"] = True
        
        # Check contractual protections
        if analysis["third_party_providers"] and re.search(patterns["contractual"], text, re.IGNORECASE):
            for match in re.finditer(patterns["contractual"], text, re.IGNORECASE):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                if any(provider.lower() in context.lower() for provider in analysis["third_party_providers"]):
                    analysis["contractual_protections"] = True
        
        # Look for potential concerns
        concern_keywords = [
            "data breach", "privacy risk", "leakage", "unauthorized access",
            "sensitive data", "personal information", "compliance", "regulation"
        ]
        
        for keyword in concern_keywords:
            if keyword in text.lower():
                start_idx = text.lower().find(keyword)
                start = max(0, start_idx - 50)
                end = min(len(text), start_idx + len(keyword) + 50)
                concern_context = text[start:end]
                analysis["concerns"].append(f"Potential concern: {concern_context}")
    
    return analysis


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_review.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_review")

def get_vendor_documentation(vendor_url):
    """
    Get document URLs for a vendor, using known mappings for common vendors
    and falling back to web scraping for unknown vendors.
    
    Args:
        vendor_url: The vendor's URL
        
    Returns:
        Dictionary of document types mapped to their URLs
    """
    import re
    
    # Normalize the vendor URL
    if not vendor_url.startswith(('http://', 'https://')):
        vendor_url = 'https://' + vendor_url
    
    # Remove trailing slash if present
    vendor_url = vendor_url.rstrip('/')
    
    # Extract the domain from the URL
    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', vendor_url)
    if domain_match:
        domain = domain_match.group(1)
    else:
        domain = None
    
    # Pre-defined document URLs for common vendors
    known_vendors = {
        # Microsoft
        "microsoft.com": {
            "privacy_policy": "https://privacy.microsoft.com/en-us",
            "terms_of_service": "https://www.microsoft.com/licensing/terms/",
            "data_processing": "https://www.microsoft.com/licensing/terms/product/PrivacyandSecurityTerms",
            "ai_trust": "https://www.microsoft.com/ai/responsible-ai",
            "ai_ethics": "https://www.microsoft.com/ai/responsible-ai-resources",
            "responsible_ai": "https://www.microsoft.com/ai/responsible-ai",
            "data_security": "https://www.microsoft.com/security",
            "gdpr_compliance": "https://www.microsoft.com/en-us/trust-center/privacy/gdpr-overview",
            "ccpa_compliance": "https://www.microsoft.com/en-us/trust-center/privacy/ccpa",
            "acceptable_use": "https://www.microsoft.com/servicesagreement",
            "data_retention": "https://privacy.microsoft.com/en-us/data-retention",
            "subprocessors": "https://www.microsoft.com/licensing/terms/product/PrivacyandSecurityTerms/all",
            "api_terms": "https://www.microsoft.com/licensing/terms/product/APITerms",
            "developer_policy": "https://learn.microsoft.com/legal/developer-policies",
            "admin_guide": "https://learn.microsoft.com/microsoft-365/admin/admin-overview/admin-center-overview",
            "enterprise_controls": "https://learn.microsoft.com/microsoft-365/admin/add-users/about-admin-roles"
        },
        
        # Google
        "google.com": {
            "privacy_policy": "https://policies.google.com/privacy",
            "terms_of_service": "https://policies.google.com/terms",
            "data_processing": "https://cloud.google.com/terms/data-processing-terms",
            "ai_trust": "https://ai.google/responsibility/",
            "ai_ethics": "https://ai.google/principles/",
            "responsible_ai": "https://ai.google/responsibility/",
            "data_security": "https://safety.google/security/",
            "gdpr_compliance": "https://cloud.google.com/privacy/gdpr",
            "ccpa_compliance": "https://privacy.google.com/businesses/compliance/",
            "acceptable_use": "https://cloud.google.com/terms/aup",
            "data_retention": "https://policies.google.com/technologies/retention",
            "subprocessors": "https://cloud.google.com/terms/subprocessors",
            "api_terms": "https://developers.google.com/terms",
            "developer_policy": "https://developers.google.com/terms/api-services-user-data-policy",
            "admin_guide": "https://support.google.com/a/answer/182076",
            "enterprise_controls": "https://support.google.com/a/answer/9050643"
        },
        
        # Amazon AWS
        "aws.amazon.com": {
            "privacy_policy": "https://aws.amazon.com/privacy/",
            "terms_of_service": "https://aws.amazon.com/service-terms/",
            "data_processing": "https://aws.amazon.com/service-terms/data-processing-addendum/",
            "ai_trust": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "ai_ethics": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "responsible_ai": "https://aws.amazon.com/machine-learning/responsible-machine-learning/",
            "data_security": "https://aws.amazon.com/security/",
            "gdpr_compliance": "https://aws.amazon.com/compliance/gdpr-center/",
            "ccpa_compliance": "https://aws.amazon.com/compliance/california-consumer-privacy-act/",
            "acceptable_use": "https://aws.amazon.com/aup/",
            "subprocessors": "https://aws.amazon.com/compliance/sub-processors/",
            "api_terms": "https://aws.amazon.com/service-terms/",
            "developer_policy": "https://aws.amazon.com/service-terms/",
            "admin_guide": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts.html",
            "enterprise_controls": "https://aws.amazon.com/organizations/"
        },
        
        # Salesforce
        "salesforce.com": {
            "privacy_policy": "https://www.salesforce.com/company/privacy/",
            "terms_of_service": "https://www.salesforce.com/company/legal/sfdc-website-terms-of-service/",
            "data_processing": "https://www.salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/data-processing-addendum.pdf",
            "ai_trust": "https://www.salesforce.com/company/ethics/ai/",
            "ai_ethics": "https://www.salesforce.com/company/ethics/ai/",
            "responsible_ai": "https://www.salesforce.com/company/ethics/ai/",
            "data_security": "https://www.salesforce.com/company/privacy/security/",
            "gdpr_compliance": "https://www.salesforce.com/gdpr/overview/",
            "acceptable_use": "https://www.salesforce.com/company/legal/acceptable-use-policy/",
            "subprocessors": "https://www.salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/data-processing-addendum.pdf",
            "admin_guide": "https://help.salesforce.com/s/articleView?id=sf.admin_overview.htm",
            "enterprise_controls": "https://help.salesforce.com/s/articleView?id=sf.admin_adminroles.htm"
        },
        
        # Adobe
        "adobe.com": {
            "privacy_policy": "https://www.adobe.com/privacy/policy.html",
            "terms_of_service": "https://www.adobe.com/legal/terms.html",
            "data_processing": "https://www.adobe.com/privacy/data-processing-terms.html",
            "ai_trust": "https://www.adobe.com/sensei/ethics.html",
            "ai_ethics": "https://www.adobe.com/sensei/ethics.html",
            "responsible_ai": "https://www.adobe.com/sensei/ethics.html",
            "data_security": "https://www.adobe.com/security.html",
            "gdpr_compliance": "https://www.adobe.com/privacy/general-data-protection-regulation.html",
            "ccpa_compliance": "https://www.adobe.com/privacy/ccpa.html",
            "acceptable_use": "https://www.adobe.com/legal/terms.html",
            "subprocessors": "https://www.adobe.com/privacy/sub-processors.html",
            "developer_policy": "https://www.adobe.io/policies/developer-terms.html",
            "admin_guide": "https://helpx.adobe.com/enterprise/using/admin-console.html",
            "enterprise_controls": "https://helpx.adobe.com/enterprise/using/admin-console.html"
        },
        
        # Slack
        "slack.com": {
            "privacy_policy": "https://slack.com/trust/privacy/privacy-policy",
            "terms_of_service": "https://slack.com/terms-of-service",
            "data_processing": "https://slack.com/terms-of-service/data-processing",
            "data_security": "https://slack.com/trust/security",
            "gdpr_compliance": "https://slack.com/trust/compliance/gdpr",
            "acceptable_use": "https://slack.com/policy-enforcement/acceptable-use-policy",
            "subprocessors": "https://slack.com/trust/compliance/subprocessors",
            "api_terms": "https://api.slack.com/terms-of-service",
            "developer_policy": "https://api.slack.com/developer-policy",
            "admin_guide": "https://slack.com/help/articles/115004071768-What-is-Slack-Enterprise-Grid-",
            "enterprise_controls": "https://slack.com/help/articles/115004071768-What-is-Slack-Enterprise-Grid-"
        },
        
        # Snowflake
        "snowflake.com": {
            "privacy_policy": "https://www.snowflake.com/privacy-policy/",
            "terms_of_service": "https://www.snowflake.com/legal/terms-of-service/",
            "data_processing": "https://www.snowflake.com/legal/dpaa/",
            "ai_trust": "https://www.snowflake.com/blog/responsible-ai-framework/",
            "data_security": "https://www.snowflake.com/security/",
            "gdpr_compliance": "https://www.snowflake.com/wp-content/uploads/2023/01/gdprwhitepaper-snowflakedpaa.pdf",
            "acceptable_use": "https://www.snowflake.com/legal/acceptable-use-policy/",
            "subprocessors": "https://www.snowflake.com/legal/subprocessors/"
        },
        
        # Zoom
        "zoom.us": {
            "privacy_policy": "https://zoom.us/privacy",
            "terms_of_service": "https://zoom.us/terms",
            "data_processing": "https://zoom.us/data-processing",
            "ai_trust": "https://explore.zoom.us/docs/en-us/trust/ai-ethics.html",
            "data_security": "https://zoom.us/security",
            "gdpr_compliance": "https://zoom.us/gdpr",
            "subprocessors": "https://zoom.us/subprocessors",
            "developer_policy": "https://marketplace.zoom.us/docs/guides/guidelines/developer-policies",
            "admin_guide": "https://support.zoom.us/hc/en-us/categories/201146643",
            "enterprise_controls": "https://support.zoom.us/hc/en-us/articles/115005756143-Creating-changing-and-locking-account-settings"
        },
        
        # Add more vendors as needed
    }
    
    # Create the standard documentation_urls dictionary with all document types
    documentation_urls = {
        # Core legal documents
        "privacy_policy": None,
        "terms_of_service": None,
        "data_processing": None,
        
        # AI specific documents
        "ai_trust": None,
        "ai_ethics": None,
        "responsible_ai": None,
        
        # Data protection documents
        "data_security": None,
        "gdpr_compliance": None,
        "ccpa_compliance": None,
        
        # Service-specific documents
        "acceptable_use": None,
        "data_retention": None,
        "subprocessors": None,
        
        # Developer-focused documentation
        "api_terms": None,
        "developer_policy": None,
        
        # Enterprise information
        "admin_guide": None,
        "enterprise_controls": None
    }
    
    # If we found a domain and it's in our known vendors list,
    # use the pre-defined document URLs
    if domain:
        for known_domain, known_docs in known_vendors.items():
            if known_domain in domain:
                print(f"Using known document URLs for {domain}")
                
                # Copy the known document URLs to our results
                for doc_type, doc_url in known_docs.items():
                    documentation_urls[doc_type] = doc_url
                
                # We found a match, no need to continue checking
                break
    
    # If we don't have pre-defined URLs for this vendor,
    # fall back to the web scraping approach
    if not any(documentation_urls.values()):
        print(f"No pre-defined URLs for {domain}, using web scraping")
        documentation_urls = scrape_vendor_documentation(vendor_url)
    
    # Return the documentation URLs
    return documentation_urls

# Example usage:
def review_vendor(vendor_url):
    # Step 1: Get document URLs
    doc_urls = get_vendor_documentation(vendor_url)
    
    # Step 2: Debug document extraction
    debug_document_extraction(doc_urls)
    
    # Step 3: Extract text from each document
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                print(f"Extracting {doc_type}: {url}")
                doc_texts[doc_type] = extract_document_text(url)
                print(f"Extracted {len(doc_texts[doc_type])} characters from {doc_type}")
            except Exception as e:
                print(f"Error extracting {doc_type}: {str(e)}")
    
    # Step 4: Analyze AI capabilities with improved function
    analysis = fix_analyze_ai_capabilities(doc_texts)
    
    # Print confidence levels to verify they're not zero
    print("\nConfidence levels:")
    for key, value in analysis["confidence_levels"].items():
        print(f"  {key}: {value:.2f}")
    
    # Return results
    return {
        "vendor_url": vendor_url,
        "documentation_urls": doc_urls,
        "analysis": analysis
    }

def scrape_vendor_documentation(vendor_url: str) -> Dict[str, Optional[str]]:
    """
    Scrape a vendor's website to find URLs for relevant documentation.
    
    Args:
        vendor_url: The base URL for the vendor's website
        
    Returns:
        Dictionary mapping document types to URLs
    """
    logger.info(f"Scraping documentation from {vendor_url}")
    
    # Normalize the vendor URL
    if not vendor_url.startswith(('http://', 'https://')):
        vendor_url = 'https://' + vendor_url
    
    # Dictionary to store discovered URLs
    documentation_urls = {
        "privacy_policy": None,
        "ai_trust": None,
        "terms_of_service": None,
        "data_processing": None
    }
    
    # List of paths to check for common documentation locations
    common_paths = [
        "/privacy", "/privacy-policy", "/privacy-statement",
        "/terms", "/terms-of-service", "/terms-and-conditions",
        "/ai", "/ai-principles", "/ai-ethics", "/ai-trust",
        "/legal", "/data-processing", "/data-protection"
    ]
    
    # First try the main page
    try:
        response = requests.get(vendor_url, timeout=10)
        response.raise_for_status()
        
        # Check if we were redirected
        if response.url != vendor_url:
            logger.info(f"Redirected to {response.url}")
            vendor_url = response.url
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links to documentation in the main page
        found_urls = _extract_doc_links(soup, vendor_url)
        for doc_type, url in found_urls.items():
            if url:
                documentation_urls[doc_type] = url
        
        # Check common footer links
        footer_elements = soup.select("footer, .footer, #footer, [class*='footer']")
        for footer in footer_elements:
            footer_urls = _extract_doc_links(footer, vendor_url)
            for doc_type, url in footer_urls.items():
                if url and not documentation_urls[doc_type]:
                    documentation_urls[doc_type] = url
        
        # Check for a sitemap or legal page
        legal_links = _find_legal_or_sitemap_links(soup, vendor_url)
        
        # If we still miss some documents, try the common paths
        for doc_type, url in documentation_urls.items():
            if not url:
                # Try legal pages first
                for legal_url in legal_links:
                    try:
                        legal_response = requests.get(legal_url, timeout=10)
                        legal_soup = BeautifulSoup(legal_response.text, 'html.parser')
                        legal_urls = _extract_doc_links(legal_soup, vendor_url)
                        if legal_urls[doc_type]:
                            documentation_urls[doc_type] = legal_urls[doc_type]
                            break
                    except Exception as e:
                        logger.warning(f"Error checking legal page {legal_url}: {str(e)}")
                
                # If still not found, try common paths
                if not documentation_urls[doc_type]:
                    for path in common_paths:
                        if _is_relevant_path(path, doc_type):
                            try:
                                test_url = f"{vendor_url.rstrip('/')}{path}"
                                test_response = requests.get(test_url, timeout=5)
                                if test_response.status_code == 200:
                                    documentation_urls[doc_type] = test_url
                                    break
                            except Exception:
                                continue
    except Exception as e:
        logger.error(f"Error scraping {vendor_url}: {str(e)}")
    
    # Log the results
    found_docs = sum(1 for v in documentation_urls.values() if v)
    logger.info(f"Found {found_docs} documents for {vendor_url}")
    for doc_type, url in documentation_urls.items():
        if url:
            logger.info(f"  {doc_type}: {url}")
    
    return documentation_urls

def _extract_doc_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Optional[str]]:
    """Extract documentation links from a BeautifulSoup object"""
    doc_urls = {
        "privacy_policy": None,
        "ai_trust": None,
        "terms_of_service": None,
        "data_processing": None
    }
    
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        text = link.text.lower()
        
        # Skip empty or javascript links
        if not href or href.startswith(('javascript:', '#', 'mailto:')):
            continue
        
        # Normalize the URL
        url = href if href.startswith(('http://', 'https://')) else f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        
        # Find privacy policy
        if not doc_urls["privacy_policy"] and _is_privacy_policy_link(href, text):
            doc_urls["privacy_policy"] = url
        
        # Find AI trust/ethics center
        if not doc_urls["ai_trust"] and _is_ai_trust_link(href, text):
            doc_urls["ai_trust"] = url
        
        # Find terms of service
        if not doc_urls["terms_of_service"] and _is_terms_link(href, text):
            doc_urls["terms_of_service"] = url
        
        # Find data processing/protection
        if not doc_urls["data_processing"] and _is_data_processing_link(href, text):
            doc_urls["data_processing"] = url
    
    return doc_urls

def _find_legal_or_sitemap_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find links to legal or sitemap pages"""
    legal_links = []
    
    legal_patterns = [
        r'/legal', r'/about/legal', r'/site-map', r'/sitemap', 
        r'/footer', r'/about'
    ]
    
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        text = link.text.lower()
        
        # Skip empty or javascript links
        if not href or href.startswith(('javascript:', '#', 'mailto:')):
            continue
        
        # Check for legal or sitemap links
        if any(re.search(pattern, href) for pattern in legal_patterns) or \
           any(term in text for term in ['legal', 'sitemap', 'site map']):
            url = href if href.startswith(('http://', 'https://')) else f"{base_url.rstrip('/')}/{href.lstrip('/')}"
            legal_links.append(url)
    
    return legal_links

def _is_privacy_policy_link(href: str, text: str) -> bool:
    """Check if a link is likely a privacy policy"""
    return ('privacy' in href or 'privacy' in text) and not ('career' in href or 'job' in href)

def _is_ai_trust_link(href: str, text: str) -> bool:
    """Check if a link is likely an AI trust/ethics center"""
    return (('ai' in href or 'artificial intelligence' in text) and 
            ('trust' in href or 'ethics' in href or 'principles' in href or 
             'trust' in text or 'ethics' in text or 'principles' in text))

def _is_terms_link(href: str, text: str) -> bool:
    """Check if a link is likely terms of service"""
    return ('terms' in href or 'terms' in text or 'conditions' in href or 
            'conditions' in text or 'legal' in href or 'legal' in text)

def _is_data_processing_link(href: str, text: str) -> bool:
    """Check if a link is likely about data processing"""
    return (('data' in href and ('processing' in href or 'protection' in href)) or
            ('data' in text and ('processing' in text or 'protection' in text)) or
            'gdpr' in href or 'gdpr' in text or 'ccpa' in href or 'ccpa' in text)

def _is_relevant_path(path: str, doc_type: str) -> bool:
    """Check if a path is relevant for a document type"""
    if doc_type == "privacy_policy" and ("privacy" in path):
        return True
    elif doc_type == "ai_trust" and ("ai" in path):
        return True
    elif doc_type == "terms_of_service" and ("terms" in path or "tos" in path):
        return True
    elif doc_type == "data_processing" and ("data" in path):
        return True
    return False

def extract_document_text(url: str) -> str:
    """
    Extract and clean text content from a document URL.
    
    Args:
        url: URL of the document to extract text from
        
    Returns:
        Cleaned text content
    """
    logger.info(f"Extracting text from {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and hidden elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()
        
        # Remove elements with classes that suggest non-content areas
        for element in soup.select('[class*="banner"], [class*="cookie"], [class*="advertisement"], [class*="sidebar"], [class*="widget"]'):
            element.decompose()
        
        # Extract main content - first try to find a main content area
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '[role="main"]']:
            content_area = soup.select_one(selector)
            if content_area:
                main_content = content_area
                break
        
        # If no main content area found, use the entire body
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Get text
        text = main_content.get_text(separator=' ')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        logger.info(f"Extracted {len(text)} characters from {url}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return ""

def debug_document_extraction(doc_urls):
    """
    Helper function to debug document extraction issues
    """
    import requests
    from bs4 import BeautifulSoup
    
    print("\nDEBUG: Testing document extraction")
    for doc_type, url in doc_urls.items():
        if url:
            try:
                print(f"Testing extraction for {doc_type}: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=15)
                
                # Check if we got a valid response
                if response.status_code != 200:
                    print(f"  ERROR: Got status code {response.status_code}")
                    continue
                
                # Check content type
                content_type = response.headers.get('Content-Type', '')
                print(f"  Content type: {content_type}")
                
                # If it's PDF or other non-HTML content
                if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                    print(f"  WARNING: Non-HTML content type may affect extraction")
                
                # Try to parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get some stats about the content
                text_content = soup.get_text(separator=' ')
                print(f"  Extracted text length: {len(text_content)} characters")
                if len(text_content) < 100:
                    print(f"  WARNING: Very short text extracted. Content: {text_content[:100]}")
                else:
                    print(f"  Text sample: {text_content[:100]}...")
                    
                    # Check for AI-related terms
                    ai_terms = ['ai', 'artificial intelligence', 'machine learning', 'ml']
                    ai_mentions = [term for term in ai_terms if term in text_content.lower()]
                    print(f"  AI-related terms found: {ai_mentions}")
                
                # Check for JavaScript redirects or content
                js_redirects = soup.find_all('script', text=lambda t: t and ('location.href' in t or 'window.location' in t))
                if js_redirects:
                    print(f"  WARNING: Possible JavaScript redirect detected")
                    
            except Exception as e:
                print(f"  ERROR: {str(e)}")
    
    print("DEBUG: End of document extraction test\n")

    debug_document_extraction(doc_urls)

def fix_analyze_ai_capabilities(texts):
    """
    Fixed version of analyze_ai_capabilities function to correctly calculate confidence levels
    
    Args:
        texts: Dictionary mapping document types to their text content
        
    Returns:
        Dictionary containing comprehensive analysis results
    """
    import re
    import logging
    
    # Configure logging if not already configured
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    logger = logging.getLogger("ai_analysis")
    
    # Debug information about input
    doc_lengths = {doc_type: len(text) for doc_type, text in texts.items() if text}
    logger.info(f"Analyzing {len(doc_lengths)} non-empty documents: {doc_lengths}")
    
    # For tracking which documents provided which insights
    document_insights = {doc_type: [] for doc_type in texts.keys() if texts[doc_type]}
    
    # Create analysis structure with expanded fields
    analysis = {
        # Opt-out information
        "opt_out_available": False,
        "enterprise_opt_out": False,
        "opt_out_method": None,  # How to opt out (admin console, API, etc.)
        "opt_out_granularity": None,  # User-level, feature-level, etc.
        
        # AI implementation 
        "native_ai": None,  # True/False/None (unknown)
        "third_party_providers": [],
        "ai_features": [],  # List of AI features mentioned
        
        # Data usage
        "data_retention": False,
        "retention_period": None,  # Specific time period if mentioned
        "model_training": False,
        "model_sharing": False,
        "model_sharing_limitations": None,  # Any limitations on sharing
        
        # Contractual protections
        "contractual_protections": False,
        "contractual_details": None,  # Details of contractual protections
        
        # Compliance
        "gdpr_compliant": None,  # GDPR compliance status
        "ccpa_compliant": None,  # CCPA compliance status
        
        # Security
        "security_measures": [],  # Security measures for AI/data
        "security_certifications": [],  # Security certifications
        
        # Concerns and insights
        "concerns": [],
        "ethical_considerations": [],  # Ethical considerations mentioned
        
        # Additional metadata
        "document_coverage": {},  # Which documents were analyzed
        "confidence_levels": {},  # Confidence in each finding
        
        # Raw evidence for debugging/validation
        "_evidence": {}
    }
    
    # Track which documents were analyzed
    for doc_type in texts.keys():
        if texts[doc_type]:
            analysis["document_coverage"][doc_type] = True
            # Quick debug check for content
            first_100_chars = texts[doc_type][:100].replace('\n', ' ')
            logger.info(f"Document {doc_type} sample: {first_100_chars}...")
        else:
            analysis["document_coverage"][doc_type] = False
    
    # Helper function to get context around a match
    def get_context(text, match, chars_before=100, chars_after=100):
        start = max(0, match.start() - chars_before)
        end = min(len(text), match.end() + chars_after)
        return text[start:end]
    
    # Helper function to check if a context is AI-related
    def is_ai_related(context):
        ai_terms = [
            r'\bai\b', r'artificial intelligence', r'machine learning', r'ml\b', 
            r'generative', r'llm', r'large language model', r'neural network',
            r'intelligent assistant', r'smart feature', r'automated', r'algorithm',
            r'chat', r'copilot', r'insight', r'analytics', r'prediction'
        ]
        return any(re.search(term, context, re.IGNORECASE) for term in ai_terms)
    
    # Base patterns for different analyses
    patterns = {
        "opt_out": r'opt[-\s]?out|disable|turn off|deactivate|disable|toggle|switch off',
        "enterprise": r'enterprise|admin|administrator|organization|tenant|company-wide|organizational',
        "ai_native": r'built[-\s]?in|native|proprietary|our (own|model)|in-house|developed by us|internal',
        "third_party": r'third[-\s]?party|partner|OpenAI|Azure|Google|AWS|Amazon|Anthropic|Claude',
        "data_retention": r'retain|store|save|keep|preserve|hold|maintain',
        "model_training": r'train|learn|improve|enhance|develop|refine|optimize',
        "model_sharing": r'share|distribute|provide to|made available|transfer|transmit',
        "contractual": r'contract|agreement|prohibit|restrict|prevent|not (allowed|permitted)|obligate',
        "security": r'security|encrypt|protect|safeguard|secure|confidential',
        "ethical": r'ethical|fair|bias|transparent|explainable|interpretable|accountability',
        "admin_controls": r'admin (console|portal|dashboard|settings)|settings|configuration|preferences',
        "granularity": r'per[ -]?(user|feature|organization|tenant)|individual|specific',
        "compliance": r'comply|compliance|regulation|regulatory|requirement',
        "period": r'day|week|month|year|days|weeks|months|years|\d+[\s-]days|\d+[\s-]months'
    }
    
    # Initialize evidence containers for each pattern
    analysis["_evidence"] = {key: [] for key in patterns.keys()}
    
    # Document type priority for each analysis aspect
    priority_map = {
        "opt_out_available": ["admin_guide", "enterprise_controls", "terms_of_service", "privacy_policy"],
        "enterprise_opt_out": ["admin_guide", "enterprise_controls", "terms_of_service"],
        "native_ai": ["ai_trust", "ai_ethics", "responsible_ai", "privacy_policy"],
        "third_party_providers": ["subprocessors", "data_processing", "privacy_policy"],
        "data_retention": ["data_retention", "privacy_policy", "data_processing"],
        "model_training": ["ai_trust", "ai_ethics", "privacy_policy", "terms_of_service"],
        "model_sharing": ["terms_of_service", "privacy_policy", "data_processing"],
        "contractual_protections": ["data_processing", "terms_of_service", "api_terms"],
        "security_measures": ["data_security", "data_processing", "privacy_policy"]
    }
    
    # Note specific pattern locations to help debug
    pattern_locations = {}
    
    # Step 1: Analyze each document for each aspect
    for doc_type, text in texts.items():
        if not text:
            continue
        
        doc_prefix = f"[{doc_type}] "
        logger.info(f"Analyzing {doc_type} ({len(text)} chars)")
        
        # Debug: Check for AI-related terms in general
        ai_terms_found = []
        for term in ['ai', 'artificial intelligence', 'machine learning', 'model', 'algorithm']:
            if term in text.lower():
                ai_terms_found.append(term)
        
        if ai_terms_found:
            logger.info(f"AI terms found in {doc_type}: {ai_terms_found}")
        else:
            logger.info(f"No AI terms found in {doc_type}")
        
        # --- Opt-out Analysis ---
        if doc_type in ["admin_guide", "enterprise_controls", "privacy_policy", "terms_of_service", "acceptable_use"]:
            opt_out_matches = list(re.finditer(patterns["opt_out"], text, re.IGNORECASE))
            logger.info(f"Found {len(opt_out_matches)} opt_out pattern matches in {doc_type}")
            
            # Debug: Log the first few matches
            for i, match in enumerate(opt_out_matches[:3]):
                match_text = match.group(0)
                context = get_context(text, match, 50, 50)
                logger.info(f"Opt-out match {i+1} in {doc_type}: '{match_text}' - Context: '{context}'")
                
                # Store location for debugging
                if "opt_out" not in pattern_locations:
                    pattern_locations["opt_out"] = []
                pattern_locations["opt_out"].append((doc_type, match.start(), match_text))
            
            for match in opt_out_matches:
                context = get_context(text, match)
                
                # Debug: Check if context is AI-related
                is_ai = is_ai_related(context)
                if not is_ai:
                    logger.info(f"Skipping non-AI-related opt-out context in {doc_type}")
                    continue
                
                # Only consider if related to AI
                if is_ai:
                    analysis["_evidence"]["opt_out"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("opt_out_info")
                    
                    analysis["opt_out_available"] = True
                    
                    # Check for enterprise-level controls
                    if re.search(patterns["enterprise"], context, re.IGNORECASE):
                        analysis["_evidence"]["enterprise"].append(doc_prefix + context.strip())
                        analysis["enterprise_opt_out"] = True
                    
                    # Look for opt-out method
                    admin_console_match = re.search(patterns["admin_controls"], context, re.IGNORECASE)
                    if admin_console_match:
                        analysis["opt_out_method"] = "admin_console"
                    elif "api" in context.lower():
                        analysis["opt_out_method"] = "api"
                    elif "contact" in context.lower() or "request" in context.lower():
                        analysis["opt_out_method"] = "contact_vendor"
                    
                    # Check granularity
                    granularity_match = re.search(patterns["granularity"], context, re.IGNORECASE)
                    if granularity_match:
                        granularity_text = granularity_match.group(0).lower()
                        if "user" in granularity_text:
                            analysis["opt_out_granularity"] = "user_level"
                        elif "feature" in granularity_text:
                            analysis["opt_out_granularity"] = "feature_level"
                        elif "organization" in granularity_text or "tenant" in granularity_text:
                            analysis["opt_out_granularity"] = "organization_level"
        
        # --- AI Implementation Analysis ---
        if doc_type in ["ai_trust", "ai_ethics", "responsible_ai", "privacy_policy", "terms_of_service"]:
            # Look for native AI mentions
            ai_native_matches = list(re.finditer(patterns["ai_native"], text, re.IGNORECASE))
            logger.info(f"Found {len(ai_native_matches)} native AI pattern matches in {doc_type}")
            
            for match in ai_native_matches:
                context = get_context(text, match)
                
                if is_ai_related(context):
                    analysis["_evidence"]["ai_native"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("native_ai_info")
                    analysis["native_ai"] = True
            
            # Identify AI features
            ai_feature_pattern = r'(feature|capability|functionality|tool)s?\s+(?:includ(?:es?|ing)|such as|like)([^.]+)'
            ai_feature_matches = list(re.finditer(ai_feature_pattern, text, re.IGNORECASE))
            
            for match in ai_feature_matches:
                context = get_context(text, match, 50, 150)
                
                if is_ai_related(context):
                    features_text = match.group(2).strip()
                    features = [f.strip() for f in re.split(r',|\band\b', features_text)]
                    for feature in features:
                        if feature and feature not in analysis["ai_features"] and len(feature) > 3:
                            analysis["ai_features"].append(feature)
                            document_insights[doc_type].append("ai_features")
        
        # --- Third Party Provider Analysis ---
        if doc_type in ["subprocessors", "privacy_policy", "data_processing", "terms_of_service"]:
            # Look for third-party providers
            third_party_matches = list(re.finditer(patterns["third_party"], text, re.IGNORECASE))
            logger.info(f"Found {len(third_party_matches)} third-party pattern matches in {doc_type}")
            
            for match in third_party_matches:
                context = get_context(text, match)
                
                if is_ai_related(context):
                    analysis["_evidence"]["third_party"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("third_party_info")
                    
                    # Try to identify specific providers
                    provider_match = None
                    for provider in ["OpenAI", "Azure", "Google", "AWS", "Amazon", "Anthropic", "Claude", "HuggingFace", "Cohere"]:
                        if re.search(r'\b' + re.escape(provider) + r'\b', context, re.IGNORECASE):
                            provider_match = provider
                            if provider not in analysis["third_party_providers"]:
                                analysis["third_party_providers"].append(provider)
                    
                    if provider_match:
                        analysis["native_ai"] = False
        
        # --- Data Usage Analysis ---
        if doc_type in ["data_retention", "privacy_policy", "data_processing", "terms_of_service"]:
            # Check data retention
            data_retention_matches = list(re.finditer(patterns["data_retention"], text, re.IGNORECASE))
            logger.info(f"Found {len(data_retention_matches)} data retention pattern matches in {doc_type}")
            
            for match in data_retention_matches:
                context = get_context(text, match)
                
                if is_ai_related(context) and "data" in context.lower():
                    analysis["_evidence"]["data_retention"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("data_retention_info")
                    analysis["data_retention"] = True
                    
                    # Look for retention period
                    period_matches = list(re.finditer(patterns["period"], context, re.IGNORECASE))
                    if period_matches:
                        # Get 10 chars before and after the period mention
                        period_match = period_matches[0]
                        period_start = max(0, period_match.start() - 10)
                        period_end = min(len(context), period_match.end() + 10)
                        period_context = context[period_start:period_end]
                        analysis["retention_period"] = period_context.strip()
            
            # Check model training
            model_training_matches = list(re.finditer(patterns["model_training"], text, re.IGNORECASE))
            logger.info(f"Found {len(model_training_matches)} model training pattern matches in {doc_type}")
            
            for match in model_training_matches:
                context = get_context(text, match)
                
                if is_ai_related(context) and "data" in context.lower():
                    analysis["_evidence"]["model_training"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("model_training_info")
                    analysis["model_training"] = True
            
            # Check model sharing
            model_sharing_matches = list(re.finditer(patterns["model_sharing"], text, re.IGNORECASE))
            logger.info(f"Found {len(model_sharing_matches)} model sharing pattern matches in {doc_type}")
            
            for match in model_sharing_matches:
                context = get_context(text, match)
                
                if is_ai_related(context) and re.search(r'model|algorithm', context, re.IGNORECASE):
                    analysis["_evidence"]["model_sharing"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("model_sharing_info")
                    
                    # Look for negation near the sharing term
                    negations = re.search(r'not|never|isn\'t|doesn\'t|won\'t|wouldn\'t|prohibited|forbidden', context, re.IGNORECASE)
                    
                    if negations:
                        analysis["model_sharing"] = False
                        # Extract limitations on sharing
                        limit_start = max(0, negations.start() - 20)
                        limit_end = min(len(context), negations.end() + 50)
                        limit_text = context[limit_start:limit_end]
                        analysis["model_sharing_limitations"] = limit_text.strip()
                    else:
                        analysis["model_sharing"] = True
        
        # --- Contractual Protections Analysis ---
        if doc_type in ["data_processing", "terms_of_service", "privacy_policy", "api_terms"]:
            # Check for contractual protections
            contractual_matches = list(re.finditer(patterns["contractual"], text, re.IGNORECASE))
            logger.info(f"Found {len(contractual_matches)} contractual pattern matches in {doc_type}")
            
            for match in contractual_matches:
                context = get_context(text, match)
                
                if is_ai_related(context) and analysis["third_party_providers"]:
                    # Check if the context mentions any of the third-party providers
                    provider_mentioned = False
                    for provider in analysis["third_party_providers"]:
                        if re.search(r'\b' + re.escape(provider) + r'\b', context, re.IGNORECASE):
                            provider_mentioned = True
                            break
                    
                    # If no specific provider is mentioned, check for generic third-party terms
                    if not provider_mentioned:
                        provider_mentioned = re.search(r'third[\s-]party|partner|provider|vendor', context, re.IGNORECASE) is not None
                    
                    if provider_mentioned:
                        analysis["_evidence"]["contractual"].append(doc_prefix + context.strip())
                        document_insights[doc_type].append("contractual_protection_info")
                        analysis["contractual_protections"] = True
                        
                        # Extract details about the protections
                        if not analysis["contractual_details"]:
                            # Find a sentence containing the contractual term
                            sentences = re.split(r'(?<=[.!?])\s+', context)
                            for sentence in sentences:
                                if re.search(patterns["contractual"], sentence, re.IGNORECASE):
                                    analysis["contractual_details"] = sentence.strip()
                                    break
        
        # --- Compliance Analysis ---
        if doc_type in ["gdpr_compliance", "ccpa_compliance", "privacy_policy", "data_processing"]:
            # Check GDPR compliance
            if re.search(r'\bgdpr\b|general data protection regulation', text, re.IGNORECASE):
                document_insights[doc_type].append("gdpr_info")
                if re.search(r'comply|compliant|compliance|adhere', text, re.IGNORECASE):
                    analysis["gdpr_compliant"] = True
            
            # Check CCPA compliance
            if re.search(r'\bccpa\b|california consumer privacy', text, re.IGNORECASE):
                document_insights[doc_type].append("ccpa_info")
                if re.search(r'comply|compliant|compliance|adhere', text, re.IGNORECASE):
                    analysis["ccpa_compliant"] = True
        
        # --- Security Analysis ---
        if doc_type in ["data_security", "privacy_policy", "data_processing"]:
            # Look for security measures
            security_matches = list(re.finditer(patterns["security"], text, re.IGNORECASE))
            logger.info(f"Found {len(security_matches)} security pattern matches in {doc_type}")
            
            for match in security_matches:
                context = get_context(text, match)
                
                if is_ai_related(context) or "data" in context.lower():
                    analysis["_evidence"]["security"].append(doc_prefix + context.strip())
                    document_insights[doc_type].append("security_info")
                    
                    # Extract security measures
                    security_measures = [
                        "encryption", "access controls", "authentication", "monitoring",
                        "auditing", "data minimization", "anonymization", "pseudonymization"
                    ]
                    
                    for measure in security_measures:
                        if measure in context.lower() and measure not in analysis["security_measures"]:
                            analysis["security_measures"].append(measure)
            
            # Look for security certifications
            cert_pattern = r'\b(ISO|SOC|HITRUST|FedRAMP|PCI DSS)[- ]\d+\b|\b(ISO|SOC|HITRUST|FedRAMP|PCI DSS)\b'
            cert_matches = list(re.finditer(cert_pattern, text, re.IGNORECASE))
            
            for match in cert_matches:
                cert = match.group(0)
                if cert not in analysis["security_certifications"]:
                    analysis["security_certifications"].append(cert)
                    document_insights[doc_type].append("security_certification_info")
        
        # --- Ethical Considerations Analysis ---
        if doc_type in ["ai_ethics", "responsible_ai", "ai_trust"]:
            # Look for ethical considerations
            ethical_matches = list(re.finditer(patterns["ethical"], text, re.IGNORECASE))
            logger.info(f"Found {len(ethical_matches)} ethical pattern matches in {doc_type}")
            
            for match in ethical_matches:
                context = get_context(text, match)
                
                analysis["_evidence"]["ethical"].append(doc_prefix + context.strip())
                document_insights[doc_type].append("ethical_consideration_info")
                
                # Extract the sentence containing the ethical consideration
                sentences = re.split(r'(?<=[.!?])\s+', context)
                for sentence in sentences:
                    if re.search(patterns["ethical"], sentence, re.IGNORECASE):
                        if sentence.strip() not in analysis["ethical_considerations"]:
                            analysis["ethical_considerations"].append(sentence.strip())
    
    # Step 2: Resolve conflicting information based on document priority
    for key, doc_priorities in priority_map.items():
        if key in analysis and analysis[key] is not None:
            # Check if we have conflicting evidence
            evidence_key = key.split("_")[0] if "_" in key else key
            if evidence_key in analysis["_evidence"] and len(analysis["_evidence"][evidence_key]) > 1:
                # Get the document type with the highest priority that has evidence
                for doc_type in doc_priorities:
                    if doc_type in document_insights and any(evidence_key in insight for insight in document_insights[doc_type]):
                        # Use this document's evidence as the most authoritative
                        logger.info(f"Using {doc_type} as authoritative source for {key}")
                        break
    
    # Step 3: Look for contradictions or uncertainties
    concerns = []
    
    if analysis["opt_out_available"] and not analysis["opt_out_method"]:
        concerns.append("Opt-out is mentioned but the method is not clearly specified")
    
    if analysis["third_party_providers"] and not analysis["contractual_protections"]:
        concerns.append("Third-party AI providers are used without explicit contractual protections mentioned")
    
    if analysis["model_training"] and not analysis["data_retention"]:
        concerns.append("Model training is mentioned without clear data retention policy")
    
    if analysis["data_retention"] and not analysis["retention_period"]:
        concerns.append("Data retention is mentioned without specifying the retention period")
    
    if analysis["model_sharing"] and not analysis["model_sharing_limitations"]:
        concerns.append("Models may be shared without clear limitations")
    
    # Add discovered concerns
    for concern in concerns:
        if concern not in analysis["concerns"]:
            analysis["concerns"].append(concern)
    
    # Step 4: Calculate confidence levels
    confidence_map = {
        "opt_out_available": 0.0,
        "enterprise_opt_out": 0.0,
        "native_ai": 0.0,
        "third_party_providers": 0.0,
        "data_retention": 0.0,
        "model_training": 0.0,
        "model_sharing": 0.0,
        "contractual_protections": 0.0
    }
    
    # Base confidence on number of pieces of evidence and document types
    for key in confidence_map.keys():
        evidence_key = key.split("_")[0] if "_" in key else key
        if evidence_key in analysis["_evidence"]:
            evidence_count = len(analysis["_evidence"][evidence_key])
            doc_types = set()
            for evidence in analysis["_evidence"][evidence_key]:
                if evidence.startswith('[') and ']' in evidence:
                    doc_type = evidence[1:evidence.find(']')]
                    doc_types.add(doc_type)
            
            doc_count = len(doc_types)
            
            # More evidence and more document types = higher confidence
            if evidence_count > 0:
                confidence_map[key] = min(1.0, (0.3 * evidence_count + 0.7 * doc_count) / 3)
                logger.info(f"Confidence for {key}: {confidence_map[key]:.2f} (based on {evidence_count} evidence items from {doc_count} document types)")
    
    analysis["confidence_levels"] = confidence_map
    
    # Debugging information
    logger.info(f"Evidence collected: {sum(len(v) for v in analysis['_evidence'].values())} items")
    for key, evidence_list in analysis["_evidence"].items():
        if evidence_list:
            logger.info(f"  {key}: {len(evidence_list)} items")
    
    # If we found no evidence at all, there might be an extraction problem
    if not any(analysis["_evidence"].values()):
        logger.warning("No evidence found in any document! This suggests an extraction or pattern matching problem.")
        analysis["concerns"].append("Analysis could not find relevant information in the provided documents.")
    
    # Log pattern locations for debugging
    if pattern_locations:
        logger.info("Pattern locations for debugging:")
        for pattern, locations in pattern_locations.items():
            logger.info(f"  {pattern}: {locations[:5]}")
    
    # Add document insights summary to output
    analysis["_document_insights"] = document_insights
    
    return analysis
def is_context_ai_related(context, default_to_true=False):
    """
    Improved function to determine if a context is AI-related, with an option
    to default to true for certain document types.
    
    Args:
        context: The text context to check
        default_to_true: Whether to default to True for ambiguous contexts
        
    Returns:
        bool: Whether the context is AI-related
    """
    # Broad list of AI-related terms
    ai_terms = [
        r'\bai\b', r'artificial intelligence', r'machine learning', r'ml\b', 
        r'model', r'algorithm', r'neural', r'predict', r'classify',
        r'generative', r'llm', r'large language model',
        r'intelligent', r'automated', r'assistant',
        r'chat', r'copilot', r'insight', r'analytics',
        r'cognitive', r'smart', r'automate'
    ]
    
    # Check if any AI term is present
    context_lower = context.lower()
    for term in ai_terms:
        if re.search(term, context_lower, re.IGNORECASE):
            return True
    
    # If we're defaulting to true for ambiguous cases and this is a privacy or data context
    if default_to_true and any(term in context_lower for term in [
        'data', 'privacy', 'information', 'user', 'personal', 'service'
    ]):
        return True
    
    return False

def direct_confidence_fix(analysis):
    """
    Direct fix for confidence levels when they're all zero despite evidence being collected.
    This function can be called after your regular analysis is complete.
    
    Args:
        analysis: The analysis results dictionary
        
    Returns:
        The updated analysis with corrected confidence levels
    """
    # Check if we have evidence but zero confidence
    has_evidence = any(len(items) > 0 for key, items in analysis.get("_evidence", {}).items())
    all_zero_confidence = all(value == 0.0 for value in analysis.get("confidence_levels", {}).values())
    
    if has_evidence and all_zero_confidence:
        print("Fixing zero confidence levels with direct fix...")
        
        # Dictionary to map evidence keys to confidence keys
        confidence_map = {
            "opt_out": "opt_out_available",
            "enterprise": "enterprise_opt_out", 
            "ai_native": "native_ai",
            "third_party": "third_party_providers",
            "data_retention": "data_retention",
            "model_training": "model_training",
            "model_sharing": "model_sharing",
            "contractual": "contractual_protections"
        }
        
        # Calculate confidence levels directly from evidence
        for evidence_key, confidence_key in confidence_map.items():
            if evidence_key in analysis["_evidence"]:
                evidence_list = analysis["_evidence"][evidence_key]
                evidence_count = len(evidence_list)
                
                # Get unique document types
                doc_types = set()
                for evidence in evidence_list:
                    if evidence.startswith('[') and ']' in evidence:
                        doc_type = evidence[1:evidence.find(']')]
                        doc_types.add(doc_type)
                
                doc_count = len(doc_types)
                
                # Calculate confidence based on evidence and document counts
                if evidence_count > 0:
                    # More evidence and document types = higher confidence
                    confidence = min(1.0, (0.3 * evidence_count + 0.7 * doc_count) / 3)
                    analysis["confidence_levels"][confidence_key] = confidence
                    print(f"  {confidence_key}: {confidence:.2f} (based on {evidence_count} items from {doc_count} docs)")
    
    # Special case for "native_ai" inference from third-party providers
    if analysis.get("third_party_providers") and analysis["confidence_levels"].get("third_party_providers", 0) > 0:
        # If we found third-party providers, we can be reasonably confident it's not native AI
        if analysis.get("native_ai") is False:
            analysis["confidence_levels"]["native_ai"] = min(1.0, analysis["confidence_levels"]["third_party_providers"] * 0.8)
            print(f"  Inferring native_ai confidence from third_party_providers: {analysis['confidence_levels']['native_ai']:.2f}")
    
    return analysis

def review_vendor(vendor_url):
    # Get document URLs
    doc_urls = get_vendor_documentation(vendor_url)
    
    # Extract text
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                doc_texts[doc_type] = extract_document_text(url)
            except Exception as e:
                print(f"Error extracting {doc_type}: {str(e)}")
    
    # Run the analysis
    analysis = fix_analyze_ai_capabilities(doc_texts)
    
    # Apply the direct confidence fix
    analysis = direct_confidence_fix(analysis)
    
    return analysis






        