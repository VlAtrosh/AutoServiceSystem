# app/repositories/payment_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from typing import Optional, List
from datetime import datetime


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # ========== GET ==========
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Получить платёж по ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_by_order_id(self, order_id: str) -> List[Payment]:
        """Получить все платежи по заказу"""
        return self.db.query(Payment).filter(Payment.order_id == order_id).all()
    
    def get_by_client_id(self, client_id: str, limit: int = 50) -> List[Payment]:
        """Получить платежи клиента"""
        return self.db.query(Payment).filter(Payment.client_id == client_id).limit(limit).all()
    
    def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Получить платежи по статусу"""
        return self.db.query(Payment).filter(Payment.status == status).all()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Payment]:
        """Получить платежи за период"""
        return self.db.query(Payment).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).all()
    
    def get_pending_payments(self) -> List[Payment]:
        """Получить все ожидающие платежи"""
        return self.db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).all()
    
    # ========== CREATE ==========
    def create(self, payment: Payment) -> Payment:
        """Создать платёж"""
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    # ========== UPDATE ==========
    def update(self, payment: Payment) -> Payment:
        """Обновить платёж"""
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    # ========== DELETE ==========
    def delete(self, payment: Payment) -> None:
        """Удалить платёж"""
        self.db.delete(payment)
        self.db.commit()
    
    # ========== STATISTICS ==========
    def get_order_total_paid(self, order_id: str) -> float:
        """Сумма оплаченных платежей по заказу"""
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.PAID
        ).first()
        return result[0] or 0.0
    
    def get_statistics(self, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Получить статистику по платежам"""
        query = self.db.query(Payment)
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        # Общая статистика
        total_paid = query.filter(Payment.status == PaymentStatus.PAID).with_entities(func.sum(Payment.amount)).scalar() or 0
        total_pending = query.filter(Payment.status == PaymentStatus.PENDING).with_entities(func.sum(Payment.amount)).scalar() or 0
        total_refunded = query.filter(Payment.status == PaymentStatus.REFUNDED).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        # Статистика по методам оплаты
        by_method = {}
        for method in PaymentMethod:
            amount = query.filter(Payment.method == method, Payment.status == PaymentStatus.PAID).with_entities(func.sum(Payment.amount)).scalar() or 0
            if amount > 0:
                by_method[method.value] = amount
        
        return {
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_refunded": total_refunded,
            "payments_count": query.count(),
            "by_method": by_method
        }
    
    def get_unpaid_order_ids(self) -> List[str]:
        """Получить ID заказов, у которых есть неоплаченные платежи"""
        subquery = self.db.query(Payment.order_id).filter(
            Payment.status == PaymentStatus.PENDING
        ).distinct().subquery()
        return [row[0] for row in self.db.query(subquery.c.order_id).all()]