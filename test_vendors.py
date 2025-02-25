# test_vendors.py

TEST_VENDORS = [
    {
        "name": "Microsoft",
        "url": "https://www.microsoft.com",
        "expected_docs": ["privacy_policy", "terms_of_service"],
        "validation_keywords": {
            "privacy_policy": ["AI", "machine learning", "data"],
            "terms_of_service": ["license", "agreement"]
        }
    },
    {
        "name": "Adobe",
        "url": "https://www.adobe.com",
        "expected_docs": ["privacy_policy", "terms_of_service"],
        "validation_keywords": {
            "privacy_policy": ["personal information", "collect"],
            "terms_of_service": ["license", "subscription"]
        }
    },
    {
        "name": "Salesforce",
        "url": "https://www.salesforce.com",
        "expected_docs": ["privacy_policy", "terms_of_service"],
        "validation_keywords": {
            "privacy_policy": ["data", "information", "collect"],
            "terms_of_service": ["service", "agreement"]
        }
    },
    {
        "name": "Zoom",
        "url": "https://www.zoom.us",
        "expected_docs": ["privacy_policy", "terms_of_service"],
        "validation_keywords": {
            "privacy_policy": ["data", "information", "collect"],
            "terms_of_service": ["service", "agreement"]
        }
    },
    {
        "name": "Slack",
        "url": "https://slack.com",
        "expected_docs": ["privacy_policy", "terms_of_service"],
        "validation_keywords": {
            "privacy_policy": ["data", "information", "collect"],
            "terms_of_service": ["service", "agreement"]
        }
    }
]

# Synthetic text samples for testing specific patterns
SYNTHETIC_SAMPLES = {
    "opt_out_enterprise": """
    Our AI features can be disabled at the enterprise level. Administrators can access the Admin 
    Console to turn off AI capabilities across their organization. Individual users cannot opt out.
    """,
    
    "opt_out_individual": """
    Users can disable AI features in their account settings. Go to Settings > Privacy > 
    AI Features and toggle the switch to off. This will deactivate all AI-powered features.
    """,
    
    "native_ai": """
    We use our proprietary machine learning models developed in-house by our data science team.
    Our native AI algorithms are trained and optimized for our specific use cases.
    """,
    
    "third_party_ai": """
    Our product integrates with OpenAI's GPT models to provide AI capabilities. Some features
    may also utilize Google's machine learning APIs for specific functionalities.
    """,
    
    "data_retention": """
    We retain user data for a period of 30 days to improve our services and train our models.
    After this period, the data is anonymized but may be kept for analytical purposes.
    """,
    
    "model_sharing_yes": """
    Our AI models are trained on aggregated user data and are shared across our customer base
    to provide improved recommendations and features for all users of our platform.
    """,
    
    "model_sharing_no": """
    While we train models on customer data, these models are specific to each customer's tenant
    and are never shared with other customers or organizations.
    """,
    
    "contractual_protection": """
    Our contracts with third-party AI providers explicitly prohibit them from using your data
    to train their general models or share any insights derived from your data with others.
    """
}

def get_test_vendor_by_name(name):
    """Get a specific test vendor by name"""
    for vendor in TEST_VENDORS:
        if vendor["name"].lower() == name.lower():
            return vendor
    return None

def get_synthetic_sample(key):
    """Get a synthetic text sample by key"""
    return SYNTHETIC_SAMPLES.get(key, "")

def get_combined_synthetic_test(scenario):
    """Combine multiple synthetic samples for a specific test scenario"""
    if scenario == "enterprise_opt_out_native":
        return SYNTHETIC_SAMPLES["opt_out_enterprise"] + "\n\n" + \
               SYNTHETIC_SAMPLES["native_ai"] + "\n\n" + \
               SYNTHETIC_SAMPLES["model_sharing_no"]
    
    elif scenario == "third_party_with_protection":
        return SYNTHETIC_SAMPLES["opt_out_individual"] + "\n\n" + \
               SYNTHETIC_SAMPLES["third_party_ai"] + "\n\n" + \
               SYNTHETIC_SAMPLES["contractual_protection"]
    
    elif scenario == "high_risk_scenario":
        return SYNTHETIC_SAMPLES["third_party_ai"] + "\n\n" + \
               SYNTHETIC_SAMPLES["data_retention"] + "\n\n" + \
               SYNTHETIC_SAMPLES["model_sharing_yes"]
    
    return ""