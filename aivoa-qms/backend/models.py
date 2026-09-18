from sqlalchemy import Column, Integer, String, Text
from database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. Product & Batch Identification
    product_name = Column(String(255), nullable=True)
    batch_number = Column(String(100), nullable=True)
    
    # 2. Facility & Material Impact
    originating_site = Column(String(255), nullable=True)
    impacted_npm = Column(String(255), nullable=True)
    
    # 3. Defect Analysis
    complaint_category = Column(String(255), nullable=True)
    product_defect = Column(String(255), nullable=True)
    complaint_description = Column(Text, nullable=True)
    
    # 4. AI Copilot Risk Assessment
    severity = Column(String(50), nullable=True)
    suggested_next_action = Column(String(255), nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)
    
    # Meta Status
    status = Column(String(50), default="Pending Triage")