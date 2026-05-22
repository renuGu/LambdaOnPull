import boto3
import json
import logging
import re
#import jsonschema
#print(jsonschema.__version__)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_json(text: str) -> str:
    idx = text.find("{")
    if idx == -1:
        raise ValueError("No JSON object found in model output")
    return text[idx:].strip()
    # stripe function used to remove unwanted leading and trailing characters from a string. 

def lambda_handler(event, context):
    # TODO implement
    from botocore.exceptions import ClientError
    #from jsonschema import validate, ValidationError

    
    FILE_RESULT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": [
        "filename",
        "software_code_quality",
        "software_code_security",
        "software_code_uptime",
        "software_code_performance",
        "software_code_cost"
    ],
    "properties": {
        "filename": {
            "type": "string"
        },
        "software_code_quality": {"$ref": "#/definitions/category"},
        "software_code_security": {"$ref": "#/definitions/category"},
        "software_code_uptime": {"$ref": "#/definitions/category"},
        "software_code_performance": {"$ref": "#/definitions/category"},
        "software_code_cost": {"$ref": "#/definitions/category"}
    },
    "definitions": {
        "category": {
            "type": "object",
            "required": ["issues", "score", "score_explanation"],
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/issue"}
                },
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100
                },
                "score_explanation": {
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "issue": {
            "type": "object",
            "required": [
                "description",
                "severity",
                "line",
                "remedy",
                "Recommendation"
            ],
            "properties": {
                "description": {"type": "string"},
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"]
                },
                "line": {"type": "number", "minimum": 0},
                "remedy": {"type": "string"},
                "Recommendation": {"type": "string"}
            },
            "additionalProperties": False
        }
    },
    "additionalProperties": False
    }

    ROOT_SCHEMA = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["results"],
            "properties": {
                "results": {
                    "type": "array",
                    "items": FILE_RESULT_SCHEMA,
                    "minItems": 1
                }
            },
            "additionalProperties": False
    }


    schema_text = json.dumps(ROOT_SCHEMA, indent=2)

    # get PR diff
    diff = event.get("diff", "")

    print('Received diff length:', len(diff))
    print('First 500 chars:')
    print(diff[:500])

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-2")

    # Set the model ID, e.g., Titan Text Premier.
    model_id = "openai.gpt-oss-120b-1:0"

    # Define the prompt for the model.
    #prompt = "can help me to detect software code quality, software code security, software code uptime issues, software code performance issues, software code cost issues related to software and infrastructure code changes and also provided the remedies for this code in java package sample; import java.util.*; public class SecurityAndPerformance { // SQL Injection example public String insecureSql(String user){ return "SELECT * FROM users WHERE name='" + user + "'"; } public String secureSql(String user){ return "SELECT * FROM users WHERE name=?"; } // Command injection example public void insecureCommand(String ip) throws Exception { Runtime.getRuntime().exec("ping " + ip); } public void secureCommand(String ip) throws Exception { new ProcessBuilder("ping", ip).start(); } // Performance issue public void slowLoop(int[] arr){ for(int a: arr){ for(int b: arr){ if(a==b){} } } } public void fastLoop(int[] arr){ HashSet<Integer> set=new HashSet<>(); for(int i: arr) set.add(i); for(int i: arr){ if(set.contains(i)){} } } }"
    
    wrapped_diff = f"""  You are a static code analysis engine used in an automated CI/CD pipeline.

    Task:
    Analyze the provided Pull Request diff 
    Generate output for each file or diff independently and detect: 
    - software code quality issues
    - software code security issues
    - software code uptime issues
    - software code performance issues
    - software error handling issues
    - software cost issues related to software and infrastructure changes

    Input:
    The Pull Request diff is provided below.
    Each file or diff section is separated by the keyword "diff git".

    Output requirements (STRICT):
    - Return ONLY valid JSON
    - Do NOT include reasoning, analysis, or explanations
    - Do NOT include <reasoning> tags
    - Do NOT include markdown
    - Do NOT include any text outside JSON
    - JSON must be strictly valid and machine-readable
    - Generate output for each file or diff independently
    - If no issues exist for a category, return an empty issues array
    - Scores must be numbers between 0 and 100
    - Do not output text before or after JSON.

    Scoring:
    Generate a score (0–100) for each category based solely on the detected issues.

    Output format:
    - The response MUST conform exactly to the provided JSON schema {schema_text} 
    - do not include </think> tag
    - do not include .y tag
    - do not include .f tag
    - do not include N! tag

    - Each element in "results" MUST match the schema.

    Pull Request diff: {diff} """

    # Format the request payload using the model's native structure.
    native_request = {

        
        "messages": [
            { "role": "user", "content": wrapped_diff }
        ],
        "temperature": 0.25,
        "max_tokens": 4000,
        "top_p": 1,
        "stop": ["<reasoning>", "</reasoning>", "```"]
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)
    
    #add while 
    idxy = -1
    while idxy == -1:
    
        try:
            # Invoke the model with the request.
            response = client.invoke_model(modelId=model_id, body=request)

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)


        # Decode the response body.
        #response_content = json.loads(response["body"].read())
        #print ('response after invoking lambda',response ) response is a strream
        response_content = response['body'].read().decode('utf-8') # Reads everything

        print('response in raw string',response_content ) 
        # reasoning can have "results" 


        # re.DOTALL (re.S) flag ensures that '.' matches newline characters if the text spans multiple lines
        cleaned_data = re.sub(r'<reasoning>.*?</reasoning>', '', response_content, flags=re.DOTALL)

        cleaned_data = re.sub(r'</think>', '', cleaned_data, flags=re.IGNORECASE)


        print('cleaned_data is: ',cleaned_data)
        model_response = json.loads(cleaned_data)
        
        # Extract and print the response text.
        print('response is: ',model_response)
        content = model_response["choices"][0]["message"]["content"]
        print('main content is :', content)

        #check if content has a results or not if not invoke model again.
        idxy = content.find("results")

        # go back to the top to invoke again
        
        # we are doing to delete the content till we find { from 'content': 'N.\n\n\n{\n  "results":
        content  = extract_json(content)
        
        try:
            content = json.loads(content) # for this content should be in json to load properly other wise will fail.
        except json.JSONDecodeError as e:
            idxy = -1
    # end of while.
    
    #try:
    #    validate(instance=parsed_content, schema=ROOT_SCHEMA)
    #except ValidationError as e:
    #  raise ValueError(f"Schema validation failed: {e.message}")

    # Step 1: Decode the escaped string into a regular JSON string
    #clean_json_str = json.loads(f'"{content}"') 

    # Step 2: Parse that string into a Python dictionary
    #data = json.loads(clean_json_str)

    # Step 3: Print it formatted (Pretty-print)
    #print(json.dumps(data, indent=2))

    return {
        'statusCode': 200,
        'body': json.dumps(content )
    }
