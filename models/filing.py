from database import Base
from sqlalchemy import Column, DateTime, Integer, String


class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True)
    ticker = Column(String(8), unique=True, index=True)
    company_name = Column(String(64))
    form_type = Column(String(8))
    filed_date = Column(DateTime)
    end_date = Column(DateTime)
    link = Column(String(256))

    def __repr__(self):
        return f"Filing(id={self.id}, ticker={self.ticker}, company_name={self.company_name})"
