CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sub_brands (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(2),
    district VARCHAR(100),
    address_street VARCHAR(200),
    address_number INTEGER,
    zipcode VARCHAR(10),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    is_active BOOLEAN DEFAULT true,
    is_own BOOLEAN DEFAULT false,
    is_holding BOOLEAN DEFAULT false,
    creation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    type CHAR(1) CHECK (type IN ('P', 'D')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    name VARCHAR(200) NOT NULL,
    type CHAR(1) DEFAULT 'P',
    pos_uuid VARCHAR(100),
    deleted_at TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(500) NOT NULL,
    pos_uuid VARCHAR(100),
    deleted_at TIMESTAMP
);

CREATE TABLE option_groups (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(500) NOT NULL,
    pos_uuid VARCHAR(100),
    deleted_at TIMESTAMP
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(500) NOT NULL,
    pos_uuid VARCHAR(100),
    deleted_at TIMESTAMP
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone_number VARCHAR(50),
    cpf VARCHAR(100),
    birth_date DATE,
    gender VARCHAR(10),
    store_id INTEGER REFERENCES stores(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    registration_origin VARCHAR(20),
    agree_terms BOOLEAN DEFAULT false,
    receive_promotions_email BOOLEAN DEFAULT false,
    receive_promotions_sms BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    sub_brand_id INTEGER REFERENCES sub_brands(id),
    customer_id INTEGER REFERENCES customers(id),
    channel_id INTEGER NOT NULL REFERENCES channels(id),
    
    cod_sale1 VARCHAR(100),
    cod_sale2 VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    customer_name VARCHAR(100),
    sale_status_desc VARCHAR(100) NOT NULL,
    
    total_amount_items DECIMAL(10,2) NOT NULL,
    total_discount DECIMAL(10,2) DEFAULT 0,
    total_increase DECIMAL(10,2) DEFAULT 0,
    delivery_fee DECIMAL(10,2) DEFAULT 0,
    service_tax_fee DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    value_paid DECIMAL(10,2) DEFAULT 0,
    
    production_seconds INTEGER,
    delivery_seconds INTEGER,
    people_quantity INTEGER,
    
    discount_reason VARCHAR(300),
    increase_reason VARCHAR(300),
    origin VARCHAR(100) DEFAULT 'POS'
);

CREATE TABLE product_sales (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity FLOAT NOT NULL,
    base_price FLOAT NOT NULL,
    total_price FLOAT NOT NULL,
    observations VARCHAR(300)
);

CREATE TABLE item_product_sales (
    id SERIAL PRIMARY KEY,
    product_sale_id INTEGER NOT NULL REFERENCES product_sales(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    option_group_id INTEGER REFERENCES option_groups(id),
    quantity FLOAT NOT NULL,
    additional_price FLOAT NOT NULL,
    price FLOAT NOT NULL,
    amount FLOAT DEFAULT 1,
    observations VARCHAR(300)
);

CREATE TABLE item_item_product_sales (
    id SERIAL PRIMARY KEY,
    item_product_sale_id INTEGER NOT NULL REFERENCES item_product_sales(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    option_group_id INTEGER REFERENCES option_groups(id),
    quantity FLOAT NOT NULL,
    additional_price FLOAT NOT NULL,
    price FLOAT NOT NULL,
    amount FLOAT DEFAULT 1
);

CREATE TABLE delivery_sales (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    courier_name VARCHAR(200),
    courier_phone VARCHAR(50),
    courier_type VARCHAR(100),
    delivery_type VARCHAR(100),
    status VARCHAR(100),
    delivery_fee DECIMAL(10,2),
    courier_fee DECIMAL(10,2),
    mode VARCHAR(100)
);

CREATE TABLE delivery_addresses (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id),
    delivery_sale_id INTEGER REFERENCES delivery_sales(id),
    address_street VARCHAR(200),
    address_number VARCHAR(20),
    address_complement VARCHAR(100),
    address_reference VARCHAR(200),
    district VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(2),
    postal_code VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE payment_types (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    description VARCHAR(100) NOT NULL
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    payment_type_id INTEGER NOT NULL REFERENCES payment_types(id),
    value DECIMAL(10,2) NOT NULL,
    is_online BOOLEAN DEFAULT false,
    currency VARCHAR(10) DEFAULT 'BRL'
);

CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    code VARCHAR(100),
    description VARCHAR(200),
    discount_type VARCHAR(50),
    discount_value DECIMAL(10,2),
    valid_from TIMESTAMP,
    valid_until TIMESTAMP
);

CREATE TABLE coupon_sales (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id),
    coupon_id INTEGER REFERENCES coupons(id),
    discount_applied DECIMAL(10,2),
    sponsorship VARCHAR(100)
);

-- Índices para performance
CREATE INDEX idx_sales_created_at ON sales(created_at);
CREATE INDEX idx_sales_store_id ON sales(store_id);
CREATE INDEX idx_sales_channel_id ON sales(channel_id);
CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_status ON sales(sale_status_desc);
CREATE INDEX idx_product_sales_sale_id ON product_sales(sale_id);
CREATE INDEX idx_product_sales_product_id ON product_sales(product_id);
CREATE INDEX idx_payments_sale_id ON payments(sale_id);
CREATE INDEX idx_delivery_sales_sale_id ON delivery_sales(sale_id);
