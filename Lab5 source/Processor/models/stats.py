from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base

class InventoryStats(Base):
    """ Processing Statistics """

    __tablename__ = "InventoryStats"

    id = Column(Integer, primary_key=True)
    num_daily_sales_events = Column(Integer, nullable=False)
    max_cheeseburgers_sold = Column(Integer, nullable=True)
    max_fry_servings_sold = Column(Integer, nullable=True)
    max_hamburgers_sold = Column(Integer, nullable=True)
    num_delivery_events = Column(Integer, nullable=False)
    max_bun_trays_received = Column(Integer, nullable=True)
    max_fry_boxes_received = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_daily_sales, max_cheeseburgers_sold,
                max_fry_servings_sold, max_hamburgers_sold,
                num_delivery_events, max_bun_trays_received,
                max_fry_boxes_received, last_updated):
        """ Initializes a processing statistics object """
        self.num_daily_sales_events = num_daily_sales
        self.max_cheeseburgers_sold = max_cheeseburgers_sold
        self.max_fry_servings_sold = max_fry_servings_sold
        self.max_hamburgers_sold = max_hamburgers_sold
        self.num_delivery_events = num_delivery_events
        self.max_bun_trays_received = max_bun_trays_received
        self.max_fry_boxes_received = max_fry_boxes_received
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_daily_sales_events'] = self.num_daily_sales_events
        dict['max_cheeseburgers_sold'] = self.max_cheeseburgers_sold
        dict['max_fry_servings_sold'] = self.max_fry_servings_sold
        dict['max_hamburgers_sold'] = self.max_hamburgers_sold
        dict['num_delivery_events'] = self.num_delivery_events
        dict['max_bun_trays_received'] = self.max_bun_trays_received
        dict['max_fry_boxes_received'] = self.max_fry_boxes_received
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")

        return dict