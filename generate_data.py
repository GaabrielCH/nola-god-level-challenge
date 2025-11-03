#!/usr/bin/env python3
"""
God Level Coder Challenge - Data Generator
Generates realistic restaurant data based on Arcca's actual models
"""
import argparse
import random
import psycopg2
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from psycopg2.extras import execute_batch
from faker import Faker

fake = Faker('pt_BR')

# Configurations
BRAND_ID = 1
SALES_STATUS = ['COMPLETED', 'CANCELLED']
STATUS_WEIGHTS = [0.95, 0.05]  # 95% completed
CATEGORIES_PRODUCTS = ['Burgers', 'Pizzas', 'Pratos', 'Combos', 'Sobremesas', 'Bebidas']
CATEGORIES_ITEMS = ['Complementos', 'Molhos', 'Adicionais']

# Realistic product prefixes
PRODUCT_PREFIXES = {
    'Burgers': ['X-Burger', 'Cheeseburger', 'Bacon Burger', 'Double Burger', 'Veggie Burger'],
    'Pizzas': ['Pizza Margherita', 'Pizza Calabresa', 'Pizza 4 Queijos', 'Pizza Portuguesa', 'Pizza Frango'],
    'Pratos': ['Prato Executivo', 'Filé', 'Frango Grelhado', 'Lasanha', 'Risoto'],
    'Combos': ['Combo Família', 'Combo Individual', 'Combo Duplo', 'Combo Kids', 'Combo Executivo'],
    'Sobremesas': ['Brownie', 'Pudim', 'Sorvete', 'Petit Gateau', 'Torta'],
    'Bebidas': ['Refrigerante', 'Suco', 'Água', 'Cerveja', 'Vinho']
}

ITEM_NAMES = {
    'Complementos': ['Bacon', 'Queijo Cheddar', 'Queijo Mussarela', 'Ovo', 'Alface', 'Tomate', 
                     'Cebola', 'Picles', 'Jalapeño', 'Cogumelos', 'Abacaxi', 'Catupiry'],
    'Molhos': ['Molho Barbecue', 'Molho Mostarda', 'Molho Especial', 'Maionese', 'Ketchup', 
               'Molho Picante', 'Molho Ranch', 'Molho Tártaro'],
    'Adicionais': ['Batata Frita', 'Onion Rings', 'Nuggets', 'Salada', 'Arroz', 'Feijão',
                   'Farofa', 'Vinagrete']
}

# Realistic patterns
HOURLY_WEIGHTS = {
    range(0, 6): 0.02, range(6, 11): 0.08, range(11, 15): 0.35,
    range(15, 19): 0.10, range(19, 23): 0.40, range(23, 24): 0.05
}

WEEKDAY_MULT = [0.8, 0.9, 0.95, 1.0, 1.3, 1.5, 1.4]  # Mon-Sun

CHANNELS = [
    ('Presencial', 'P', 0.40, 0),
    ('iFood', 'D', 0.30, 27),
    ('Rappi', 'D', 0.15, 25),
    ('Uber Eats', 'D', 0.08, 30),
    ('WhatsApp', 'D', 0.05, 0),
    ('App Próprio', 'D', 0.02, 0)
]

PAYMENT_TYPES_LIST = [
    'Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 
    'PIX', 'Vale Refeição', 'Vale Alimentação'
]

DISCOUNT_REASONS = [
    'Cupom de desconto', 'Promoção do dia', 'Cliente fidelidade',
    'Desconto gerente', 'Primeira compra', 'Aniversário'
]

DELIVERY_TYPES = ['DELIVERY', 'TAKEOUT', 'INDOOR']
COURIER_TYPES = ['PLATFORM', 'OWN', 'THIRD_PARTY']


def get_db_connection(db_url):
    return psycopg2.connect(db_url)


def get_hour_weight(hour):
    for hour_range, weight in HOURLY_WEIGHTS.items():
        if hour in hour_range:
            return weight
    return 0.01


