import random
import string
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

def format_price(price):
    if price >= 1_000_000:
        return f"${price / 1_000_000:.1f}M"
    elif price >= 1_000:
        return f"${price / 1_000:.1f}K"
    else:
        return f"${price:.2f}"

class Car:
    def __init__(self, name, price, mileage, condition, age):
        self.name = name
        self.price = price
        self.mileage = mileage
        self.condition = condition
        self.age = age
        self.owners = 0
        self.maintenance_history = []

    def depreciate(self):
        depreciation_rate = 0.1 if self.condition == "New" else 0.2
        self.price = max(0, self.price - self.price * depreciation_rate)

    def maintain(self, year):
        maintenance_cost = (1000 * self.age) if self.condition == "New" else (2000 * self.age)
        self.maintenance_history.append({"year": year, "cost": maintenance_cost})
        return maintenance_cost

    def modify(self, upgrade_type):
        if upgrade_type == "performance":
            self.price += 10000
            print(f"{Fore.GREEN}Performance upgrade applied to {self.name}. New value: {format_price(self.price)}")
        elif upgrade_type == "luxury":
            self.price += 5000
            print(f"{Fore.GREEN}Luxury upgrade applied to {self.name}. New value: {format_price(self.price)}")
        elif upgrade_type == "efficiency":
            self.price += 2000
            print(f"{Fore.GREEN}Efficiency upgrade applied to {self.name}. New value: {format_price(self.price)}")
        else:
            print(Fore.RED + "Invalid upgrade type.")

class LuxuryCar(Car):
    def luxury_tax(self):
        self.price += 5000

class SportsCar(Car):
    def boost_performance(self):
        self.price += 10000

class EconomyCar(Car):
    def fuel_efficiency_bonus(self):
        self.price += 2000

class Customer:
    def __init__(self, name, budget, preference, negotiation_skill):
        self.name = name
        self.budget = budget
        self.preference = preference
        self.negotiation_skill = negotiation_skill

    def negotiate_price(self, car_price):
        discount = random.randint(0, int(car_price * (self.negotiation_skill / 10)))
        final_price = car_price - discount
        return final_price

class AICompetitor:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.owned_cars = {}

    def buy_car(self, car):
        negotiation = random.randint(-5000, 5000)
        final_price = max(0, car.price + negotiation)
        if self.money >= final_price:
            self.owned_cars[car.name] = car
            self.money -= final_price
            car.owners += 1
            print(f"{Fore.MAGENTA}{self.name} bought {car.name} for {format_price(final_price)}.")
        else:
            print(f"{Fore.RED}{self.name} couldn't afford {car.name}.")

    def sell_car(self, car):
        sell_price = car.price
        if car.name in self.owned_cars:
            del self.owned_cars[car.name]
            self.money += sell_price
            print(f"{Fore.MAGENTA}{self.name} sold {car.name} for {format_price(sell_price)}.")

class Employee:
    def __init__(self, name, role, skill_level):
        self.name = name
        self.role = role  # e.g., "Salesperson", "Mechanic"
        self.skill_level = skill_level  # Ranges from 1 to 10

    def improve_skill(self):
        if self.skill_level < 10:
            self.skill_level += 1
            print(f"{self.name} has improved their {self.role} skills to level {self.skill_level}.")
        else:
            print(f"{self.name} has already reached maximum skill level.")

