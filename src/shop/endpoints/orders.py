from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.shop.db import get_db
from src.shop.models import Product, Order, OrderItem, Admin
from src.shop.models.orders import OrderStatus
from src.shop.schemas.orders import OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
):
    product_ids = [item.product_id for item in order_in.items]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=400,
            detail="No se puede repetir un producto dentro del pedido",
        )

    products = (
        db.query(Product)
        .filter(
            Product.id.in_(product_ids),
            Product.is_active == True,
        )
        .all()
    )

    products_by_id = {product.id: product for product in products}

    missing_ids = [
        product_id for product_id in product_ids if product_id not in products_by_id
    ]

    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail="Uno o más productos ya no están disponibles",
        )
    assigned_admin = (
        db.query(Admin)
        .filter(
            Admin.id == order_in.assigned_admin_id,
            Admin.is_active == True,
        )
        .first()
    )

    if not assigned_admin:
        raise HTTPException(
            status_code=400,
            detail="El administrador seleccionado no existe o está inactivo",
        )

    order = Order(
        customer_name=order_in.customer_name.strip(),
        customer_phone=order_in.customer_phone.strip(),
        customer_address=order_in.customer_address,
        comments=order_in.comments,
        assigned_admin_id=assigned_admin.id,
        status=OrderStatus.pending,
    )

    for requested_item in order_in.items:
        product = products_by_id[requested_item.product_id]

        current_price = (
            product.sale_price
            if product.is_on_sale and product.sale_price is not None
            else product.price
        )

        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=requested_item.quantity,
                price_at_time=current_price,
                current_price=current_price,
            )
        )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "status": order.status.value,
        "created_at": order.created_at,
    }
