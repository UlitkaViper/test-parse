from enum import Enum
import csv
import requests
import json


URL = "https://api.metro-cc.ru/products-api/graph"
AMOUNT = 100

class Location(Enum):
    MOSCOW = 10
    SPB = 15


def get_row(item: dict) -> list:
    try:
        id_ = item.get("id")
        name = item.get("name")
        link = f"https://online.metro-cc.ru{item.get('url')}" 
        brand = item.get("manufacturer").get("name")
        cur_price = item.get("stocks")[0].get("prices").get("price")
        old_price = item.get("stocks")[0].get("prices").get("old_price")
        if not old_price:
            old_price = cur_price
    except Exception:
        return None
    
    return [id_, name, old_price, cur_price, brand, link]


def get_data(location: Location) -> dict:
    headers = {
    "Accept": "*/*",
    "Content-Type": "application/json" 
    }

    payload = json.dumps({
    "query": "\n  query Query($storeId: Int!, $slug: String!, $attributes:[AttributeFilter], $filters: [FieldFilter], $from: Int!, $size: Int!, $sort: InCategorySort, $in_stock: Boolean, $eshop_order: Boolean, $is_action: Boolean, $price_levels: Boolean) {\n    category (storeId: $storeId, slug: $slug, inStock: $in_stock, eshopAvailability: $eshop_order, isPromo: $is_action, priceLevels: $price_levels) {\n      id\n      name\n      slug\n      id\n      parent_id\n      meta {\n        description\n        h1\n        title\n        keywords\n      }\n      disclaimer\n      description {\n        top\n        main\n        bottom\n      }\n#      treeBranch {\n#        id\n#        name\n#        slug\n#        children {\n#          category_type\n#          id\n#          name\n#          slug\n#          children {\n#            category_type\n#            id\n#            name\n#            slug\n#            children {\n#              category_type\n#              id\n#              name\n#              slug\n#              children {\n#                category_type\n#                id\n#                name\n#                slug\n#              }\n#            }\n#          }\n#        }\n#      }\n      breadcrumbs {\n        category_type\n        id\n        name\n        parent_id\n        parent_slug\n        slug\n      }\n      promo_banners {\n        id\n        image\n        name\n        category_ids\n        virtual_ids\n        type\n        sort_order\n        url\n        is_target_blank\n        analytics {\n          name\n          category\n          brand\n          type\n          start_date\n          end_date\n        }\n      }\n\n\n      dynamic_categories(from: 0, size: 9999) {\n        slug\n        name\n        id\n        category_type\n      }\n      filters {\n        facets {\n          key\n          total\n          filter {\n            id\n            name\n            display_title\n            is_list\n            is_main\n            text_filter\n            is_range\n            category_id\n            category_name\n            values {\n              slug\n              text\n              total\n            }\n          }\n        }\n      }\n      total\n      prices {\n        max\n        min\n      }\n      pricesFiltered {\n        max\n        min\n      }\n      products(attributeFilters: $attributes, from: $from, size: $size, sort: $sort, fieldFilters: $filters)  {\n        health_warning\n        limited_sale_qty\n        id\n        slug\n        name\n        name_highlight\n        article\n        main_article\n        main_article_slug\n        is_target\n        category_id\n        url\n        images\n        pick_up\n        rating\n        icons {\n          id\n          badge_bg_colors\n          rkn_icon\n          caption\n          image\n          type\n          is_only_for_sales\n          stores\n          caption_settings {\n            colors\n            text\n          }\n          stores\n          sort\n          image_png\n          image_svg\n          description\n          end_date\n          start_date\n          status\n        }\n        manufacturer {\n          id\n          image\n          name\n        }\n        packing {\n          size\n          type\n          pack_factors {\n            instamart\n          }\n        }\n        stocks {\n          value\n          text\n          eshop_availability\n          scale\n          prices_per_unit {\n            old_price\n            offline {\n              price\n              old_price\n              type\n              offline_discount\n              offline_promo\n            }\n            price\n            is_promo\n            levels {\n              count\n              price\n            }\n            discount\n          }\n          prices {\n            price\n            is_promo\n            old_price\n            offline {\n              old_price\n              price\n              type\n              offline_discount\n              offline_promo\n            }\n            levels {\n              count\n              price\n            }\n            discount\n          }\n        }\n      }\n    }\n  }\n",
    "variables": {
        "isShouldFetchOnlyProducts": True,
        "slug": "pityevaya-voda-kulery",
        "storeId": location,
        "sort": "default",
        "size": AMOUNT,
        "from": 0,
        "filters": [
        {
            "field": "main_article",
            "value": "0"
        }
        ],
        "attributes": [],
        "in_stock": True,
        "eshop_order": False
    }
    })
    
    response = requests.request("POST", URL, data=payload,  headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None
    
    

def main(location: Location):
    data = get_data(location.value)
    if not data:
        print("Не удалось получить данные")
        return

    headers = ["id", "name", "original_price", "current_price", "brand", "link"]
    with open(f"metro_{location.name}.csv", 'w', encoding="UTF-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for product in data.get("data").get("category").get("products"):
            row = get_row(product)
            writer.writerow(row)


main(Location.MOSCOW)
main(Location.SPB)