def setup_base_data(conn):
    """Create brands, channels, payment types"""
    print("Setting up base data...")
    cursor = conn.cursor()
    
    # Brand
    cursor.execute("INSERT INTO brands (name) VALUES ('Nola God Level Brand') RETURNING id")
    brand_id = cursor.fetchone()[0]
    
    # Sub-brands
    sub_brands = ['Challenge Burger', 'Challenge Pizza', 'Challenge Sushi']
    sub_brand_ids = []

    for sb in sub_brands:
        cursor.execute(
            "INSERT INTO sub_brands (brand_id, name) VALUES (%s, %s) RETURNING id",
            (brand_id, sb)
        )
        sub_brand_ids.append(cursor.fetchone()[0])
    
    # Channels
    channel_ids = []
    for name, ch_type, weight, commission in CHANNELS:
        cursor.execute(
            """INSERT INTO channels (brand_id, name, type, description) 
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (brand_id, name, ch_type, f"Canal {name}")
        )
        channel_ids.append({
            'id': cursor.fetchone()[0],
            'name': name,
            'type': ch_type,
            'weight': weight,
            'commission': commission
        })
    
    # Payment types
    for pt in PAYMENT_TYPES_LIST:
        cursor.execute(
            "INSERT INTO payment_types (brand_id, description) VALUES (%s, %s)",
            (brand_id, pt)
        )
    
    conn.commit()
    print(f"✓ Base data: {len(sub_brand_ids)} sub-brands, {len(channel_ids)} channels")
    return brand_id, sub_brand_ids, channel_ids


def generate_stores(conn, sub_brand_ids, num_stores=50):
    """Generate realistic stores"""
    print(f"Generating {num_stores} stores...")
    cursor = conn.cursor()
    stores = []
    
    cities = [fake.city() for _ in range(20)]
    
    for i in range(num_stores):
        name = f"{random.choice(['Burguer House', 'Pizza Palace', 'Food Corner', 'Quick Bite'])} - {fake.city()}"
        city = random.choice(cities)
        state = random.choice(['SP', 'RJ', 'MG', 'RS', 'PR', 'SC'])
        
        cursor.execute("""
            INSERT INTO stores (
                brand_id, sub_brand_id, name, city, state, district,
                address_street, address_number, zipcode, latitude, longitude,
                is_active, is_own, creation_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            BRAND_ID,
            random.choice(sub_brand_ids),
            name,
            city,
            state,
            fake.bairro(),
            fake.street_name(),
            random.randint(1, 999),
            fake.postcode(),
            float(fake.latitude()),
            float(fake.longitude()),
            True,
            random.random() < 0.7,
            fake.date_between(start_date='-2y', end_date='-6m')
        ))
        stores.append(cursor.fetchone()[0])
    
    conn.commit()
    print(f"✓ {len(stores)} stores created")
    return stores


