from sqlalchemy import Column, String, Integer,Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class App_gstore(Base):
    __tablename__ = "gstore"
    ID = Column(Integer(), primary_key=True)
    app_ID = Column(Integer(), ForeignKey('apps.ID'))
    name = Column(String())
    publisher = Column(String(), unique=False)
    publisher_ID = Column(Integer())
    price = Column(Float())
    downloads = Column(Integer())
    rating = Column(Float())
    position = Column(Integer())
    date = Column(DateTime())

    app = relationship("App", back_populates="gstore_entries")

    def __init__(self, app, price, downloads, rating, position, date):
        self.app_ID = app.ID
        self.name = app.name
        self.publisher = app.publisher_name
        self.publisher_ID = app.publisher_ID
        self.price = price
        self.downloads = downloads
        self.rating = rating
        self.position = position
        self.date = date

    def __repr__(self):
        return (f"| {self.app_ID} || {self.name} || {self.publisher} || {self.price} || "
                f"{self.downloads} || {self.rating} || {self.position} || {self.date} |")    


class App(Base):
    __tablename__ = "apps"
    ID = Column(Integer(), primary_key=True)
    name = Column(String())
    publisher_ID = Column(Integer(), ForeignKey('publisher.ID'))
    publisher_name = Column(String())
    
    publisher = relationship("Publisher", back_populates="apps")
    gstore_entries = relationship("App_gstore", back_populates="app", cascade="all, delete-orphan")

    def __init__(self, name, publisher):
        self.name = name
        self.publisher_ID = publisher.ID
        self.publisher_name = publisher.name

    def __repr__(self):
        return f"App:{self.name} ID:{self.ID}"


class Publisher(Base):
    __tablename__ = "publisher"
    ID = Column(Integer(), primary_key=True)
    name = Column(String(), unique=True)
    apps = relationship("App", back_populates="publisher")

    def __repr__(self):
        return f"App:{self.name} \nID:{self.ID}"
