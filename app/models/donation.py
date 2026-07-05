from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import validates, relationship

from app.core.db import Base


class Donation(Base):
    """Модель пожертвования фонда QRKot."""

    __tablename__ = 'donation'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=True)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    close_date = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    user = relationship("User", back_populates="donations")

    @validates('full_amount')
    def validate_full_amount(self, key, value):
        """Валидация суммы пожертвования (больше 0)."""
        if value <= 0:
            raise ValueError('Сумма пожертвования должна быть больше 0')
        return value

    @validates('invested_amount')
    def validate_invested_amount(self, key, value):
        """Валидация инвестированной суммы (не может быть отрицательной)."""
        if value < 0:
            raise ValueError(
                'Инвестированная сумма не может быть отрицательной'
            )
        return value

    @validates('comment')
    def validate_comment(self, key, value):
        """Валидация комментария (очистка от лишних пробелов)."""
        if value is not None:
            return value.strip()
        return value

    def __repr__(self):
        return f'<Donation {self.id} amount={self.full_amount}>'