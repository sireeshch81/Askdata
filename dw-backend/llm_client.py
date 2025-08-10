import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found!")
    exit(1)

# Initialize the LLM client
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=api_key
)

def load_recommendation_prompt():
    """Load the recommendation letter prompt from file."""
    try:
        with open("api-backend/prompts/recommendation-letter-prompt.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Error: recommendation-letter-prompt.txt not found!")
        return None

def generate_recommendation_letter(customer_data,offer_id):
    """
    Generate a recommendation letter using the prompt and customer data.
    
    Args:
        customer_data (dict): Customer profile and recommendations data
    
    Returns:
        str: Generated recommendation letter
    """
    # Load the prompt template
    prompt_template = load_recommendation_prompt()
    if not prompt_template:
        return "Error: Could not load prompt template"
    
    # Convert customer data to JSON string for the prompt
    customer_data_json = json.dumps(customer_data, indent=2)
    
    # Create the full prompt with customer data
    full_prompt = f"""
{prompt_template}

Offer ID:
{offer_id}

Customer Data (JSON):
{customer_data_json}

Please generate the recommendation letter based on the above instructions and customer data.
"""
    
    try:
        # Generate the recommendation letter
        response = llm.invoke(full_prompt)
        return response.content
    except Exception as e:
        return f"Error generating recommendation letter: {e}"

# def test_recommendation_letter():
#     """Test the recommendation letter generation with sample data."""
#     # Sample customer data (you can replace this with real data)
# # Generate offer ID (simple implementation)
#     import uuid
#     offer_id = str(uuid.uuid4())[:8].upper()

#     sample_customer_data = {
#         "customer_profile": {
#             "name": "John Smith",
#             "customer_id": "12345"
#         },
#         "recommendations": [
#             {
#                 "rank": 1,
#                 "product_name": "Premium Credit Card",
#                 "reason": "Excellent credit score and payment history"
#             },
#             {
#                 "rank": 2,
#                 "product_name": "Personal Loan",
#                 "reason": "Strong financial standing and low debt utilization"
#             },
#             {
#                 "rank": 3,
#                 "product_name": "Home Equity Line of Credit",
#                 "reason": "Good equity position and stable income"
#             }
#         ]
#     }
    
#     print("📝 Generating recommendation letter...")
#     letter = generate_recommendation_letter(sample_customer_data,offer_id)
#     print("\n" + "="*50)
#     print("GENERATED RECOMMENDATION LETTER")
#     print("="*50)
#     print(letter)
#     print("="*50)

# Test the connection
# try:
    # response = llm.invoke("What is the capital of France?")
    # print(f"\n🤖 Basic test response: {response.content}")
    
    # Test recommendation letter generation
#     test_recommendation_letter()
    
# except Exception as e:
#     print(f"❌ Error calling OpenAI API: {e}")
#     print("Please check your API key and internet connection.")
