from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class TitleBasics(BaseModel):
    __tablename__ = "TitleBasics"
    fields = (
        ('titleId', 'titleId', 'char(9)'),
        ('ordering', None, 'int'),
        ('title', None, 'nvarchar(255)'),
        ('region', None, 'nvarchar(4)'),
        ('language', None, 'nvarchar(3)'),
        ('types', None, 'nvarchar(20)'),
        ('attributes', None, 'nvarchar(255)'),
        ('isOriginalTitle', 'isOriginalTitle', 'int'),
    )

    titleId: str = Column(
        String(9),
        primary_key=True,
        nullable=False
    )
    ordering: int = Column(
        Integer,
        nullable=False
    )
    title: str = Column(
        String,
        nullable=False
    )
    region: str = Column(
        String,
        nullable=False
    )

    principals = relationship("TitlePrincipal")
    akas = relationship("TitleAkas", lazy='dynamic')
    crew = relationship("TitleCrew")

    def __repr__(self):
        return '<TitleBasics model {}>'.format(self.titleId)
