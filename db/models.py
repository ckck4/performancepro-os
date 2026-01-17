# db/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association tables for many‑to‑many relationships
trade_tags = Table(
    "trade_tags",
    Base.metadata,
    Column("trade_id", Integer, ForeignKey("trades.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

session_tags = Table(
    "session_tags",
    Base.metadata,
    Column("session_id", Integer, ForeignKey("sessions.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

# Trading entities
class Instrument(Base):
    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String)
    exchange = Column(String)
    tick_size = Column(Float)
    tick_value = Column(Float)

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    market = Column(String)
    notes = Column(Text)
    trades = relationship("Trade", back_populates="session")
    tags = relationship("Tag", secondary=session_tags, back_populates="sessions")

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    quantity = Column(Integer)
    direction = Column(Enum("LONG", "SHORT", name="trade_direction"))
    entry_price = Column(Float)
    exit_price = Column(Float)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    fees_commissions = Column(Float)
    session = relationship("Session", back_populates="trades")
    instrument = relationship("Instrument")
    strategy = relationship("Strategy")
    tags = relationship("Tag", secondary=trade_tags, back_populates="trades")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    trades = relationship("Trade", secondary=trade_tags, back_populates="tags")
    sessions = relationship("Session", secondary=session_tags, back_populates="tags")

# Business / lifetime finance entities
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    category = Column(String)
    amount = Column(Float)
    currency = Column(String)
    notes = Column(Text)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("funded_accounts.id"), nullable=True)
    vendor = relationship("Vendor")
    evaluation = relationship("Evaluation", back_populates="expenses")
    account = relationship("FundedAccount", back_populates="expenses")

class Payout(Base):
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    firm = Column(String)
    account_id = Column(Integer, ForeignKey("funded_accounts.id"))
    amount_gross = Column(Float)
    fees_withheld = Column(Float)
    amount_net = Column(Float)
    account = relationship("FundedAccount", back_populates="payouts")

class EvaluationProgram(Base):
    __tablename__ = "evaluation_programs"
    id = Column(Integer, primary_key=True)
    firm = Column(String)
    model = Column(String)
    rules = Column(Text)
    price = Column(Float)
    evaluations = relationship("Evaluation", back_populates="program")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("evaluation_programs.id"))
    purchase_date = Column(Date)
    status = Column(
        Enum("bought", "active", "passed", "failed", "expired", name="evaluation_status")
    )
    attempts_count = Column(Integer)
    resets_count = Column(Integer)
    cost_total = Column(Float)
    program = relationship("EvaluationProgram", back_populates="evaluations")
    expenses = relationship("Expense", back_populates="evaluation")
    funded_account = relationship("FundedAccount", back_populates="evaluation", uselist=False)

class FundedAccount(Base):
    __tablename__ = "funded_accounts"
    id = Column(Integer, primary_key=True)
    firm = Column(String)
    start_date = Column(Date)
    status = Column(Enum("active", "closed", name="account_status"))
    account_size = Column(Float)
    current_drawdown_buffer = Column(Float)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=True)
    evaluation = relationship("Evaluation", back_populates="funded_account")
    expenses = relationship("Expense", back_populates="account")
    payouts = relationship("Payout", back_populates="account")

# AI output entities
class AIReport(Base):
    __tablename__ = "ai_reports"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    period_start = Column(Date)
    period_end = Column(Date)
    summary = Column(Text)
    actions = Column(Text)
    confidence = Column(Float)

class AIObservation(Base):
    __tablename__ = "ai_observations"
    id = Column(Integer, primary_key=True)
    target_type = Column(String)
    target_id = Column(Integer)
    content = Column(Text)
    created_at = Column(DateTime)
