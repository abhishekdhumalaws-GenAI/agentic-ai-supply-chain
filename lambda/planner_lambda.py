import json
import boto3
from boto3.dynamodb.conditions import Key
from model_service import invoke_model

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

memory_table = dynamodb.Table('agent-memory')


# --- Existing functions ---
def check_inventory(product_id):
    inventory_db = {
        "p1": 20,
        "p2": 150,
        "p3": 5
    }
    return {"product_id": product_id, "stock": inventory_db.get(product_id, 0)}


def estimate_demand(product_id):
    demand_map = {
        "p1": 5,
        "p2": 3,
        "p3": 2
    }
    return {"product_id": product_id, "predicted_daily_demand": demand_map.get(product_id, 1)}


# --- 🔥 AI BUFFER FUNCTION ---
def get_buffer_from_ai(product_id, demand, lead_time, past_records):

    history = "\n".join([
        f"- stockout: {r.get('stockout_risk')}, delay: {r.get('delay_risk')}"
        for r in past_records[-5:]
    ]) if past_records else "No past issues"

    prompt = f"""
    You are a supply chain expert.

    Product: {product_id}
    Daily demand: {demand}
    Lead time: {lead_time}

    Past history:
    {history}

    Task:
    Return JSON ONLY in this format:
    {{
      "buffer": <integer>,
      "reason": "<short explanation>"
    }}

    Do not return anything else.
    """

    response = invoke_model("nova", prompt)

    print("AI Raw Response:", response)

    # 🔥 Parse AI JSON safely
    try:
        import re

        json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
        ai_output = json.loads(json_str)

        buffer = int(ai_output.get("buffer", 0))
        reason = ai_output.get("reason", "No reason provided")

    except Exception as e:
        print("AI Parsing Error:", str(e))
        buffer = 0
        reason = "Fallback: Unable to parse AI response"

    return buffer, reason


# --- MAIN HANDLER ---
def lambda_handler(event, context):
    print("Planner Input:", json.dumps(event))

    bucket = event['bucket']
    key = event['key']

    # Read orders from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    orders = json.loads(response['Body'].read().decode('utf-8'))

    plans = []

    for order in orders:
        product_id = order['product_id']
        warehouse = order['warehouse']
        lead_time = order['lead_time_days']

        inventory = check_inventory(product_id)
        demand = estimate_demand(product_id)

        # 🔥 READ MEMORY
        try:
            response = memory_table.query(
                KeyConditionExpression=Key('product_id').eq(product_id)
            )
            past_records = response.get("Items", [])
        except Exception as e:
            print("Memory read error:", str(e))
            past_records = []

        # 🔥 AI decides buffer
        # 🔥 AI-based buffer + reason
        buffer, ai_reason = get_buffer_from_ai(
            product_id,
            demand['predicted_daily_demand'],
            lead_time,
            past_records
        )

        # Final calculation
        required_stock = (demand['predicted_daily_demand'] * lead_time) + buffer

        plan = {
            "product_id": product_id,
            "warehouse": warehouse,
            "current_stock": inventory['stock'],
            "required_stock": required_stock,
            "buffer_added": buffer,
            "ai_reason": ai_reason,   # 🔥 NEW FIELD
            "reorder_needed": inventory['stock'] <= required_stock
        }

        plans.append(plan)

    return {
        "plans": plans
    }
