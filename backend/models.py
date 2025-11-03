"""SQLAlchemy models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, DECIMAL, Text, CHAR
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubBrand(Base):
    __tablename__ = "sub_brands"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    state = Column(String(2))
    district = Column(String(100))
    address_street = Column(String(200))
    address_number = Column(Integer)
    zipcode = Column(String(10))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    is_active = Column(Boolean, default=True)
    is_own = Column(Boolean, default=False)
    is_holding = Column(Boolean, default=False)
    creation_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    type = Column(CHAR(1))  # P=Presencial, D=Delivery
    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    name = Column(String(200), nullable=False)
    type = Column(CHAR(1), default='P')  # P=Produto, I=Item
    pos_uuid = Column(String(100))
    deleted_at = Column(DateTime)


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(500), nullable=False)
    pos_uuid = Column(String(100))
    deleted_at = Column(DateTime)


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(500), nullable=False)
    pos_uuid = Column(String(100))
    deleted_at = Column(DateTime)


class OptionGroup(Base):
    __tablename__ = "option_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(500), nullable=False)
    pos_uuid = Column(String(100))
    deleted_at = Column(DateTime)


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(50))
    cpf = Column(String(100))
    birth_date = Column(Date)
    gender = Column(String(10))
    store_id = Column(Integer, ForeignKey("stores.id"))
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    registration_origin = Column(String(20))
    agree_terms = Column(Boolean, default=False)
    receive_promotions_email = Column(Boolean, default=False)
    receive_promotions_sms = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    sub_brand_id = Column(Integer, ForeignKey("sub_brands.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, index=True)
    
    cod_sale1 = Column(String(100))
    cod_sale2 = Column(String(100))
    created_at = Column(DateTime, nullable=False, index=True)
    customer_name = Column(String(100))
    sale_status_desc = Column(String(100), nullable=False, index=True)
    
    total_amount_items = Column(DECIMAL(10, 2), nullable=False)
    total_discount = Column(DECIMAL(10, 2), default=0)
    total_increase = Column(DECIMAL(10, 2), default=0)
    delivery_fee = Column(DECIMAL(10, 2), default=0)
    service_tax_fee = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    value_paid = Column(DECIMAL(10, 2), default=0)
    
    production_seconds = Column(Integer)
    delivery_seconds = Column(Integer)
    people_quantity = Column(Integer)
    
    discount_reason = Column(String(300))
    increase_reason = Column(String(300))
    origin = Column(String(100), default='POS')
    
    # Relationships
    store = relationship("Store")
    channel = relationship("Channel")
    customer = relationship("Customer")
    product_sales = relationship("ProductSale", back_populates="sale")
    payments = relationship("Payment", back_populates="sale")
    delivery_sale = relationship("DeliverySale", back_populates="sale", uselist=False)


class ProductSale(Base):
    __tablename__ = "product_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    observations = Column(String(300))
    
    sale = relationship("Sale", back_populates="product_sales")
    product = relationship("Product")
    item_product_sales = relationship("ItemProductSale", back_populates="product_sale")


class ItemProductSale(Base):
    __tablename__ = "item_product_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_sale_id = Column(Integer, ForeignKey("product_sales.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    option_group_id = Column(Integer, ForeignKey("option_groups.id"))
    quantity = Column(Float, nullable=False)
    additional_price = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, default=1)
    observations = Column(String(300))
    
    product_sale = relationship("ProductSale", back_populates="item_product_sales")
    item = relationship("Item")
    option_group = relationship("OptionGroup")


class ItemItemProductSale(Base):
    __tablename__ = "item_item_product_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    item_product_sale_id = Column(Integer, ForeignKey("item_product_sales.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    option_group_id = Column(Integer, ForeignKey("option_groups.id"))
    quantity = Column(Float, nullable=False)
    additional_price = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, default=1)


class DeliverySale(Base):
    __tablename__ = "delivery_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    courier_name = Column(String(200))
    courier_phone = Column(String(50))
    courier_type = Column(String(100))
    delivery_type = Column(String(100))
    status = Column(String(100))
    delivery_fee = Column(DECIMAL(10, 2))
    courier_fee = Column(DECIMAL(10, 2))
    mode = Column(String(100))
    
    sale = relationship("Sale", back_populates="delivery_sale")
    delivery_address = relationship("DeliveryAddress", back_populates="delivery_sale", uselist=False)


class DeliveryAddress(Base):
    __tablename__ = "delivery_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    delivery_sale_id = Column(Integer, ForeignKey("delivery_sales.id"))
    address_street = Column(String(200))
    address_number = Column(String(20))
    address_complement = Column(String(100))
    address_reference = Column(String(200))
    district = Column(String(100))
    city = Column(String(100))
    state = Column(String(2))
    postal_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    delivery_sale = relationship("DeliverySale", back_populates="delivery_address")


class PaymentType(Base):
    __tablename__ = "payment_types"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    description = Column(String(100), nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_type_id = Column(Integer, ForeignKey("payment_types.id"), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    is_online = Column(Boolean, default=False)
    currency = Column(String(10), default='BRL')
    
    sale = relationship("Sale", back_populates="payments")
    payment_type = relationship("PaymentType")


class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    code = Column(String(100))
    description = Column(String(200))
    discount_type = Column(String(50))
    discount_value = Column(DECIMAL(10, 2))
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)


class CouponSale(Base):
    __tablename__ = "coupon_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    coupon_id = Column(Integer, ForeignKey("coupons.id"))
    discount_applied = Column(DECIMAL(10, 2))
    sponsorship = Column(String(100))
