# main.py
''' The main module serves as the entry point for the car dealership, e-commerce simulation for a terminal-based car dealership system.
 It integrates user authentication, inventory management, shopping cart functionality, payment processing, and reporting.
 Intended for simple terminal interaction without a graphical user interface.
 Key principles followed are ensuring readability, writability, and maintainability from our Computational Thinking course at SAIT.
 000563621
'''
from car import Car, VINExistsError, PermissionError
from inventory import Inventory
from auth import User, UserManager
from ecommerce import Cart, Payment, Notification, Delivery
import sys

# ============================================================
# Helper Functions for Input Validation & UI
# ============================================================

def get_valid_year() -> int:
    while True:
        try:
            return int(input("Enter car year: "))
        except ValueError:
            print("Invalid input. Year must be a whole number.")

def get_valid_price(prompt: str) -> float:
    while True:
        try:
            price_str = input(prompt)
            return float(price_str.replace("$", "").replace(",", ""))
        except ValueError:
            print("Invalid input. Price must be a number.")

def get_valid_vin() -> str:
    while True:
        vin = input("Enter car VIN: ").strip().upper()
        if vin:
            return vin
        print("VIN cannot be empty.")

def print_header(title: str):
    print("\n" + "=" * 40)
    print(f" {title.upper()} ".center(40, "="))
    print("=" * 40)

def find_car_with_suggestion(inventory: Inventory, vin: str) -> Car | None:
    """
    Finds a car by VIN. Tries an exact match first, then falls back to a
    fuzzy search to provide a suggestion for typos.
    """
    vin = vin.strip().upper()
    # 1. Try exact match first for speed
    car = inventory.find_car(vin)
    if car:
        return car

    # 2. If not found, try fuzzy search
    print("Exact VIN not found. Searching for similar VINs...")
    suggested_car, distance = inventory.find_car_by_vin_fuzzy(vin)

    # 3. If a close match is found, suggest it to the user
    if suggested_car and distance <= 3: # Threshold of 3 seems reasonable
        print(f"Did you mean VIN '{suggested_car.vin}'?")
        print(f"Details: {suggested_car}")
        confirm = input("Is this the correct car? (y/n): ").strip().lower()
        if confirm == 'y':
            return suggested_car
    
    # 4. If no close match or user denies, return None
    return None

# ============================================================
# Main Application Logic Functions
# ============================================================

