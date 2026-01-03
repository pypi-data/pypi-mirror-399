from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, LargeBinary, Enum
from .base import Base
import enum

class LeafType(enum.Enum):
    STRUCTURE = "structure"
    ACTION = "action"

class Leaf(Base):
    __tablename__ = "leaves"

    leaf_index = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String(255), nullable=False)
    type = Column(Enum(LeafType), nullable=False)

class Structure(Base):
    __tablename__ = "structures"
    __table_args__ = (
        UniqueConstraint("org_name", "can_structure", name="uq_can_structure"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    raw_structure = Column(String(500), nullable=False)
    can_structure = Column(String(500), nullable=False)
    structure_hash = Column(String(64), nullable=False)
    leaf_index = Column(Integer, nullable=False)
    tree_size = Column(Integer, nullable=False)
    root_hash = Column(String(64), nullable=False)
    signature = Column(String(128), nullable=False)

class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String(255), nullable=False)
    can_structure = Column(String(500), ForeignKey('structures.can_structure'), nullable=False)
    action = Column(String(500), nullable=False)
    action_hash = Column(String(64), nullable=False)
    leaf_index = Column(Integer, nullable=False)
    tree_size = Column(Integer, nullable=False)
    root_hash = Column(String(64), nullable=False)
    signature = Column(String(128), nullable=False)

class Packet(Base):
    __tablename__ = "packets"

    id = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String(255), nullable=False)
    serial_inclusion_peaks = Column(LargeBinary, nullable=False)
    serial_inclusion_path = Column(LargeBinary, nullable=False)
    serial_consistency_path = Column(LargeBinary, nullable=False)
    serial_consistency_old_peaks = Column(LargeBinary, nullable=False)
    serial_consistency_new_peaks = Column(LargeBinary, nullable=False)
    leaf_index = Column(Integer, nullable=False)
    tree_size = Column(Integer, nullable=False)
    root_hash = Column(String(64), nullable=False)
    signature = Column(String(128), nullable=False)