def generate_products_and_items(conn, sub_brand_ids, num_products=500, num_items=200):
    """Generate products, items, and option groups"""
    print(f"Generating {num_products} products and {num_items} items...")
    cursor = conn.cursor()
    
    products = []
    items = []
    option_groups = []
    
    # Product categories
    for cat_name in CATEGORIES_PRODUCTS:
        cursor.execute(
            "INSERT INTO categories (brand_id, sub_brand_id, name, type) VALUES (%s, %s, %s, %s) RETURNING id",
            (BRAND_ID, random.choice(sub_brand_ids), cat_name, 'P')
        )
        cat_id = cursor.fetchone()[0]
        
        # Generate products in this category
        num_in_cat = num_products // len(CATEGORIES_PRODUCTS)
        for _ in range(num_in_cat):
            prefix = random.choice(PRODUCT_PREFIXES[cat_name])
            suffix = random.choice(['Especial', 'Tradicional', 'Premium', 'Light', 'Grande'])
            name = f"{prefix} {suffix}"
            
            cursor.execute(
                "INSERT INTO products (brand_id, sub_brand_id, category_id, name) VALUES (%s, %s, %s, %s) RETURNING id",
                (BRAND_ID, random.choice(sub_brand_ids), cat_id, name)
            )
            products.append(cursor.fetchone()[0])
    
    # Item categories (for complements/additions)
    for cat_name in CATEGORIES_ITEMS:
        cursor.execute(
            "INSERT INTO categories (brand_id, sub_brand_id, name, type) VALUES (%s, %s, %s, %s) RETURNING id",
            (BRAND_ID, random.choice(sub_brand_ids), cat_name, 'I')
        )
        cat_id = cursor.fetchone()[0]
        
        # Generate items
        for item_name in ITEM_NAMES[cat_name]:
            cursor.execute(
                "INSERT INTO items (brand_id, sub_brand_id, category_id, name) VALUES (%s, %s, %s, %s) RETURNING id",
                (BRAND_ID, random.choice(sub_brand_ids), cat_id, item_name)
            )
            items.append(cursor.fetchone()[0])
    
    # Option groups
    option_group_names = ['Adicionais', 'Remover', 'Ponto da Carne', 'Tamanho']
    for og_name in option_group_names:
        cursor.execute(
            "INSERT INTO option_groups (brand_id, sub_brand_id, name) VALUES (%s, %s, %s) RETURNING id",
            (BRAND_ID, random.choice(sub_brand_ids), og_name)
        )
        option_groups.append(cursor.fetchone()[0])
    
    conn.commit()
    print(f"✓ {len(products)} products, {len(items)} items, {len(option_groups)} option groups")
    return products, items, option_groups


