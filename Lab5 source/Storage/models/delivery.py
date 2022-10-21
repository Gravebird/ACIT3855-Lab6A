from sqlalchemy import Column, Integer, String
from models.base import Base
import datetime


class Delivery(Base):

    __tablename__ = "delivery"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(String(250), nullable=False)
    delivery_id = Column(Integer, nullable=False)
    delivery_datetime = Column(String(100), nullable=False)
    bun_trays_received = Column(Integer, nullable=True)
    cheese_boxes_received = Column(Integer, nullable=True)
    fry_boxes_received = Column(Integer, nullable=True)
    patty_boxes_received = Column(Integer, nullable=True)
    trace_id = Column(Integer, nullable=False)


    def __init__(self, restaurant_id, delivery_id, bun_trays_received, cheese_boxes_received, fry_boxes_received, patty_boxes_received, trace_id):
        self.restaurant_id = restaurant_id
        self.delivery_id = delivery_id
        self.delivery_datetime = datetime.datetime.now()
        self.bun_trays_received = bun_trays_received
        self.cheese_boxes_received = cheese_boxes_received
        self.fry_boxes_received = fry_boxes_received
        self.patty_boxes_received = patty_boxes_received
        self.trace_id = trace_id

    
    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['restaurant_id'] = self.restaurant_id
        dict['delivery_id'] = self.delivery_id
        dict['delivery_datetime'] = self.delivery_datetime
        dict['bun_trays_received'] = self.bun_trays_received
        dict['cheese_boxes_received'] = self.cheese_boxes_received
        dict['fry_boxes_received'] = self.fry_boxes_received
        dict['patty_boxes_received'] = self.patty_boxes_received
        dict['trace_id'] = self.trace_id

        return dict