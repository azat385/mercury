from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DATETIME
#from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

db_name = "common_ts.db"
Base = declarative_base()


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, nullable=False, default=999)
    value = Column(REAL)
    ts = Column(DATETIME)

    def __repr__(self):
        return "<Data(id='{}', tag_id='{}' value='{}' timestamp='{}' )>".format(
            self.id,  self.tag_id, self.value, self.ts)


engine = create_engine('sqlite:///{}'.format(db_name), echo=False)

def create_db_and_table():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    create_db_and_table()