def handle_buyer_actions(current_user: User, inventory: Inventory):
    cart = Cart(current_user)
    while True:
        print_header("Buyer Menu")
        print("1. Browse and Filter Cars")
        print("2. View and Manage Cart")
        print("3. Checkout")
        print("4. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            handle_browsing(inventory, cart)
        elif choice == '2':
            handle_cart_management(cart)
        elif choice == '3':
            if not cart.items:
                print("Your cart is empty. Add items before checking out.")
                continue
            
            payment_successful = handle_checkout(current_user, cart, inventory)
            if payment_successful:
                cart = Cart(current_user) # Reset cart ONLY on successful purchase
        elif choice == '4':
            break
        else:
            print("Invalid option.")

def handle_browsing(inventory: Inventory, cart: Cart):
    while True:
        print_header("Browse Cars")
        print(inventory.list_inventory())
        print("\nFilter & Action:")
        print("1. Filter by Make and Model")
        print("2. Filter by Price Range")
        print("3. Add a Car to Cart")
        print("4. Back to Buyer Menu")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            make = input("Enter make: ").strip()
            model = input("Enter model: ").strip()
            results = inventory.find_car_by_make_and_model(make, model)
            print("\n--- Filter Results ---")
            if results:
                for car in results: print(car)
            else:
                print("No cars found matching that make and model.")
            # Change made here so not the whole menu gets displayed
            input("\nPress Enter to go back to Filter & Action menu...")  

        elif choice == '2':
            min_p = get_valid_price("Enter minimum price: ")
            max_p = get_valid_price("Enter maximum price: ")
            try:
                results = inventory.filter_by_price_range(min_p, max_p)
                print("\n--- Filter Results ---")
                if results:
                    for car in results: print(car)
                else:
                    print("No cars found in that price range.")
                # Change made here so not the whole menu gets displayed
                input("\nPress Enter to go back to Filter & Action menu...")

            except ValueError as e:
                print(f"Error: {e}")
        elif choice == '3':
            vin = get_valid_vin()
            car = find_car_with_suggestion(inventory, vin)
            if car:
                cart.add_item(car)
            else:
                print("Car with that VIN not found.")
            # Change made here so not the whole menu gets displayed
            input("\nPress Enter to go back to Filter & Action menu...")

        elif choice == '4':
            break
        else:
            print("Invalid option.")

def handle_cart_management(cart: Cart):
    while True:
        cart.display()
        print("\nCart Actions:")
        print("1. Remove a Car from Cart")
        print("2. Apply Discount Code")
        print("3. Back to Buyer Menu")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            vin = get_valid_vin()
            cart.remove_item(vin)
        elif choice == '2':
            code = input("Enter discount code: ").strip()
            cart.apply_discount(code)
        elif choice == '3':
            break
        else:
            print("Invalid option.")

def handle_checkout(user: User, cart: Cart, inventory: Inventory) -> bool:
    print_header("Checkout")
    cart.display()
    _, total = cart.calculate_total()
    
    confirm = input("Proceed to payment? (y/n): ").lower()
    if confirm != 'y':
        print("Checkout cancelled.")
        return False

    payment = Payment()
    if payment.process(total):
        # Mark all items in cart as sold
        for car in cart.items.values():
            car.sell()
        
        Notification.send_order_confirmation(user, cart)
        Delivery.schedule()
        print("\nThank you for your purchase!")


        input("\nPress Enter to return to the Main Menu...")

        return True
    else:
        print("Could not complete purchase due to payment failure.")
        return False

def handle_seller_admin_actions(current_user: User, inventory: Inventory, user_manager: UserManager):
    is_admin = current_user.role_type == "Admin"
    while True:
        print_header(f"{current_user.role_type} Menu")
        print("1. List All Cars (including sold)")
        print("2. Update Car Price")
        print("3. Update Car Status (e.g., Reserve)")
        if is_admin:
            print("4. Add New Car")
            print("5. Edit Existing Car")
            print("6. Permanently Remove Sold Car Record")
            print("7. User Management")
            print("8. Generate Reports")
        print("0. Back to Main Menu")
        
        choice = input("Choose an option: ").strip()

        if choice == '1':
            print_header("Full Inventory Listing")
            print(inventory.list_inventory(include_sold=True))
        elif choice == '2':
            vin = get_valid_vin()
            car = find_car_with_suggestion(inventory, vin)
            if car:
                try:
                    new_price = get_valid_price(f"Enter new price for {vin} (current: ${car.price:,.2f}): ")
                    car.update_price(new_price, admin=is_admin)
                    print("Price updated successfully.")
                except (ValueError, PermissionError) as e:
                    print(f"Error: {e}")
            else:
                print("Car not found.")
        elif choice == '3':
            vin = get_valid_vin()
            car = find_car_with_suggestion(inventory, vin)
            if car:
                try:
                    status_in = input("Enter new status (Available, Reserved, Sold): ").strip().title()
                    if status_in in ["Available", "Reserved", "Sold"]:
                        car.update_status(status_in, admin=is_admin) # type: ignore
                        print("Status updated successfully.")
                    else:
                        print("Invalid status entered.")
                except (ValueError, PermissionError) as e:
                    print(f"Error: {e}")
            else:
                print("Car not found.")
        elif choice == '4' and is_admin:
            try:
                print_header("Add New Car")
                vin = get_valid_vin()
                year = get_valid_year()
                make = input("Enter car make: ").strip()
                model = input("Enter car model: ").strip()
                colour = input("Enter car colour: ").strip()
                cost = get_valid_price("Enter dealership cost: ")
                price = get_valid_price("Enter selling price: ")
                new_car = Car(vin=vin, year=year, make=make, model=model, colour=colour, cost=cost, price=price)
                inventory.add_car(new_car)
                print(f"\nSuccessfully added new car: {new_car.make} {new_car.model}")
            except (ValueError, VINExistsError) as e:
                print(f"Error adding car: {e}")
        elif choice == '5' and is_admin:
            handle_edit_car(inventory)
        elif choice == '6' and is_admin:
            vin = get_valid_vin()
            print(inventory.remove_car(vin))
        elif choice == '7' and is_admin:
            handle_user_management(user_manager)
        elif choice == '8' and is_admin:
            handle_reports(inventory)
        elif choice == '0':
            break
        else:
            print("Invalid option or insufficient permissions.")

def handle_edit_car(inventory: Inventory):
    print_header("Edit Car (Admin)")
    vin = get_valid_vin()
    car = find_car_with_suggestion(inventory, vin)
    if not car:
        print("Car not found.")
        return

    print(f"Editing: {car}")
    print("Leave blank to keep current value.")
    
    try:
        # For simplicity, this example updates a few fields. Can be expanded.
        new_make = input(f"Make [{car.make}]: ").strip()
        if new_make: car.update_make(new_make, admin=True)

        new_model = input(f"Model [{car.model}]: ").strip()
        if new_model: car.update_model(new_model, admin=True)
        
        print("Car details updated successfully.")
    except (ValueError, PermissionError) as e:
        print(f"Error updating car: {e}")

def handle_user_management(user_manager: UserManager):
    print_header("User Management (Admin)")
    while True:
        print("\n1. List All Users")
        print("2. Change User Role")
        print("3. Create New User")
        print("0. Back to Admin Menu")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            print_header("All Users")
            for u in user_manager.list_users():
                print(f"- Username: {u.username}, Role: {u.role_type}")
        elif choice == '2':
            username = input("Enter username to modify: ").strip().lower()
            new_role = input("Enter new role (Admin, Seller, Buyer): ").strip().title()
            user_manager.update_user_role(username, new_role)
        elif choice == '3':
            print_header("Create New User")
            username = input("Enter new username: ").strip().lower()
            password = input(f"Enter password for {username}: ").strip()
            role = input("Enter role (Admin, Seller, Buyer): ").strip().title()
            user_manager.create_user(username, password, role)
        elif choice == '0':
            break
        else:
            print("Invalid option.")

def handle_reports(inventory: Inventory):
    print_header("Generate Reports (Admin)")
    sold_cars = [car for car in inventory.cars.values() if car.status == "Sold"]
    
    if not sold_cars:
        print("No sales data available to generate reports.")
        return

    total_revenue = sum(car.price for car in sold_cars)
    total_cost = sum(car.cost for car in sold_cars)
    total_profit = total_revenue - total_cost

    print("\n--- Sales and Profit Report ---")
    print(f"Total Cars Sold: {len(sold_cars)}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Cost of Goods Sold: ${total_cost:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    print("---------------------------------")

# ============================================================
# Main Program Execution
# ============================================================

def main():
    """Main function to run the car dealership simulation."""
    print_header("E-Commerce Car Dealership Simulation")

    # Setup Users and Inventory
    user_manager = UserManager()
    user_manager.populate_default_users()

    inventory = Inventory()
    try:
        inventory.add_car(Car(vin="VIN123", year=2021, make="Honda", model="Civic", colour="Blue", cost=20000, price=22000.0))
        inventory.add_car(Car(vin="VIN456", year=2022, make="Ford", model="Mustang", colour="Red", cost=40000, price=45000.0))
        inventory.add_car(Car("VIN101", 2022, "Toyota", "Camry", "Silver", 25000, 28000))
    except (ValueError, VINExistsError) as e:
        print(f"Error pre-populating data: {e}")

    current_user: User | None = None
    login_attempts = 0
    MAX_LOGIN_ATTEMPTS = 3

    while True:
        print_header("Main Menu")
        if current_user:
            print(f"Logged in as: {current_user.username} ({current_user.role_type})")
            print("1. Enter Buyer Portal")
            if current_user.role_type in ["Admin", "Seller"]:
                print("2. Enter Staff Portal (Admin/Seller)")
            print("3. Logout")
        else:
            if login_attempts < MAX_LOGIN_ATTEMPTS:
                print("1. Login")
            else:
                print("1. Login (Locked due to too many failed attempts)")
            print("2. Browse Inventory (Public)")
        print("0. Exit Program")

        choice = input("Choose an option: ").strip()

        if current_user:
            if choice == '1':
                handle_buyer_actions(current_user, inventory)
            elif choice == '2' and current_user.role_type in ["Admin", "Seller"]:
                handle_seller_admin_actions(current_user, inventory, user_manager)
            elif choice == '3':
                print(f"Logging out {current_user.username}.")
                current_user = None
                login_attempts = 0 # Reset attempts on logout
            elif choice == '0':
                break
            else:
                print("Invalid option.")
        else: # Not logged in
            if choice == '1':
                if login_attempts >= MAX_LOGIN_ATTEMPTS:
                    print("You have been temporarily locked out.")
                    continue
                
                name = input("Enter username: ").strip().lower()
                user = user_manager.get_user(name)
                if user and user.login():
                    current_user = user
                    login_attempts = 0 # Reset on success
                else:
                    login_attempts += 1
                    remaining = MAX_LOGIN_ATTEMPTS - login_attempts
                    print(f"Login failed. You have {remaining} attempts remaining.")
            elif choice == '2':
                print_header("Public Inventory")
                print(inventory.list_inventory())
            elif choice == '0':
                break
            else:
                print("Invalid option.")

    print("\nExiting program. Goodbye!")

if __name__ == "__main__":
    main()