from db_helpers import get_db_connection

items = [
    # Accessories
    ("Studded Belt", "accessories", "/images/accessories/belt1.png"),
    ("Stacked Bracelets", "accessories", "/images/accessories/bracelets.png"),
    ("Cross Earrings", "accessories", "/images/accessories/cross_earrings.png"),
    ("Hat with Dangles", "accessories", "/images/accessories/hat_dangle.png"),
    ("Paint Splatter Hat", "accessories", "/images/accessories/hat_paint_splatter.png"),
    ("Pirate Hat", "accessories", "/images/accessories/hat_pirate.png"),
    ("Hat with Red Bow", "accessories", "/images/accessories/hat_red_bow.png"),
    ("Bold Makeup", "accessories", "/images/accessories/makeup.png"),
    ("Statement Sunglasses", "accessories", "/images/accessories/sunglasses.png"),
    ("Skinny Tie", "accessories", "/images/accessories/tie.png"),
    # Dresses
    ("Red Dress", "dresses", "/images/dresses/red_dress1.png"),
    # Jackets
    ("Black Pleather Jacket", "jackets", "/images/jacket/black_pleather_jacket.png"),
    ("Black Short Jacket", "jackets", "/images/jacket/black_short_jkt.png"),
    ("Black Cropped Jacket", "jackets", "/images/jacket/black_short_jkt2.png"),
    ("Burgundy Short Jacket", "jackets", "/images/jacket/burgundy_short_jacket.png"),
    ("Statement Jacket", "jackets", "/images/jacket/jacket1.png"),
    ("Vintage Jacket", "jackets", "/images/jacket/jacket2.png"),
    ("Oversized Sweater", "jackets", "/images/jacket/sweater.png"),
    ("Fitted Vest", "jackets", "/images/jacket/vest.png"),
    # Pants
    ("Gray Tailored Pants", "pants", "/images/pants/mens_gray_pants.png"),
    ("Black Tailored Pants", "pants", "/images/pants/pants_black_taiilored.png"),
    ("Black Pants", "pants", "/images/pants/pants_black.png"),
    ("Plaid Pants", "pants", "/images/pants/pants_checks_plaid.png"),
    ("Polka Dot Pants", "pants", "/images/pants/pants_dots.png"),
    # Shirts
    ("Paint Splatter Shirt", "shirts", "/images/shirts/paint_splatter_shirt.png"),
    # Shoes
    ("Black Boots", "shoes", "/images/shoes/black_boots.png"),
    ("Ankle Boots", "shoes", "/images/shoes/black_boots2.png"),
    ("Tall Black Boots", "shoes", "/images/shoes/black_boots3.png"),
    ("High Heel Shoes", "shoes", "/images/shoes/high_heel_shoes.png"),
    # Skirts
    ("Black Pleather Mini Skirt", "skirts", "/images/skirts/black_pleather_mini_skirt.png"),
]

def seed():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM catalog_items;")

    for name, category, image_url in items:
        cursor.execute(
            "INSERT INTO catalog_items (name, category, image_url) VALUES (%s, %s, %s);",
            (name, category, image_url)
        )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    seed()