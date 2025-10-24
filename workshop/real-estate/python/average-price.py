import requests
import json
import os

json_url = 'https://raw.githubusercontent.com/bogdanfazakas/datasets/refs/heads/main/data.json'
output_folder = '/data/outputs'
output_file = os.path.join(output_folder, 'results.json')

def compute_avg_price_by_rooms(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        properties = response.json()

        if not isinstance(properties, list):
            raise ValueError("Expected JSON to be a list")

        avg_prices_by_rooms = {}

        for prop in properties:
            info = prop.get("info", {})
            price = info.get("price")
            rooms_no = info.get("roomsNo")

            if price is None or rooms_no is None:
                continue

            if rooms_no not in avg_prices_by_rooms:
                avg_prices_by_rooms[rooms_no] = {
                    "totalPrice": 0,
                    "count": 0
                }

            avg_prices_by_rooms[rooms_no]["totalPrice"] += price
            avg_prices_by_rooms[rooms_no]["count"] += 1

        # Finalize average calculation
        for rooms_no, stats in avg_prices_by_rooms.items():
            avg = stats["totalPrice"] / stats["count"]
            avg_prices_by_rooms[rooms_no]["averagePrice"] = round(avg, 2)

        # Write to output file
        os.makedirs(output_folder, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(avg_prices_by_rooms, f, indent=2)

        print("✅ Results written to:", output_file)
        print("📊 Avg Prices by Rooms:", avg_prices_by_rooms)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Run it
compute_avg_price_by_rooms(json_url)