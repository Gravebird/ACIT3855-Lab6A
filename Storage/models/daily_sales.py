from sqlalchemy import Column, Integer, String
from models.base import Base
import datetime


class DailySales(Base):
    """ Daily Sales """

    __tablename__ = "daily_sales"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(String(250), nullable=False)
    inventory_datetime = Column(String(100), nullable=False)
    cheeseburgers_sold = Column(Integer, nullable=True)
    hamburgers_sold = Column(Integer, nullable=True)
    fry_servings_sold = Column(Integer, nullable=True)
    trace_id = Column(Integer, nullable=False)


    def __init__(self, restaurant_id, cheeseburgers_sold, hamburgers_sold, fry_servings_sold, trace_id):
        self.restaurant_id = restaurant_id
        self.inventory_datetime = datetime.datetime.now()
        self.cheeseburgers_sold = cheeseburgers_sold
        self.hamburgers_sold = hamburgers_sold
        self.fry_servings_sold = fry_servings_sold
        self.trace_id = trace_id


    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['restaurant_id'] = self.restaurant_id
        dict['inventory_datetime'] = self.inventory_datetime
        dict['cheeseburgers_sold'] = self.cheeseburgers_sold
        dict['hamburgers_sold'] = self.hamburgers_sold
        dict['fry_servings_sold'] = self.fry_servings_sold
        dict['trace_id'] = self.trace_id

        return dict