def generate_customers(conn, num_customers=10000):
    """Generate customers"""
    print(f"Generating {num_customers} customers...")
    cursor = conn.cursor()
    
    batch = []
    for _ in range(num_customers):
        batch.append((
            fake.name(),
            fake.email(),
            fake.phone_number(),
            fake.cpf(),
            fake.date_of_birth(minimum_age=18, maximum_age=70),
            random.choice(['M', 'F', 'Outro']),
            random.random() < 0.8,
            random.random() < 0.6,
        ))
    
    execute_batch(cursor, """
        INSERT INTO customers (
            customer_name, email, phone_number, cpf, birth_date, gender,
            agree_terms, receive_promotions_email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, batch)
    
    conn.commit()
    print(f"✓ {num_customers} customers created")


def generate_sales(conn, stores, channels, products, items, option_groups, months=6):
    """Generate sales with realistic patterns"""
    print(f"\nGenerating {months} months of sales data...")
    cursor = conn.cursor()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    # Get customer IDs
    cursor.execute("SELECT id FROM customers")
    customers = [row[0] for row in cursor.fetchall()]
    
    # Get payment type IDs
    cursor.execute("SELECT id FROM payment_types")
    payment_types = [row[0] for row in cursor.fetchall()]
    
    current_date = start_date
    sales_batch = []
    batch_size = 1000
    total_sales = 0
    
    while current_date < end_date:
        weekday = current_date.weekday()
        day_multiplier = WEEKDAY_MULT[weekday]
        
        # Sales per store per day
        for store_id in stores:
            daily_sales = int(random.gauss(30, 10) * day_multiplier)
            
            for _ in range(max(1, daily_sales)):
                # Random hour based on weights
                hour = random.choices(
                    list(range(24)),
                    weights=[get_hour_weight(h) for h in range(24)]
                )[0]
                
                sale_time = current_date.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Select channel
                channel = random.choices(channels, weights=[c['weight'] for c in channels])[0]
                
                # Customer (70% identified)
                customer_id = random.choice(customers) if random.random() < 0.7 else None
                
                sale_data = generate_single_sale(
                    sale_time, store_id, channel, customer_id,
                    products, items, option_groups, payment_types
                )
                
                sales_batch.append(sale_data)
                total_sales += 1
                
                if len(sales_batch) >= batch_size:
                    insert_sales_batch(cursor, sales_batch, items, option_groups)
                    conn.commit()
                    sales_batch = []
                    print(f"  ✓ Inserted {total_sales} sales... ({current_date.strftime('%Y-%m-%d')})")
        
        current_date += timedelta(days=1)
    
    # Insert remaining
    if sales_batch:
        insert_sales_batch(cursor, sales_batch, items, option_groups)
        conn.commit()
    
    print(f"\n✓ Total: {total_sales} sales generated!")


def generate_single_sale(sale_time, store_id, channel, customer_id, products, items, option_groups, payment_types):
    """Generate a single sale with products and customizations"""
    status = random.choices(SALES_STATUS, weights=STATUS_WEIGHTS)[0]
    
    # Number of products (1-5)
    num_products = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.2, 0.07, 0.03])[0]
    
    products_data = []
    total_items = 0
    
    for _ in range(num_products):
        product_id = random.choice(products)
        quantity = 1
        base_price = round(random.uniform(15, 85), 2)
        
        # Customizations (60% have them)
        customizations = []
        if random.random() < 0.6:
            num_customizations = random.randint(1, 4)
            for _ in range(num_customizations):
                item_id = random.choice(items)
                option_group_id = random.choice(option_groups)
                additional_price = round(random.uniform(0, 8), 2)
                
                customizations.append({
                    'item_id': item_id,
                    'option_group_id': option_group_id,
                    'quantity': 1,
                    'additional_price': additional_price,
                    'price': additional_price
                })
        
        product_total = base_price + sum(c['additional_price'] for c in customizations)
        total_items += product_total
        
        products_data.append({
            'product_id': product_id,
            'quantity': quantity,
            'base_price': base_price,
            'total_price': product_total,
            'customizations': customizations
        })
    
    # Discount (20% of sales)
    discount = 0
    discount_reason = None
    if random.random() < 0.2:
        discount = round(total_items * random.uniform(0.05, 0.25), 2)
        discount_reason = random.choice(DISCOUNT_REASONS)
    
    # Delivery fee
    delivery_fee = 0
    delivery_data = None
    if channel['type'] == 'D':
        delivery_fee = round(random.uniform(5, 15), 2)
        delivery_data = {
            'courier_name': fake.name(),
            'courier_phone': fake.phone_number(),
            'courier_type': random.choice(COURIER_TYPES),
            'delivery_type': random.choice(DELIVERY_TYPES),
            'status': 'DELIVERED' if status == 'COMPLETED' else 'CANCELLED',
            'delivery_fee': delivery_fee,
            'courier_fee': round(delivery_fee * 0.3, 2),
            'address': {
                'address_street': fake.street_name(),
                'address_number': str(random.randint(1, 999)),
                'district': fake.bairro(),
                'city': fake.city(),
                'state': random.choice(['SP', 'RJ', 'MG']),
                'postal_code': fake.postcode(),
                'latitude': float(fake.latitude()),
                'longitude': float(fake.longitude())
            }
        }
    
    total_amount = total_items - discount + delivery_fee
    
    # Payment
    num_payments = 1 if random.random() < 0.9 else 2
    payments_data = []
    remaining = total_amount
    
    for i in range(num_payments):
        payment_type_id = random.choice(payment_types)
        value = remaining if i == num_payments - 1 else round(remaining * random.uniform(0.3, 0.7), 2)
        remaining -= value
        
        payments_data.append({
            'payment_type_id': payment_type_id,
            'value': value,
            'is_online': random.random() < 0.6
        })
    
    # Times
    production_seconds = random.randint(300, 2400) if status == 'COMPLETED' else None
    delivery_seconds = random.randint(900, 3600) if channel['type'] == 'D' and status == 'COMPLETED' else None
    
    return {
        'store_id': store_id,
        'channel_id': channel['id'],
        'customer_id': customer_id,
        'created_at': sale_time,
        'status': status,
        'total_items': total_items,
        'discount': discount,
        'discount_reason': discount_reason,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'production_seconds': production_seconds,
        'delivery_seconds': delivery_seconds,
        'products': products_data,
        'payments': payments_data,
        'delivery': delivery_data
    }


def insert_sales_batch(cursor, sales_batch, items, option_groups):
    """Insert batch of sales with all relations"""
    for sale in sales_batch:
        # Insert sale
        cursor.execute("""
            INSERT INTO sales (
                store_id, channel_id, customer_id, created_at, sale_status_desc,
                total_amount_items, total_discount, delivery_fee, total_amount,
                value_paid, production_seconds, delivery_seconds, discount_reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sale['store_id'], sale['channel_id'], sale['customer_id'],
            sale['created_at'], sale['status'], sale['total_items'],
            sale['discount'], sale['delivery_fee'], sale['total_amount'],
            sale['total_amount'], sale['production_seconds'],
            sale['delivery_seconds'], sale['discount_reason']
        ))
        sale_id = cursor.fetchone()[0]
        
        # Insert products
        for product in sale['products']:
            cursor.execute("""
                INSERT INTO product_sales (
                    sale_id, product_id, quantity, base_price, total_price
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                sale_id, product['product_id'], product['quantity'],
                product['base_price'], product['total_price']
            ))
            product_sale_id = cursor.fetchone()[0]
            
            # Insert customizations
            for custom in product['customizations']:
                cursor.execute("""
                    INSERT INTO item_product_sales (
                        product_sale_id, item_id, option_group_id,
                        quantity, additional_price, price
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    product_sale_id, custom['item_id'], custom['option_group_id'],
                    custom['quantity'], custom['additional_price'], custom['price']
                ))
        
        # Insert payments
        for payment in sale['payments']:
            cursor.execute("""
                INSERT INTO payments (sale_id, payment_type_id, value, is_online)
                VALUES (%s, %s, %s, %s)
            """, (sale_id, payment['payment_type_id'], payment['value'], payment['is_online']))
        
        # Insert delivery
        if sale['delivery']:
            delivery = sale['delivery']
            cursor.execute("""
                INSERT INTO delivery_sales (
                    sale_id, courier_name, courier_phone, courier_type,
                    delivery_type, status, delivery_fee, courier_fee
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                sale_id, delivery['courier_name'], delivery['courier_phone'],
                delivery['courier_type'], delivery['delivery_type'],
                delivery['status'], delivery['delivery_fee'], delivery['courier_fee']
            ))
            delivery_sale_id = cursor.fetchone()[0]
            
            addr = delivery['address']
            cursor.execute("""
                INSERT INTO delivery_addresses (
                    sale_id, delivery_sale_id, address_street, address_number,
                    district, city, state, postal_code, latitude, longitude
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sale_id, delivery_sale_id, addr['address_street'],
                addr['address_number'], addr['district'], addr['city'],
                addr['state'], addr['postal_code'], addr['latitude'], addr['longitude']
            ))


def main():
    parser = argparse.ArgumentParser(description='Generate restaurant challenge data')
    parser.add_argument('--db-url', default='postgresql://challenge:challenge_2024@localhost:5432/challenge_db')
    parser.add_argument('--stores', type=int, default=50)
    parser.add_argument('--products', type=int, default=500)
    parser.add_argument('--items', type=int, default=200)
    parser.add_argument('--customers', type=int, default=10000)
    parser.add_argument('--months', type=int, default=6)
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("God Level Coder Challenge - Data Generator")
    print("=" * 60)
    
    conn = get_db_connection(args.db_url)
    
    try:
        brand_id, sub_brand_ids, channels = setup_base_data(conn)
        stores = generate_stores(conn, sub_brand_ids, args.stores)
        products, items, option_groups = generate_products_and_items(
            conn, sub_brand_ids, args.products, args.items
        )
        generate_customers(conn, args.customers)
        generate_sales(conn, stores, channels, products, items, option_groups, args.months)
        
        print("\n" + "=" * 60)
        print("✓ Data generation completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
