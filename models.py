from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean
engine = create_engine('mysql://root:findout5@localhost/kyc', echo=False)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Registry(Base):
	__tablename__ = 'Registry'


	id = Column(Integer, primary_key=True)
    name_of_the_entity = Column(String(200),)
    legal_status = Column(String(200),)
    reg_no = Column(String(50),)
    reg_status = Column(String(50),)
    place_of_business = Column(String(50),)
    db_registry_url = Column(String(100),)
    db_registry_file_name = Column(String(100),)
    db_state_of_registry = Column(String(100),)
    reg_address = Column(String(200),)
    db_country = Column(String(100),)

    def __repr__(self):
	    return "<Registry('%s')>" % (self.name_of_the_entity)


registry_table = Registry.__table__
metadata = Base.metadata

def create_all():
    metadata.create_all(engine)

create_all()