class CarDealershipSimulator:
    def __init__(self):
        self.money = 1_000_000
        self.current_year = 2023
        self.owned = {}
        self.price_history = {}
        self.income_history = []
        self.expense_history = []
        self.ai_competitors = [AICompetitor("Competitor A", 800_000), AICompetitor("Competitor B", 1_200_000)]
        self.customers = [Customer("John Doe", 150_000, "Luxury", 8), Customer("Jane Smith", 50_000, "Economy", 5)]
        self.employees = [Employee("Alice", "Salesperson", 5), Employee("Bob", "Mechanic", 7)]

        self.luxury_cars = {
            "Rolls Royce": LuxuryCar("Rolls Royce", 500_000, 10, "New", 0),
            "Maybach": LuxuryCar("Maybach", 200_000, 15, "New", 0),
            "Bmw Alphina": LuxuryCar("Bmw Alphina", 150_000, 20, "New", 0),
            "Bentley": LuxuryCar("Bentley", 250_000, 8, "New", 0),
            "Aston Martin": LuxuryCar("Aston Martin", 180_000, 12, "New", 0),
        }
        self.sports_cars = {
            "Mclaren": SportsCar("Mclaren", 400_000, 5, "New", 0),
            "Lamborghini": SportsCar("Lamborghini", 300_000, 8, "New", 0),
            "Porsche": SportsCar("Porsche", 150_000, 18, "New", 0),
            "Ferrari": SportsCar("Ferrari", 350_000, 6, "New", 0),
            "Bugatti": SportsCar("Bugatti", 700_000, 4, "New", 0),
        }
        self.economy_cars = {
            "Alfa Romeo": EconomyCar("Alfa Romeo", 50_000, 25, "Used", 3),
            "Ford": EconomyCar("Ford", 40_000, 30, "Used", 5),
            "Toyota": EconomyCar("Toyota", 50_000, 35, "Used", 4),
            "Mini Cooper": EconomyCar("Mini Cooper", 60_000, 28, "Used", 6),
            "Honda": EconomyCar("Honda", 30_000, 40, "Used", 5),
            "Nissan": EconomyCar("Nissan", 35_000, 38, "Used", 4),
        }

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        while True:
            self.clear_console()
            print(Fore.CYAN + Style.BRIGHT + "Welcome to the Advanced Car Dealership Simulator!")
            print(Fore.GREEN + "\nMain Menu:")
            print(Fore.YELLOW + "1. View available cars")
            print("2. Buy a car")
            print("3. View your owned cars")
            print("4. Sell a car")
            print("5. Add your own car")
            print("6. Modify a car")
            print("7. Auction a car")
            print("8. Simulate next year")
            print("9. Manage Employees")
            print("10. Save game")
            print("11. Load game")
            print("12. View user guide")
            print("13. Exit")
            choice = input(Fore.MAGENTA + "Enter your choice: ")
            if choice == '1':
                self.view_available_cars()
            elif choice == '2':
                self.buy_car_menu()
            elif choice == '3':
                self.view_owned_cars()
            elif choice == '4':
                self.sell_car()
            elif choice == '5':
                self.add_user_car()
            elif choice == '6':
                self.modify_car()
            elif choice == '7':
                self.auction_car()
            elif choice == '8':
                self.simulate()
            elif choice == '9':
                self.manage_employees()
            elif choice == '10':
                self.save_game()
            elif choice == '11':
                self.load_game()
            elif choice == '12':
                self.view_user_guide()
            elif choice == '13':
                print(Fore.CYAN + "Exiting the game. Goodbye!")
                break
            else:
                print(Fore.RED + "Invalid choice. Please try again.")

    def view_available_cars(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Available Cars:")
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                print(f"{Fore.YELLOW}{car.name}: {format_price(car.price)} | Mileage: {car.mileage}k miles | Condition: {car.condition} | Age: {car.age} years")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def buy_car_menu(self):
        while True:
            self.clear_console()
            print(Fore.GREEN + "\nBuy a Car Menu:")
            print(Fore.YELLOW + "1. View Luxury Cars")
            print("2. View Sports Cars")
            print("3. View Economy Cars")
            print("4. Return to Main Menu")
            choice = input(Fore.MAGENTA + "Enter your choice: ")
            if choice == '1':
                self.buy_car("Luxury", self.luxury_cars)
            elif choice == '2':
                self.buy_car("Sports", self.sports_cars)
            elif choice == '3':
                self.buy_car("Economy", self.economy_cars)
            elif choice == '4':
                break
            else:
                print(Fore.RED + "Invalid choice. Please try again.")

    def buy_car(self, category, car_list):
        self.clear_console()
        print(Fore.GREEN + f"\n{category} Cars:")
        for car in car_list.values():
            print(f"{Fore.YELLOW}{car.name}: {format_price(car.price)} | Mileage: {car.mileage}k miles | Condition: {car.condition} | Age: {car.age} years")
        carname = string.capwords(input(Fore.MAGENTA + "\nWhich car would you like to buy? (or type 'back' to return): "))
        if carname.lower() == 'back':
            return
        if carname in car_list:
            car = car_list[carname]
            print(f"{Fore.YELLOW}{car.name}: {format_price(car.price)} | Mileage: {car.mileage}k miles | Condition: {car.condition} | Age: {car.age} years")
            buythiscar = input(Fore.MAGENTA + "Do you want to buy this car? (yes or no): ").lower()
            if buythiscar == "yes":
                negotiation = random.randint(-5000, 5000)
                final_price = max(0, car.price + negotiation)
                if self.money - final_price >= 0:
                    if carname in self.owned:
                        print(Fore.RED + "You already own this car.")
                    else:
                        self.owned[carname] = car
                        self.money -= final_price
                        car.owners += 1
                        self.expense_history.append({"type": "purchase", "amount": final_price, "car": carname, "year": self.current_year})
                        print(f"{Fore.GREEN}You bought a {carname} for {format_price(final_price)}.")
                else:
                    print(Fore.RED + "You don't have enough money.")
            else:
                print(Fore.CYAN + "Purchase cancelled.")
        else:
            print(Fore.RED + "Invalid car model.")
        input(Fore.CYAN + "\nPress Enter to return to the previous menu...")

    def view_owned_cars(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Your Owned Cars:")
        for carname, car in self.owned.items():
            print(f"{Fore.YELLOW}{carname}: 1 car")
            print(f"    Age: {car.age} years | Mileage: {car.mileage}k miles | Condition: {car.condition}")
            print(f"    Owners: {car.owners} | Maintenance: {car.maintenance_history}")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def sell_car(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Sell a Car:")
        carname = string.capwords(input(Fore.MAGENTA + "\nWhich car would you like to sell? --> "))
        if carname in self.owned:
            car = self.owned[carname]
            sellprice = car.price
            self.money += sellprice
            del self.owned[carname]
            self.income_history.append({"type": "sale", "amount": sellprice, "car": carname, "year": self.current_year})
            print(f"{Fore.GREEN}You sold your {carname} for {format_price(sellprice)}.")
        else:
            print(Fore.RED + "You do not own this car.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def add_user_car(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Add Your Own Car:")
        carname = string.capwords(input(Fore.MAGENTA + "\nEnter the name of the car: "))
        try:
            carprice = int(input(Fore.MAGENTA + "Enter the value of the car: $"))
            carmileage = int(input(Fore.MAGENTA + "Enter the mileage of the car: "))
            carcondition = input(Fore.MAGENTA + "Enter the condition of the car (New/Used): ").capitalize()
            carage = int(input(Fore.MAGENTA + "Enter the age of the car (years): "))
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter valid numbers.")
            input(Fore.CYAN + "\nPress Enter to return to the main menu...")
            return

        if carcondition not in ["New", "Used"]:
            print(Fore.RED + "Invalid condition. Please enter 'New' or 'Used'.")
            input(Fore.CYAN + "\nPress Enter to return to the main menu...")
            return

        # Decide which category the car belongs to based on price and add to the appropriate list
        if carprice >= 200_000:
            car = LuxuryCar(carname, carprice, carmileage, carcondition, carage)
            self.luxury_cars[carname] = car
        elif carprice >= 100_000:
            car = SportsCar(carname, carprice, carmileage, carcondition, carage)
            self.sports_cars[carname] = car
        else:
            car = EconomyCar(carname, carprice, carmileage, carcondition, carage)
            self.economy_cars[carname] = car

        print(Fore.GREEN + f"Your car {carname} has been added successfully.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def modify_car(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Modify a Car:")
        carname = string.capwords(input(Fore.MAGENTA + "\nWhich car would you like to modify? --> "))
        if carname in self.owned:
            car = self.owned[carname]
            print(f"{Fore.YELLOW}{carname}: 1 car | Value: {format_price(car.price)}")
            print("Available Modifications: ")
            print("1. Performance Upgrade (+$10,000)")
            print("2. Luxury Upgrade (+$5,000)")
            print("3. Efficiency Upgrade (+$2,000)")
            upgrade_choice = input(Fore.MAGENTA + "Choose an upgrade (1-3): ")
            if upgrade_choice == '1':
                car.modify("performance")
            elif upgrade_choice == '2':
                car.modify("luxury")
            elif upgrade_choice == '3':
                car.modify("efficiency")
            else:
                print(Fore.RED + "Invalid choice.")
        else:
            print(Fore.RED + "You do not own this car.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def auction_car(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Auction a Car:")
        carname = string.capwords(input(Fore.MAGENTA + "\nWhich car would you like to auction? --> "))
        if carname in self.owned:
            car = self.owned[carname]
            base_price = car.price
            auction_price = base_price + random.randint(0, base_price // 2)
            competitors = random.sample(self.ai_competitors, k=random.randint(1, len(self.ai_competitors)))
            for comp in competitors:
                comp.bid_price = random.randint(base_price, auction_price + 50000)
                print(f"{Fore.MAGENTA}{comp.name} bids {format_price(comp.bid_price)} for {carname}.")
            player_bid = input(Fore.MAGENTA + f"Do you want to place a bid higher than {format_price(auction_price)}? (yes/no): ").lower()
            if player_bid == 'yes':
                player_bid_price = int(input(Fore.MAGENTA + "Enter your bid amount: $"))
                if player_bid_price > auction_price:
                    auction_price = player_bid_price
                    print(Fore.GREEN + f"You win the auction for {carname} with a bid of {format_price(auction_price)}.")
                else:
                    print(Fore.RED + f"Your bid was too low. {competitors[0].name} wins the auction.")
                    self.owned.pop(carname)
            else:
                print(Fore.RED + f"{competitors[0].name} wins the auction for {format_price(auction_price)}.")
                self.owned.pop(carname)
            self.money += auction_price
        else:
            print(Fore.RED + "You do not own this car.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def simulate(self):
        self.clear_console()
        print(Fore.CYAN + Style.BRIGHT + "\nSimulating Car Prices for the next year...")
        self.current_year += 1
        self.random_event()
        maintenance_costs = self.calculate_maintenance_costs()
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                car.depreciate()
                self.price_history.setdefault(car.name, []).append(car.price)
                car.age += 1  # Increase the age of each car by 1 year
        print(Fore.GREEN + "\nNew Car Prices:")
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                print(f"{Fore.YELLOW}{car.name}: {format_price(car.price)}")
        print(Fore.CYAN + "\nYour owned cars:")
        for carname, car in self.owned.items():
            print(f"{Fore.YELLOW}{carname}: 1 car")

        # AI competitors also participate in the market
        for competitor in self.ai_competitors:
            self.ai_turn(competitor)

        self.yearly_report(maintenance_costs)
        self.calculate_profit(maintenance_costs)
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def calculate_maintenance_costs(self):
        total_cost = 0
        for carname, car in self.owned.items():
            maintenance_cost = car.maintain(self.current_year)
            total_cost += maintenance_cost
            self.expense_history.append({"type": "maintenance", "amount": maintenance_cost, "car": carname, "year": self.current_year})
        return total_cost

    def calculate_profit(self, maintenance_costs):
        profit = sum(car.price for car in self.owned.values())
        total_assets = self.money + profit
        print(f"\n{Fore.GREEN}Total value of your assets: {format_price(total_assets)}")
        print(f"{Fore.GREEN}Profit from car sales: {format_price(profit - sum(car.price for car in self.owned.values()) - maintenance_costs)}")

    def random_event(self):
        events = [
            {"event": "economic boom", "description": "An economic boom increases car values significantly.", "impact": lambda value: value + random.randint(10000, 50000)},
            {"event": "recession", "description": "A recession decreases car values significantly.", "impact": lambda value: value - random.randint(10000, 50000)},
            {"event": "new tax law", "description": "A new tax law negatively affects car values.", "impact": lambda value: value - random.randint(5000, 25000)},
            {"event": "high demand", "description": "High demand increases car values moderately.", "impact": lambda value: value + random.randint(5000, 30000)},
            {"event": "low demand", "description": "Low demand decreases car values moderately.", "impact": lambda value: value - random.randint(5000, 30000)},
            {"event": "new technology", "description": "New technology boosts car values.", "impact": lambda value: value + random.randint(5000, 20000)},
            {"event": "market saturation", "description": "Market saturation decreases car values.", "impact": lambda value: value - random.randint(10000, 40000)},
            {"event": "natural disaster", "description": "A natural disaster significantly lowers car values.", "impact": lambda value: value - random.randint(20000, 60000)}
        ]
        event = random.choice(events)
        print(f"{Fore.MAGENTA}Random event this year: {Fore.YELLOW}{event['event']}")
        print(f"{Fore.YELLOW}{event['description']}")
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                car.price = max(0, event["impact"](car.price))

    def ai_turn(self, competitor):
        if random.choice([True, False]):
            available_cars = random.choice([self.luxury_cars, self.sports_cars, self.economy_cars])
            car = random.choice(list(available_cars.values()))
            competitor.buy_car(car)
        else:
            if competitor.owned_cars:
                car = random.choice(list(competitor.owned_cars.values()))
                competitor.sell_car(car)

    def manage_employees(self):
        self.clear_console()
        print(Fore.GREEN + Style.BRIGHT + "Manage Employees:")
        for i, employee in enumerate(self.employees, start=1):
            print(f"{Fore.YELLOW}{i}. {employee.name} ({employee.role}) - Skill Level: {employee.skill_level}")
        choice = input(Fore.MAGENTA + "Select an employee to improve their skills (or type 'back' to return): ")
        if choice.lower() == 'back':
            return
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(self.employees):
                self.employees[choice].improve_skill()
            else:
                print(Fore.RED + "Invalid selection.")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        input(Fore.CYAN + "\nPress Enter to return to the previous menu...")

    def yearly_report(self, maintenance_costs):
        print(Fore.CYAN + "\nYearly Report:")
        print(f"{Fore.YELLOW}Year: {self.current_year}")
        print(f"{Fore.YELLOW}Money: {format_price(self.money)}")
        print(f"{Fore.YELLOW}Owned Cars: {list(self.owned.keys())}")
        print(Fore.GREEN + "\nPrice History:")
        for model, history in self.price_history.items():
            print(f"{Fore.YELLOW}{model}: {', '.join(map(format_price, history))}")
        print(Fore.GREEN + "\nIncome History:")
        for entry in self.income_history:
            print(f"{Fore.YELLOW}{entry}")
        print(Fore.GREEN + "\nExpense History:")
        for entry in self.expense_history:
            print(f"{Fore.YELLOW}{entry}")
        print(Fore.GREEN + f"\nTotal Maintenance Costs: {format_price(maintenance_costs)}")

    def save_game(self):
        slot = input(Fore.MAGENTA + "Enter save slot number (1-3): ")
        if slot not in ['1', '2', '3']:
            print(Fore.RED + "Invalid slot number. Please choose between 1 and 3.")
            return
        game_state = {
            "money": self.money,
            "owned": {name: car.__dict__ for name, car in self.owned.items()},
            "current_year": self.current_year,
            "price_history": self.price_history,
            "income_history": self.income_history,
            "expense_history": self.expense_history,
            "ai_competitors": {comp.name: comp.__dict__ for comp in self.ai_competitors},
            "employees": [emp.__dict__ for emp in self.employees]
        }
        with open(f"car_dealership_save_{slot}.json", "w") as save_file:
            json.dump(game_state, save_file)
        print(Fore.GREEN + "Game saved successfully.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def load_game(self):
        slot = input(Fore.MAGENTA + "Enter load slot number (1-3): ")
        if slot not in ['1', '2', '3']:
            print(Fore.RED + "Invalid slot number. Please choose between 1 and 3.")
            return
        if os.path.exists(f"car_dealership_save_{slot}.json"):
            with open(f"car_dealership_save_{slot}.json", "r") as save_file:
                game_state = json.load(save_file)
            self.money = game_state["money"]
            self.current_year = game_state["current_year"]
            self.price_history = game_state["price_history"]
            self.income_history = game_state["income_history"]
            self.expense_history = game_state["expense_history"]
            self.owned = {name: Car(**car) for name, car in game_state["owned"].items()}
            self.ai_competitors = [AICompetitor(name, data['money']) for name, data in game_state["ai_competitors"].items()]
            self.employees = [Employee(**emp) for emp in game_state["employees"]]
            print(Fore.GREEN + "Game loaded successfully.")
        else:
            print(Fore.RED + "No saved game found in this slot. Starting a new game.")
        input(Fore.CYAN + "\nPress Enter to return to the main menu...")

    def view_user_guide(self):
        while True:
            self.clear_console()
            print(Fore.GREEN + Style.BRIGHT + "User Guide:")
            print(Fore.YELLOW + "1. View available cars: Displays the list of cars available for purchase with their details.")
            print("2. Buy a car: Allows you to purchase a car if you have enough money.")
            print("3. View your owned cars: Shows the cars you currently own along with their details.")
            print("4. Sell a car: Enables you to sell one of your owned cars.")
            print("5. Add your own car: Allows you to add a car of your own to the dealership.")
            print("6. Modify a car: Lets you apply upgrades to your cars, increasing their value.")
            print("7. Auction a car: Puts a car up for auction, allowing AI competitors to bid against you.")
            print("8. Simulate next year: Advances the game by one year, applying random events and updating car prices.")
            print("9. Manage Employees: Train and manage your employees to improve their skills and boost dealership performance.")
            print("10. Save game: Saves your current game state in one of three slots.")
            print("11. Load game: Loads a previously saved game from one of three slots.")
            print("12. Exit: Exits the game.")
            print("\n0. Return to Main Menu")
            choice = input(Fore.MAGENTA + "\nEnter your choice: ")
            if choice == '0':
                break
            else:
                print(Fore.RED + "Invalid choice. Please try again.")
                input(Fore.CYAN + "\nPress Enter to return to the user guide...")

if __name__ == "__main__":
    game = CarDealershipSimulator()
    game.main_menu()
