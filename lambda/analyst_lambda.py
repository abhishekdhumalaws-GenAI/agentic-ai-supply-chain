import json
import boto3
from datetime import datetime

sns = boto3.client('sns')
TOPIC_ARN = "arn:aws:sns:us-east-1:623593083974:supply-chain-alerts"

dynamodb = boto3.resource('dynamodb')

memory_table = dynamodb.Table('agent-memory')
results_table = dynamodb.Table('supply_chain_results')


def lambda_handler(event, context):

    print("Analyst Input:", json.dumps(event))

    executions = event.get("executions", [])
    analysis = []

    for e in executions:

        product_id = e["product_id"]
        warehouse = e["warehouse"]
        ai_reason = e.get("ai_reason", "No AI reasoning")

        if e.get("order_created"):
            stockout_risk = True
            delay_risk = True
            recommendation = "Expedite shipment or increase safety stock"
        else:
            stockout_risk = False
            delay_risk = False
            recommendation = "Stock is sufficient"

        timestamp = datetime.utcnow().isoformat()

        item = {
            "product_id": product_id,
            "timestamp": timestamp,
            "warehouse": warehouse,
            "stockout_risk": stockout_risk,
            "delay_risk": delay_risk,
            "recommendation": recommendation,
            "ai_reason": ai_reason   # 🔥 STORED HERE
        }
        
        if stockout_risk:
            message = f"""
            🚨 Supply Chain Alert

            Product: {product_id}
            Warehouse: {warehouse}

            AI Reason:
            {ai_reason}

            Recommendation:
            {recommendation}
            """

            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="Stockout Alert",
                Message=message
            )

        # 🔥 STORE IN BOTH TABLES
        memory_table.put_item(Item=item)
        results_table.put_item(Item=item)

        analysis.append(item)

    return {
        "analysis": analysis,
        "feedback_required": any(a["stockout_risk"] for a in analysis)
    }
