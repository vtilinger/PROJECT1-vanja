# ecommerce.py
""" The ecommerce module implements shopping cart, payment processing,
notification, and delivery scheduling functionalities for the car dealership system.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from car import Car
if TYPE_CHECKING:
    from auth import User

class Cart:
    def __init__(self, user: User):
        self.user = user
        self.items: dict[str, Car] = {}
        self.discount_code: str | None = None

    def add_item(self, car: Car):
        if not car.is_available():
            print(f"Sorry, {car.make} {car.model} is no longer available.")
            return
        if car.vin in self.items:
            print(f"{car.make} {car.model} is already in your cart.")
            return
        self.items[car.vin] = car
        print(f"Added {car.make} {car.model} to your cart.")

    def remove_item(self, vin: str):
        vin = vin.upper()
        if vin in self.items:
            removed_car = self.items.pop(vin)
            print(f"Removed {removed_car.make} {removed_car.model} from your cart.")
        else:
            print("That car is not in your cart.")

    def apply_discount(self, code: str):
        if code.upper() == "SAVE10":
            self.discount_code = code.upper()
            print("Applied 10% discount!")
            return True
        print("Invalid discount code.")
        return False

    def calculate_total(self) -> tuple[float, float]:
        subtotal = sum(car.price for car in self.items.values())
        discount_amount = 0.0
        if self.discount_code == "SAVE10":
            discount_amount = subtotal * 0.10
        
        total = subtotal - discount_amount
        return subtotal, total

    def display(self):
        if not self.items:
            print("\nYour shopping cart is empty.")
            return
        
        print("\n--- Your Shopping Cart ---")
        for car in self.items.values():
            print(f"- {car}")
        
        subtotal, total = self.calculate_total()
        print(f"\nSubtotal: ${subtotal:,.2f}")
        if self.discount_code:
            print(f"Discount ({self.discount_code}): -${(subtotal - total):,.2f}")
        print(f"Total: ${total:,.2f}")
        print("--------------------------")

class Payment:
    def process(self, total: float) -> bool:
        print(f"\nTotal amount due: ${total:,.2f}")
        card = input("Enter mock card number (e.g., 1234567812345678): ")
        if len(card) == 16 and card.isdigit():
            print("Processing payment...")
            print("Payment successful!")
            return True
        else:
            print("Payment failed. Invalid card number.")
            return False

class Notification:
    @staticmethod
    def send_order_confirmation(user: User, cart: Cart):
        print("\n--- Sending Notifications ---")
        print(f"To: Buyer ({user.full_name or user.username})")
        print("Subject: Your Order Confirmation")
        print("Thank you for your purchase! Your order details:")
        for car in cart.items.values():
            print(f"- {car.make} {car.model} (VIN: {car.vin})")
        _, total = cart.calculate_total()
        print(f"Total Paid: ${total:,.2f}")
        
        print("\nTo: Dealership Sales Team")
        print("Subject: New Sale Alert!")
        print(f"A new sale has been made to {user.full_name or user.username}.")
        print("-----------------------------")

class Delivery:
    @staticmethod
    def schedule():
        print("\n--- Scheduling Delivery ---")
        address = input("Enter delivery address: ")
        date = input("Enter desired delivery date (e.g., YYYY-MM-DD): ")
        print(f"Delivery for the purchased vehicle(s) scheduled for {date} to {address}.")
        print("---------------------------")
