from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload

from src.shop.db import get_db
from src.shop.models import Product, Order, OrderItem, Admin
from src.shop.models.orders import OrderStatus
from src.shop.schemas.orders import OrderCreate, OrderCreated, OrderAdminListItem, OrderAdminDetail, OrderStatusUpdate, OrderStatusUpdated
from src.shop.schemas.auth import AdminContactPublic
from src.shop.dependencies import get_current_admin

router = APIRouter(prefix="/orders", tags=["orders"])
@router.get("/admins", response_model=list[AdminContactPublic])
def get_order_admins(db: Session = Depends(get_db)):
    return (
        db.query(Admin)
        .filter(Admin.is_active.is_(True))
        .order_by(Admin.name.asc())
        .all()
    )

@router.get("/admin/{order_id}", response_model=OrderAdminDetail)
def get_admin_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.assigned_admin),
            joinedload(Order.processed_by_admin),
            selectinload(Order.items).joinedload(OrderItem.product),
        )
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    total = sum(
        (item.price_at_time * item.quantity for item in order.items),
        Decimal("0.00"),
    )

    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "created_at": order.created_at,
        "status": order.status.value,
        "total": total,
        "assigned_admin_id": order.assigned_admin_id,
        "assigned_admin_name": order.assigned_admin.name,
        "customer_address": order.customer_address,
        "comments": order.comments,
        "processed_by_admin_name": (
            order.processed_by_admin.name if order.processed_by_admin else None
        ),
        "items": [
            {
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.price_at_time,
            }
            for item in order.items
        ],
    }
   
@router.get("/admin", response_model=list[OrderAdminListItem])
def get_admin_orders(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    status: OrderStatus | None = Query(default=None),
    assigned_admin_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = (
        db.query(Order)
        .options(
            joinedload(Order.assigned_admin),
            selectinload(Order.items),
        )
    )

    if status is not None:
        query = query.filter(Order.status == status)

    if assigned_admin_id is not None:
        query = query.filter(Order.assigned_admin_id == assigned_admin_id)

    orders = (
        query.order_by(Order.created_at.desc(), Order.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "created_at": order.created_at,
            "status": order.status.value,
            "total": sum(
                (item.price_at_time * item.quantity for item in order.items),
                Decimal("0.00"),
            ),
            "assigned_admin_id": order.assigned_admin_id,
            "assigned_admin_name": order.assigned_admin.name,
        }
        for order in orders
    ]
    
    
@router.patch(
    "/admin/{order_id}/status",
    response_model=OrderStatusUpdated,
)
def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    order.status = OrderStatus(status_in.status)
    order.processed_by_admin_id = current_admin.id

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "status": order.status.value,
        "processed_by_admin_id": current_admin.id,
        "processed_by_admin_name": current_admin.name,
    }

@router.post("/", response_model=OrderCreated)
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
        "comments": order.comments,
        "assigned_admin" : {
            "name":assigned_admin.name,
            "whatsapp_phone" : assigned_admin.whatsapp_phone
        },
        "items":  [{
            "name": order_item.product.name,
            "quantity": order_item.quantity,
            "unit_price": str(order_item.price_at_time),
        }
        for order_item in order.items
        ],
    }

    
    