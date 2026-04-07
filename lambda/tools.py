def check_inventory(product_id):

    inventory_db = {
        "p1": 20,
        "p2": 150,
        "p3": 5
    }

    return {
        "product_id": product_id,
        "stock": inventory_db.get(product_id, 0)
    }

def estimate_demand(product_id):
    """
    Mock demand prediction function.
    Later you can replace this with ML model / SageMaker endpoint.
    """

    # Simple mock logic (you can improve later)
    demand_map = {
        "p1": 5,
        "p2": 3,
        "p3": 2
    }

    return {
        "product_id": product_id,
        "predicted_daily_demand": demand_map.get(product_id, 1)
    }
