# car.py
"""The car module defines the Car class and related functionality for managing each individual car in the dealership inventory.
 It also includes custom management for car status and pricing rules."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, ClassVar, Dict, Literal

# A car's status can only be one of these three literal strings
CarStatus = Literal["Available", "Sold", "Reserved"]

class PermissionError(Exception):
    pass

class VINExistsError(ValueError):
    pass

@dataclass
class Car:
    vin: str
    year: int
    make: str
    model: str
    colour: str
    cost: float  # The price the dealership paid for the car
    price: float # The price the car is being sold for
    
    delivery_date: Optional[date] = None
    status: CarStatus = field(default="Available", init=False)
    sold_date: Optional[date] = field(default=None, init=False)

    _registry: ClassVar[Dict[str, "Car"]] = {}
    MIN_PROFIT_MARGIN: ClassVar[float] = 0.10 # 10% minimum profit

    def __post_init__(self):
        vin = self.vin.strip().upper()
        if not vin:
            raise ValueError("VIN must be a non-empty string.")
        if vin in Car._registry:
            raise VINExistsError(f"VIN {vin} already exists.")
        if self.cost < 0 or self.price < 0:
            raise ValueError("Cost and Price must be >= 0.")
        
        # Enforce profit margin at creation time
        min_price = self.cost * (1 + self.MIN_PROFIT_MARGIN)
        if self.price < min_price:
            raise ValueError(f"Initial price ${self.price:,.2f} is below the minimum profitable price of ${min_price:,.2f}.")

        self.vin = vin
        Car._registry[vin] = self

    def __repr__(self) -> str:
        return f"<Car {self.vin} | {self.year} {self.make} {self.model} | {self.colour} | ${self.price:,.2f} | {self.status}>"
    def is_available(self) -> bool:
        return self.status == "Available"

    def sell(self, sold_on: Optional[date] = None):
        if self.status != "Available":
            raise ValueError(f"Car is not available to be sold. Current status: {self.status}")
        self.status = "Sold"
        self.sold_date = sold_on or date.today()

    def reserve(self):
        if not self.is_available():
            raise ValueError(f"Car is not available to be reserved. Current status: {self.status}")
        self.status = "Reserved"

    def mark_available(self):
        self.status = "Available"
        self.sold_date = None

    def _require_admin(self, admin: bool):
        if not admin:
            raise PermissionError("Admin privileges required for this operation.")

    def update_price(self, new_price: float, admin: bool = False):
        """Updates the selling price of the car.
        Sellers can only update if the new price maintains the minimum profit margin.
        Admins can override this restriction.
        """
        min_price = self.cost * (1 + self.MIN_PROFIT_MARGIN)
        if new_price < 0:
            raise ValueError("Price must be >= 0.")
        
        if not admin and new_price < min_price:
            raise PermissionError(f"Price cannot be set below the minimum profit margin. Minimum price: ${min_price:,.2f}")
            
        self.price = float(new_price)

    def update_make(self, new_make: str, admin: bool = False):
        self._require_admin(admin)
        if not new_make:
            raise ValueError("Make must be non-empty.")
        self.make = new_make

    def update_model(self, new_model: str, admin: bool = False):
        self._require_admin(admin)
        if not new_model:
            raise ValueError("Model must be non-empty.")
        self.model = new_model

    def update_colour(self, new_colour: str, admin: bool = False):
        self._require_admin(admin)
        if not new_colour:
            raise ValueError("Colour must be non-empty.")
        self.colour = new_colour

    def update_year(self, new_year: int, admin: bool = False):
        self._require_admin(admin)
        if new_year <= 0:
            raise ValueError("Year must be a positive integer.")
        self.year = int(new_year)
    
    def update_status(self, new_status: CarStatus, admin: bool = False):
        """Allows a Seller or Admin to manually update a car's status."""
        if new_status not in ["Available", "Sold", "Reserved"]:
            raise ValueError("Invalid status provided.")
        
        # A seller can't un-sell a car, but an admin can.
        if self.status == "Sold" and not admin:
            raise PermissionError("Only an Admin can change the status of a sold car.")

        self.status = new_status
        if new_status == "Sold" and not self.sold_date:
            self.sold_date = date.today()
        elif new_status in ["Available", "Reserved"]:
            self.sold_date = None

    @classmethod
    def get_by_vin(cls, vin: str):
        return cls._registry.get(vin.strip().upper())

    @classmethod
    def all_cars(cls) -> Dict[str, "Car"]:
        return dict(cls._registry)