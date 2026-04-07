import json

def lambda_handler(event, context):

    print("Executor Input:", json.dumps(event))

    plans = event.get("plans", [])
    executions = []

    for p in plans:
        product_id = p["product_id"]
        warehouse = p["warehouse"]
        reorder_needed = p["reorder_needed"]

        if reorder_needed:
            order_qty = p["required_stock"] - p["current_stock"]

            execution = {
                "product_id": product_id,
                "warehouse": warehouse,
                "order_created": True,
                "order_quantity": order_qty,
                "supplier": "Supplier_A",
                "ai_reason": p.get("ai_reason", "")   # 🔥 PASS AI REASON
            }

        else:
            execution = {
                "product_id": product_id,
                "warehouse": warehouse,
                "order_created": False,
                "order_quantity": 0,
                "supplier": None,
                "ai_reason": p.get("ai_reason", "")   # 🔥 PASS AI REASON
            }

        executions.append(execution)

    return {
        "executions": executions
    }
