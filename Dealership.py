import random
import string
import json
import os
import sqlite3
from datetime import datetime
import time
from colorama import init
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress
from rich.text import Text
from rich import box

# Initialize colorama and console
init(autoreset=True)
console = Console()

def format_price(price):
    if price >= 1_000_000:
        return f"${price / 1_000_000:.1f}M"
    elif price >= 1_000:
        return f"${price / 1_000:.1f}K"
    else:
        return f"${price:.2f}"

def typing_effect(text, delay=0.05):
    """Simulates a typing effect for the given text."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def loading_animation(text, duration=2):
    """Displays a loading animation for a specified duration."""
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{text}", total=100)
        for _ in range(100):
            time.sleep(duration / 100)
            progress.advance(task)

# -------------------- Classes --------------------

# Base Car Class
class Car:
    def __init__(self, name, price, mileage, condition, age, **kwargs):
        self.name = name
        self.price = price
        self.base_price = price  # Original price for calculations
        self.mileage = mileage
        self.condition = condition
        self.age = age
        self.owners = 0
        self.maintenance_history = []
        self.customizations = []
        self.sold = False
        # Accept extra keys from saved game state
        self.__dict__.update(kwargs)

    def depreciate(self):
        # Depreciation logic based on car condition and age
        depreciation_rate = 0.05 + (0.02 * self.age)
        if self.condition == "Used":
            depreciation_rate += 0.05
        self.price = max(500, self.price * (1 - depreciation_rate))
        self.price = round(self.price, 2)

    def maintain(self, year):
        # Maintenance cost increases with age
        maintenance_cost = (500 * self.age) if self.condition == "New" else (1000 * self.age)
        self.maintenance_history.append({"year": year, "cost": maintenance_cost})
        return maintenance_cost

    def modify(self, upgrade_type):
        upgrades = {"performance": 10000, "luxury": 5000, "efficiency": 2000}
        if upgrade_type in upgrades:
            self.price += upgrades[upgrade_type]
            self.customizations.append(upgrade_type)
            console.print(f"[green]{upgrade_type.capitalize()} upgrade applied to {self.name}. New value: {format_price(self.price)}")
        else:
            console.print("[red]Invalid upgrade type.")

    def list_customizations(self):
        return ', '.join(self.customizations) if self.customizations else "None"

    def display_info(self):
        info = (
            f"Name: {self.name}\n"
            f"Price: {format_price(self.price)}\n"
            f"Mileage: {self.mileage}k miles\n"
            f"Condition: {self.condition}\n"
            f"Age: {self.age} years\n"
            f"Owners: {self.owners}\n"
            f"Customizations: {self.list_customizations()}\n"
        )
        return info

# Subclasses for different car types
class LuxuryCar(Car):
    def luxury_tax(self):
        self.price += 5000

class SportsCar(Car):
    def boost_performance(self):
        self.price += 10000

class EconomyCar(Car):
    def fuel_efficiency_bonus(self):
        self.price += 2000

# Inventory Management
class Inventory:
    def __init__(self):
        self.locations = {"Showroom": [], "Warehouse": []}
        self.low_stock_threshold = 5

    def add_car(self, location, car):
        if location in self.locations:
            self.locations[location].append(car)
            console.print(f"[green]Added {car.name} to {location}.")
        else:
            console.print("[red]Invalid location!")

    def move_car(self, from_location, to_location, car_name):
        if from_location in self.locations and to_location in self.locations:
            car = next((c for c in self.locations[from_location] if c.name == car_name), None)
            if car:
                # Move the car and remove from original location
                self.locations[to_location].append(car)
                self.locations[from_location].remove(car)
                console.print(f"[green]Moved {car.name} from {from_location} to {to_location}.")
            else:
                console.print(f"[red]{car_name} not found in {from_location}.")
        else:
            console.print("[red]Invalid location!")

    def check_inventory(self):
        for location, cars in self.locations.items():
            console.print(f"[bold yellow]{location}:")
            for car in cars:
                # Display each car
                console.print(f" - {car.name}")
            if len(cars) < self.low_stock_threshold:
                console.print(f"[red]Low stock alert at {location}!")

# Customer Class with Trade-In Feature
class Customer:
    def __init__(self, name, budget, preference, negotiation_skill, loyalty=1, trade_in_car=None):
        self.name = name
        self.budget = budget
        self.preference = preference
        self.negotiation_skill = negotiation_skill
        self.loyalty = loyalty
        self.purchase_history = []
        self.reviews = []
        self.trade_in_car = trade_in_car

    def negotiate_price(self, car_price):
        discount = random.randint(0, int(car_price * (self.negotiation_skill / 100)))
        final_price = car_price - discount
        if self.trade_in_car:
            final_price -= self.trade_in_car.price * 0.8  # Trade-in value is 80% of the car's current price
        return max(0, final_price)

    def provide_feedback(self, satisfaction_level):
        self.loyalty = min(5, max(1, self.loyalty + (satisfaction_level - 3)))
        console.print(f"[yellow]{self.name} gave a satisfaction rating of {satisfaction_level}. Loyalty is now {self.loyalty}.")

    def leave_review(self, car):
        review_text = Prompt.ask(f"[yellow]{self.name}, please leave a review for {car.name}:")
        rating = Prompt.ask(f"[yellow]Rate your experience with {car.name} out of 5:", choices=["1", "2", "3", "4", "5"])
        self.reviews.append({"car": car.name, "review": review_text, "rating": int(rating)})
        console.print(f"[green]{self.name} left a review: {review_text} (Rating: {rating}/5)")

    def purchase_car(self, car):
        final_price = self.negotiate_price(car.price)
        if final_price <= self.budget:
            self.purchase_history.append({"car": car.name, "price": final_price, "date": datetime.now().strftime('%Y-%m-%d')})
            self.budget -= final_price
            console.print(f"[green]{self.name} purchased {car.name} for {format_price(final_price)}. Remaining budget: {format_price(self.budget)}")
            self.leave_review(car)
            car.sold = True
            car.owners += 1
            return True
        else:
            console.print(f"[red]{self.name} could not afford {car.name}.")
            return False

# Employee Class with Training Programs
class Employee:
    def __init__(self, name, role, skill_level, **kwargs):
        self.name = name
        self.role = role
        self.skill_level = skill_level
        self.morale = 5
        self.__dict__.update(kwargs)

    def improve_skill(self):
        self.skill_level += 1
        console.print(f"[green]{self.name}'s skill level has improved to {self.skill_level}!")

    def affect_morale(self, change):
        self.morale = max(1, min(10, self.morale + change))
        morale_status = "happy" if self.morale > 7 else "neutral" if self.morale > 4 else "unhappy"
        console.print(f"[yellow]{self.name} is now {morale_status} with morale level {self.morale}.")

# AI Competitor with Advanced Strategies
class AICompetitor:
    def __init__(self, name, money, strategy="Balanced", **kwargs):
        self.name = name
        self.money = money
        self.owned_cars = {}
        self.dealerships = 1
        self.strategy = strategy
        self.__dict__.update(kwargs)

    def expand_business(self):
        if self.money >= 500_000:
            self.money -= 500_000
            self.dealerships += 1
            console.print(f"[magenta]{self.name} has opened a new dealership! Total dealerships: {self.dealerships}")
        else:
            console.print(f"[red]{self.name} doesn't have enough money to open a new dealership.")

    def steal_customer(self, customers):
        if self.strategy == "Aggressive" and customers:
            target = random.choice(customers)
            if random.random() > 0.5:
                console.print(f"[magenta]{self.name} has stolen a customer: {target.name}!")
                customers.remove(target)
            else:
                console.print(f"[cyan]{self.name} tried to steal a customer but failed.")
        elif self.strategy == "Balanced":
            pass

    def sabotage(self, player_dealership):
        if self.strategy == "Aggressive" and random.random() > 0.5 and player_dealership.owned:
            affected_cars = random.sample(list(player_dealership.owned.values()), k=min(len(player_dealership.owned), 3))
            for car in affected_cars:
                car.price -= random.randint(5000, 20000)
                console.print(f"[red]{self.name} sabotaged {car.name}, reducing its value!")

    def buy_car(self, car):
        negotiation = random.randint(-5000, 5000)
        final_price = max(0, car.price + negotiation)
        if self.money >= final_price and not car.sold:
            self.owned_cars[car.name] = car
            self.money -= final_price
            car.owners += 1
            car.sold = True
            console.print(f"[magenta]{self.name} bought {car.name} for {format_price(final_price)}.")
        else:
            console.print(f"[red]{self.name} couldn't afford {car.name} or it's already sold.")

    def sell_car(self, car):
        sell_price = car.price
        if car.name in self.owned_cars:
            del self.owned_cars[car.name]
            self.money += sell_price
            console.print(f"[magenta]{self.name} sold {car.name} for {format_price(sell_price)}.")

# Financial Manager with Detailed Management
class FinancialManager:
    def __init__(self, game):
        self.game = game
        self.profit_loss_statement = []
        self.balance_sheet = {}
        self.cash_flow = 0
        self.loans = []
        self.investments = []
        self.crypto_portfolio = {}
        self.taxes_due = 0

    def record_transaction(self, transaction_type, amount, description):
        self.profit_loss_statement.append({
            "date": datetime.now().strftime('%Y-%m-%d'),
            "type": transaction_type,
            "amount": amount,
            "description": description
        })
        self.cash_flow += amount if transaction_type == "income" else -amount
        console.print(f"[green]Recorded {transaction_type} of {format_price(amount)}: {description}")

    def take_loan(self, amount, interest_rate, term_years):
        total_payment = amount * (1 + interest_rate / 100) ** term_years
        self.loans.append({
            "amount": amount,
            "interest_rate": interest_rate,
            "term_years": term_years,
            "total_payment": total_payment,
            "outstanding": total_payment
        })
        self.game.money += amount  # Add loan amount to game money
        console.print(f"[green]Loan of {format_price(amount)} taken with {interest_rate}% interest over {term_years} years. Total repayment: {format_price(total_payment)}.")

    def calculate_taxes(self, profit):
        tax_rate = 0.3
        self.taxes_due = profit * tax_rate
        console.print(f"[yellow]Taxes calculated on profit: {format_price(self.taxes_due)}")

    def pay_taxes(self):
        if self.taxes_due > 0:
            if self.game.money >= self.taxes_due:
                self.game.money -= self.taxes_due
                console.print(f"[green]Taxes of {format_price(self.taxes_due)} paid.")
                self.taxes_due = 0
            else:
                console.print("[red]Not enough money to pay taxes.")
        else:
            console.print("[cyan]No taxes due.")

    def invest_in_stock(self, stock_name, amount):
        if amount <= self.game.money:
            self.game.money -= amount
            self.investments.append({"stock": stock_name, "amount": amount, "purchase_date": datetime.now().strftime('%Y-%m-%d')})
            console.print(f"[green]Invested {format_price(amount)} in {stock_name}.")
        else:
            console.print(f"[red]Not enough money to invest in {stock_name}.")

    def invest_in_crypto(self, crypto_name, amount):
        if amount <= self.game.money:
            self.game.money -= amount
            self.crypto_portfolio[crypto_name] = self.crypto_portfolio.get(crypto_name, 0) + amount
            console.print(f"[green]Invested {format_price(amount)} in {crypto_name} cryptocurrency.")
        else:
            console.print(f"[red]Not enough money to invest in {crypto_name}.")

    def pay_loan_installments(self):
        total_installment = 0
        for loan in self.loans[:]:
            installment = loan["total_payment"] / (loan["term_years"] * 12)
            loan["outstanding"] -= installment
            total_installment += installment
            if loan["outstanding"] <= 0:
                console.print(f"[green]Loan of {format_price(loan['amount'])} has been fully repaid.")
                self.loans.remove(loan)
        if total_installment > 0:
            if self.game.money >= total_installment:
                self.game.money -= total_installment
                console.print(f"[yellow]Paid loan installments totaling {format_price(total_installment)}.")
            else:
                console.print("[red]Not enough money to pay loan installments.")

# Auction House for Buying and Selling Cars
class AuctionHouse:
    def __init__(self, game):
        self.game = game
        self.auctions = []

    def list_car(self, car):
        starting_bid = car.price * 0.6
        self.auctions.append({"car": car, "highest_bid": starting_bid, "highest_bidder": None})
        console.print(f"[cyan]{car.name} has been listed in the auction house with a starting bid of {format_price(starting_bid)}.")

    def conduct_auction(self):
        for auction in self.auctions:
            car = auction["car"]
            current_bid = auction["highest_bid"]
            participants = self.game.ai_competitors + [self.game]
            for participant in participants:
                if participant == self.game:
                    bid_input = Prompt.ask(f"Do you want to bid on {car.name}? Current bid is {format_price(current_bid)}. Enter your bid or type 'pass'.", default='pass')
                    if bid_input.lower() != 'pass':
                        try:
                            bid = float(bid_input)
                            if bid > current_bid and bid <= self.game.money:
                                auction["highest_bid"] = bid
                                auction["highest_bidder"] = self.game
                        except ValueError:
                            console.print("[red]Invalid bid amount.")
                else:
                    bid = current_bid + random.randint(1000, 10000)
                    if bid <= participant.money and bid > auction["highest_bid"]:
                        auction["highest_bid"] = bid
                        auction["highest_bidder"] = participant
                        console.print(f"[magenta]{participant.name} bids {format_price(bid)} for {car.name}.")
            if auction["highest_bidder"]:
                auction["highest_bidder"].money -= auction["highest_bid"]
                if auction["highest_bidder"] == self.game:
                    self.game.owned[car.name] = car
                    console.print(f"[green]You win the auction for {car.name} with a bid of {format_price(auction['highest_bid'])}.")
                else:
                    auction["highest_bidder"].owned_cars[car.name] = car
                    console.print(f"[magenta]{auction['highest_bidder'].name} wins the auction for {car.name} with a bid of {format_price(auction['highest_bid'])}.")
                car.sold = True
            else:
                console.print(f"[red]No bids were placed for {car.name}.")
        self.auctions.clear()

# Market Class with Seasonal and Trend Influences
class Market:
    def __init__(self):
        self.market_trends = {"Luxury": 1.0, "Sports": 1.0, "Economy": 1.0}

    def update_market(self):
        for segment in self.market_trends:
            trend_change = random.uniform(0.95, 1.05)
            self.market_trends[segment] *= trend_change
            console.print(f"[yellow]The market trend for {segment} cars is now {self.market_trends[segment]:.2f}.")

    def apply_trends(self, car):
        if isinstance(car, LuxuryCar):
            car.price *= self.market_trends["Luxury"]
        elif isinstance(car, SportsCar):
            car.price *= self.market_trends["Sports"]
        elif isinstance(car, EconomyCar):
            car.price *= self.market_trends["Economy"]
        car.price = max(500, round(car.price, 2))

# Training Programs for Employees
class TrainingProgram:
    def __init__(self, name, cost, skill_boost, morale_boost):
        self.name = name
        self.cost = cost
        self.skill_boost = skill_boost
        self.morale_boost = morale_boost

    def enroll_employee(self, employee, game):
        if self.cost <= game.money:
            game.money -= self.cost
            employee.improve_skill()
            employee.affect_morale(self.morale_boost)
            console.print(f"[green]{employee.name} attended {self.name} training. Skill level increased by {self.skill_boost} and morale increased by {self.morale_boost}.")
        else:
            console.print(f"[red]Not enough money to enroll {employee.name} in {self.name}.")

# Marketing Campaigns
class MarketingCampaign:
    def __init__(self, name, cost, effectiveness):
        self.name = name
        self.cost = cost
        self.effectiveness = effectiveness

    def apply_campaign(self, dealership):
        if dealership.money >= self.cost:
            dealership.money -= self.cost
            dealership.reputation += self.effectiveness
            console.print(f"[green]Marketing campaign {self.name} launched! Effectiveness: {self.effectiveness}")
        else:
            console.print("[red]Not enough money for this campaign.")

# Service Department for Car Maintenance
class ServiceDepartment:
    def __init__(self):
        self.revenue = 0

    def service_car(self, car, customer):
        service_cost = random.randint(1000, 5000)
        if customer.budget >= service_cost:
            customer.budget -= service_cost
            car.maintain(datetime.now().year)
            self.revenue += service_cost
            console.print(f"[green]{customer.name} paid {format_price(service_cost)} for servicing {car.name}. Revenue added: {format_price(service_cost)}.")
        else:
            console.print(f"[red]{customer.name} cannot afford the service.")

# Car Leasing System
class LeaseContract:
    def __init__(self, car, customer, lease_duration, monthly_payment):
        self.car = car
        self.customer = customer
        self.lease_duration = lease_duration
        self.monthly_payment = monthly_payment

    def process_lease(self):
        total_cost = self.lease_duration * self.monthly_payment
        if total_cost <= self.customer.budget:
            self.customer.budget -= total_cost
            console.print(f"[green]{self.customer.name} leased {self.car.name} for {self.lease_duration} months at {format_price(self.monthly_payment)} per month. Total: {format_price(total_cost)}.")
        else:
            console.print(f"[red]{self.customer.name} couldn't afford the lease for {self.car.name}.")

# Main Game Class
class CarDealershipSimulator:
    def __init__(self):
        self.money = 1_000_000
        self.current_year = 2023
        self.owned = {}
        self.price_history = {}
        self.income_history = []
        self.expense_history = []
        self.reputation = 50  # Starting reputation
        self.ai_competitors = [
            AICompetitor("AutoElite", 800_000, strategy="Aggressive"),
            AICompetitor("Luxury Motors", 1_200_000, strategy="Balanced"),
            AICompetitor("Economy Wheels", 600_000, strategy="Economical")
        ]
        self.customers = [
            Customer("John Doe", 150_000, "Luxury", 8),
            Customer("Jane Smith", 50_000, "Economy", 5),
            Customer("Alice Johnson", 200_000, "Sports", 7),
            Customer("Bob Brown", 80_000, "Economy", 6)
        ]
        self.employees = [
            Employee("Alex", "Salesperson", 5),
            Employee("Beth", "Mechanic", 7),
            Employee("Charlie", "Finance Manager", 6)
        ]
        self.inventory = Inventory()
        self.financial_manager = FinancialManager(self)
        self.auction_house = AuctionHouse(self)
        self.market = Market()
        self.service_department = ServiceDepartment()

        self.luxury_cars = {}
        self.sports_cars = {}
        self.economy_cars = {}
        self.populate_cars()

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def populate_cars(self):
        # Luxury Cars
        luxury_car_list = [
            ("Rolls Royce Phantom", 450_000, 5, "New", 0),
            ("Bentley Mulsanne", 300_000, 10, "New", 1),
            ("Mercedes-Benz S-Class", 110_000, 5, "New", 1),
            # Add more luxury cars here...
        ]
        for name, price, mileage, condition, age in luxury_car_list:
            car = LuxuryCar(name, price, mileage, condition, age)
            self.luxury_cars[name] = car

        # Sports Cars
        sports_car_list = [
            ("Ferrari 488", 250_000, 10, "New", 1),
            ("Porsche 911", 120_000, 20, "Used", 2),
            ("Lamborghini Aventador", 400_000, 4, "New", 0),
            # Add more sports cars here...
        ]
        for name, price, mileage, condition, age in sports_car_list:
            car = SportsCar(name, price, mileage, condition, age)
            self.sports_cars[name] = car

        # Economy Cars
        economy_car_list = [
            ("Toyota Corolla", 20_000, 55, "Used", 5),
            ("Honda Civic", 19_000, 60, "Used", 6),
            ("Ford Focus", 21_000, 58, "Used", 6),
            # Add more economy cars here...
        ]
        for name, price, mileage, condition, age in economy_car_list:
            car = EconomyCar(name, price, mileage, condition, age)
            self.economy_cars[name] = car

    # --- Implementing the methods with enhancements ---

    def main_menu(self):
        while True:
            self.clear_console()
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=5),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            header_panel = Panel(
                Text("Welcome to the Advanced Car Dealership Simulator!", justify="center", style="bold cyan"),
                title="Main Menu",
                subtitle="Select an option",
                style="bold cyan",
                width=70,
                padding=(1, 2)
            )
            layout["header"].update(header_panel)

            table = Table.grid(padding=1)
            table.add_column(justify="center", style="bold yellow", width=3)
            table.add_column(justify="left", style="white", width=45)

            options = [
                ("1", "View Available Cars"),
                ("2", "Buy a Car"),
                ("3", "View Your Owned Cars"),
                ("4", "Sell a Car"),
                ("5", "Add Your Own Car"),
                ("6", "Modify a Car"),
                ("7", "Auction a Car"),
                ("8", "Simulate Next Year"),
                ("9", "Manage Employees"),
                ("10", "Manage Marketing"),
                ("11", "Manage Finances"),
                ("12", "Manage Service Department"),
                ("13", "Save Game"),
                ("14", "Load Game"),
                ("15", "View User Guide"),
                ("16", "Exit")
            ]

            for key, value in options:
                table.add_row(f"[yellow]{key}[/yellow]", f"[white]{value}[/white]")

            body_panel = Panel(table, style="green", padding=(1, 2), box=box.ROUNDED)
            layout["body"].update(body_panel)

            footer_text = Text(f"Year: {self.current_year} | Money: {format_price(self.money)} | Reputation: {self.reputation}", style="dim white", justify="center")
            footer_panel = Panel(footer_text, style="bold cyan", box=box.ROUNDED)
            layout["footer"].update(footer_panel)

            console.print(layout)
            choice = Prompt.ask("\n[bold yellow]Enter your choice: [/bold yellow]", choices=[opt[0] for opt in options])
            if choice == '1':
                # Call view available cars
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
                self.manage_marketing()
            elif choice == '11':
                self.manage_finances()
            elif choice == '12':
                self.manage_service_department()
            elif choice == '13':
                self.save_game()
            elif choice == '14':
                self.load_game()
            elif choice == '15':
                self.view_user_guide()
            elif choice == '16':
                console.print("[cyan]Exiting the game. Goodbye!")
                break

    def view_available_cars(self):
        while True:
            self.clear_console()
            console.print(Panel("🚗 [bold green]Available Cars:[/bold green]", title="[bold white]Car Listings[/bold white]", box=box.DOUBLE))

            table = Table(show_header=True, header_style="bold magenta", title="Current Inventory", box=box.MINIMAL_DOUBLE_HEAD)
            table.add_column("Name", style="dim")
            table.add_column("Price", justify="right")
            table.add_column("Mileage", justify="right")
            table.add_column("Condition", justify="center")
            table.add_column("Age", justify="center")

            for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
                for car in category.values():
                    if not car.sold:
                        table.add_row(
                            car.name,
                            format_price(car.price),
                            f"{car.mileage}k miles",
                            car.condition,
                            f"{car.age} years"
                        )

            console.print(table)
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to refresh...").strip().lower()
            if choice == 'menu':
                break

    def buy_car_menu(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Buy a Car Menu:", title="Select a Car Category"))
            categories = {"1": "Luxury", "2": "Sports", "3": "Economy", "4": "Return to Main Menu"}
            for key, value in categories.items():
                console.print(f"[yellow]{key}. {value}")

            choice = Prompt.ask("\nEnter your choice", choices=list(categories.keys()))
            if choice == '1':
                self.buy_car("Luxury", self.luxury_cars)
            elif choice == '2':
                self.buy_car("Sports", self.sports_cars)
            elif choice == '3':
                self.buy_car("Economy", self.economy_cars)
            elif choice == '4':
                break

    def buy_car(self, category, car_list):
        while True:
            self.clear_console()
            console.print(Panel(f"[bold green]{category} Cars:", title="Available Cars"))
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="dim")
            table.add_column("Price")
            table.add_column("Mileage")
            table.add_column("Condition")
            table.add_column("Age")

            available_cars = [car for car in car_list.values() if not car.sold]
            if not available_cars:
                console.print("[red]No cars available in this category.")
                input("Press Enter to return...")
                break

            for car in available_cars:
                table.add_row(car.name, format_price(car.price), f"{car.mileage}k miles", car.condition, f"{car.age} years")

            console.print(table)
            carname = Prompt.ask("\nWhich car would you like to buy?", choices=[car.name for car in available_cars] + ['menu'])

            if carname.lower() == 'menu':
                break

            car = car_list.get(carname)
            if car:
                self.process_car_purchase(car)
                break

    def process_car_purchase(self, car):
        while True:
            console.print(f"[yellow]{car.name}: {format_price(car.price)} | Mileage: {car.mileage}k miles | Condition: {car.condition} | Age: {car.age} years")
            buythiscar = Prompt.ask("Do you want to buy this car?", choices=["yes", "no"])
            if buythiscar == "yes":
                negotiation = random.randint(-5000, 5000)
                final_price = max(0, car.price + negotiation)
                if self.money - final_price >= 0:
                    if car.name in self.owned:
                        console.print("[red]You already own this car.")
                    else:
                        self.owned[car.name] = car
                        self.money -= final_price
                        car.owners += 1
                        car.sold = True
                        self.expense_history.append({"type": "purchase", "amount": final_price, "car": car.name, "year": self.current_year})
                        console.print(f"[green]You bought a {car.name} for {format_price(final_price)}.")
                else:
                    console.print("[red]You don't have enough money.")
            else:
                console.print("[cyan]Purchase cancelled.")
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break

    def view_owned_cars(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Your Owned Cars:", title="Owned Cars"))
            if not self.owned:
                console.print("[red]You do not own any cars.")
                input("Press Enter to return...")
                break
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="dim")
            table.add_column("Value")
            table.add_column("Age")
            table.add_column("Mileage")
            table.add_column("Condition")
            table.add_column("Owners")
            table.add_column("Maintenance History")

            for carname, car in self.owned.items():
                maintenance = ', '.join([f"{entry['year']}: {format_price(entry['cost'])}" for entry in car.maintenance_history])
                table.add_row(carname, format_price(car.price), f"{car.age} years", f"{car.mileage}k miles", car.condition, str(car.owners), maintenance)

            console.print(table)
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to refresh...").strip().lower()
            if choice == 'menu':
                break

    def sell_car(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Sell a Car:", title="Sell Car"))
            if not self.owned:
                console.print("[red]You do not own any cars.")
                input("Press Enter to return...")
                break
            carname = Prompt.ask("\nWhich car would you like to sell?", choices=list(self.owned.keys()) + ['menu'])
            if carname.lower() == 'menu':
                break
            if carname in self.owned:
                car = self.owned[carname]
                sellprice = car.price
                self.money += sellprice
                del self.owned[carname]
                self.income_history.append({"type": "sale", "amount": sellprice, "car": carname, "year": self.current_year})
                console.print(f"[green]You sold your {carname} for {format_price(sellprice)}.")
            else:
                console.print("[red]You do not own this car.")
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break

    def add_user_car(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Add Your Own Car:", title="Add Car"))
            carname = string.capwords(Prompt.ask("Enter the name of the car"))
            if carname.lower() == 'menu':
                break
            try:
                carprice = int(Prompt.ask("Enter the value of the car: $"))
                carmileage = int(Prompt.ask("Enter the mileage of the car: "))
                carcondition = Prompt.ask("Enter the condition of the car (New/Used)", choices=["New", "Used"])
                carage = int(Prompt.ask("Enter the age of the car (years): "))
            except ValueError:
                console.print("[red]Invalid input. Please enter valid numbers.")
                input("\nPress Enter to return to the main menu...")
                continue

            if carcondition not in ["New", "Used"]:
                console.print("[red]Invalid condition. Please enter 'New' or 'Used'.")
                input("\nPress Enter to return to the main menu...")
                continue

            if carprice >= 200_000:
                car = LuxuryCar(carname, carprice, carmileage, carcondition, carage)
                self.luxury_cars[carname] = car
            elif carprice >= 100_000:
                car = SportsCar(carname, carprice, carmileage, carcondition, carage)
                self.sports_cars[carname] = car
            else:
                car = EconomyCar(carname, carprice, carmileage, carcondition, carage)
                self.economy_cars[carname] = car

            console.print(f"[green]Your car {carname} has been added successfully.")
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break

    def modify_car(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Modify a Car:", title="Modify Car"))
            if not self.owned:
                console.print("[red]You do not own any cars.")
                input("Press Enter to return...")
                break
            carname = Prompt.ask("\nWhich car would you like to modify?", choices=list(self.owned.keys()) + ['menu'])
            if carname.lower() == 'menu':
                break
            if carname in self.owned:
                car = self.owned[carname]
                console.print(f"[yellow]{carname}: 1 car | Value: {format_price(car.price)}")
                options = {"1": "Performance Upgrade (+$10,000)", "2": "Luxury Upgrade (+$5,000)", "3": "Efficiency Upgrade (+$2,000)"}
                for key, value in options.items():
                    console.print(f"[yellow]{key}. {value}")

                upgrade_choice = Prompt.ask("Choose an upgrade (1-3)", choices=list(options.keys()))
                if upgrade_choice == '1':
                    car.modify("performance")
                elif upgrade_choice == '2':
                    car.modify("luxury")
                elif upgrade_choice == '3':
                    car.modify("efficiency")
            else:
                console.print("[red]You do not own this car.")
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break

    def auction_car(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Auction a Car:", title="Auction Car"))
            if not self.owned:
                console.print("[red]You do not own any cars.")
                input("Press Enter to return...")
                break
            carname = Prompt.ask("\nWhich car would you like to auction?", choices=list(self.owned.keys()) + ['menu'])
            if carname.lower() == 'menu':
                break
            if carname in self.owned:
                car = self.owned[carname]
                self.auction_house.list_car(car)
                self.auction_house.conduct_auction()
            else:
                console.print("[red]You do not own this car.")
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break

    def simulate(self):
        self.clear_console()
        console.print(Panel("[bold cyan]Simulating Car Prices for the next year...", title="Simulation"))
        loading_animation("Processing", duration=2)

        self.current_year += 1
        self.random_event()
        self.market.update_market()
        maintenance_costs = self.calculate_maintenance_costs()
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                car.depreciate()
                self.market.apply_trends(car)
                self.price_history.setdefault(car.name, []).append(car.price)
                car.age += 1  # Increase the age of each car by 1 year

        console.print(Panel("[bold green]New Car Prices:", title="Updated Prices"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="dim")
        table.add_column("Price")
        table.add_column("Mileage")
        table.add_column("Condition")
        table.add_column("Age")

        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                table.add_row(car.name, format_price(car.price), f"{car.mileage}k miles", car.condition, f"{car.age} years")

        console.print(table)

        console.print(Panel("[cyan]Your owned cars:", title="Owned Cars"))
        for carname, car in self.owned.items():
            console.print(f"[yellow]{carname}: 1 car")

        for competitor in self.ai_competitors:
            self.ai_turn(competitor)

        self.yearly_report(maintenance_costs)
        self.calculate_profit(maintenance_costs)

        input("\nPress Enter to return to the main menu...")

    def calculate_maintenance_costs(self):
        total_cost = 0
        for carname, car in self.owned.items():
            maintenance_cost = car.maintain(self.current_year)
            total_cost += maintenance_cost
            self.expense_history.append({"type": "maintenance", "amount": maintenance_cost, "car": carname, "year": self.current_year})
        return total_cost

    def calculate_profit(self, maintenance_costs):
        total_income = sum(entry["amount"] for entry in self.income_history if entry["year"] == self.current_year)
        total_expenses = sum(entry["amount"] for entry in self.expense_history if entry["year"] == self.current_year)
        net_profit = total_income - total_expenses
        self.financial_manager.calculate_taxes(net_profit)
        console.print(f"[green]Net Profit for the year: {format_price(net_profit)}")

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
        console.print(f"[magenta]Random event this year: [yellow]{event['event']}")
        console.print(f"[yellow]{event['description']}")
        for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
            for car in category.values():
                car.price = max(0, event["impact"](car.price))

    def ai_turn(self, competitor):
        competitor.expand_business()
        competitor.steal_customer(self.customers)
        competitor.sabotage(self)
        if random.choice([True, False]):
            available_cars = random.choice([self.luxury_cars, self.sports_cars, self.economy_cars])
            available_cars = [car for car in available_cars.values() if not car.sold]
            if available_cars:
                car = random.choice(available_cars)
                competitor.buy_car(car)
        else:
            if competitor.owned_cars:
                car = random.choice(list(competitor.owned_cars.values()))
                competitor.sell_car(car)

    def yearly_report(self, maintenance_costs):
        self.clear_console()
        console.print(Panel("[bold cyan]Yearly Report:", title="Yearly Summary"))
        console.print(f"[yellow]Year: {self.current_year}")
        console.print(f"[yellow]Money: {format_price(self.money)}")
        console.print(f"[yellow]Owned Cars: {list(self.owned.keys())}")
        console.print("[green]\nPrice History:")
        for model, history in self.price_history.items():
            console.print(f"[yellow]{model}: {', '.join(map(format_price, history))}")
        console.print("[green]\nIncome History:")
        for entry in self.income_history:
            console.print(f"[yellow]{entry}")
        console.print("[green]\nExpense History:")
        for entry in self.expense_history:
            console.print(f"[yellow]{entry}")
        console.print(f"[green]\nTotal Maintenance Costs: {format_price(maintenance_costs)}")
        input("\nPress Enter to return to the main menu...")

    def manage_employees(self):
        while True:
            self.clear_console()
            console.print(Panel("👥 [bold green]Manage Employees[/bold green]", title="[bold white]Employee Management[/bold white]"))

            table = Table(show_header=True, header_style="bold magenta", title="Employee Roster")
            table.add_column("No.", style="dim", width=3)
            table.add_column("Name", style="white", width=15)
            table.add_column("Role", style="yellow", width=15)
            table.add_column("Skill Level", style="cyan", justify="right")

            for i, employee in enumerate(self.employees, start=1):
                table.add_row(str(i), employee.name, employee.role, str(employee.skill_level))

            console.print(table)
            choice = Prompt.ask("Select an employee to improve their skills (or type 'menu' to return)").strip().lower()
            if choice == 'menu':
                break
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(self.employees):
                    training_programs = [
                        TrainingProgram("Sales Mastery", 5000, 1, 2),
                        TrainingProgram("Technical Workshop", 7000, 1, 1),
                        TrainingProgram("Leadership Seminar", 10000, 2, 3)
                    ]
                    console.print("Available Training Programs:")
                    for idx, program in enumerate(training_programs, start=1):
                        console.print(f"[yellow]{idx}. {program.name} - Cost: {format_price(program.cost)}")
                    program_choice = Prompt.ask("Select a training program (or type 'menu' to return)").strip().lower()
                    if program_choice == 'menu':
                        continue
                    program_choice = int(program_choice) - 1
                    if 0 <= program_choice < len(training_programs):
                        training_programs[program_choice].enroll_employee(self.employees[choice], self)
                    else:
                        console.print("[red]Invalid training program selection.")
                else:
                    console.print("[red]Invalid employee selection.")
            except ValueError:
                console.print("[red]Please enter a valid number.")
            input("\nPress Enter to return to the previous menu...")

    def manage_marketing(self):
        campaigns = [
            MarketingCampaign("Social Media Blast", 50000, 10),
            MarketingCampaign("TV Commercial", 150000, 30),
            MarketingCampaign("Billboard Ads", 100000, 20)
        ]
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Manage Marketing Campaigns", title="Marketing"))
            for i, campaign in enumerate(campaigns, start=1):
                console.print(f"[yellow]{i}. {campaign.name} - Cost: {format_price(campaign.cost)} - Effectiveness: {campaign.effectiveness}")

            choice = Prompt.ask("\nSelect a campaign to launch or type 'menu' to return", choices=[str(i) for i in range(1, len(campaigns) + 1)] + ['menu'])
            if choice == 'menu':
                break
            else:
                campaign = campaigns[int(choice) - 1]
                campaign.apply_campaign(self)
                input("\nPress Enter to return to the previous menu...")
                break

    def manage_finances(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]Manage Finances", title="Finances"))
            console.print(f"[yellow]Cash Flow: {format_price(self.financial_manager.cash_flow)}")
            console.print(f"[yellow]Outstanding Loans: {len(self.financial_manager.loans)}")
            console.print(f"[yellow]Investments: {len(self.financial_manager.investments)}")
            console.print(f"[yellow]Crypto Portfolio: {len(self.financial_manager.crypto_portfolio)}")
            console.print(f"[yellow]Taxes Due: {format_price(self.financial_manager.taxes_due)}")
            choice = Prompt.ask("\n1. Pay Taxes\n2. Take Loan\n3. Invest\n4. View Profit/Loss Statement\nmenu. Return to Menu", choices=["1", "2", "3", "4", "menu"])
            if choice == '1':
                self.financial_manager.pay_taxes()
            elif choice == '2':
                amount = int(Prompt.ask("Enter loan amount: $"))
                interest_rate = float(Prompt.ask("Enter interest rate: %"))
                term_years = int(Prompt.ask("Enter term in years: "))
                self.financial_manager.take_loan(amount, interest_rate, term_years)
            elif choice == '3':
                invest_choice = Prompt.ask("1. Stock\n2. Cryptocurrency", choices=["1", "2"])
                amount = int(Prompt.ask("Enter investment amount: $"))
                if invest_choice == '1':
                    stock_name = Prompt.ask("Enter stock name:")
                    self.financial_manager.invest_in_stock(stock_name, amount)
                else:
                    crypto_name = Prompt.ask("Enter cryptocurrency name:")
                    self.financial_manager.invest_in_crypto(crypto_name, amount)
            elif choice == '4':
                console.print(self.financial_manager.profit_loss_statement)
                input("\nPress Enter to return to the previous menu...")
            elif choice == 'menu':
                break
            input("\nPress Enter to return to the previous menu...")

    def manage_service_department(self):
        while True:
            self.clear_console()
            console.print(Panel("🔧 [bold green]Manage Service Department[/bold green]", title="[bold white]Service Management[/bold white]"))

            table = Table(show_header=True, header_style="bold magenta", title="Service Customers")
            table.add_column("No.", style="dim", width=3)
            table.add_column("Customer Name", style="white", width=20)
            table.add_column("Budget", style="yellow", justify="right")

            for i, customer in enumerate(self.customers, start=1):
                table.add_row(str(i), customer.name, format_price(customer.budget))

            console.print(table)
            choice = Prompt.ask("\nSelect a customer for service or type 'menu' to return", choices=[str(i) for i in range(1, len(self.customers) + 1)] + ['menu'])
            if choice == 'menu':
                break
            else:
                customer = self.customers[int(choice) - 1]
                car_name = Prompt.ask("Enter car name for service:")
                # For simplicity, we'll assume the customer owns the car they want serviced.
                car = Car(car_name, 0, 0, "Used", 0)  # Placeholder car
                self.service_department.service_car(car, customer)
                input("\nPress Enter to return to the previous menu...")
                break

    def save_game(self):
        while True:
            slot = Prompt.ask("Enter save slot number (1-3) or type 'menu' to return").strip().lower()
            if slot == 'menu':
                break
            if slot in ["1", "2", "3"]:
                conn = sqlite3.connect(f'car_dealership_save_{slot}.db')
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS game_state 
                             (id INTEGER PRIMARY KEY, money INTEGER, current_year INTEGER, owned TEXT, 
                             price_history TEXT, income_history TEXT, expense_history TEXT, ai_competitors TEXT, employees TEXT)''')

                game_state = {
                    "money": self.money,
                    "owned": json.dumps({name: car.__dict__ for name, car in self.owned.items()}),
                    "current_year": self.current_year,
                    "price_history": json.dumps(self.price_history),
                    "income_history": json.dumps(self.income_history),
                    "expense_history": json.dumps(self.expense_history),
                    "ai_competitors": json.dumps({comp.name: comp.__dict__ for comp in self.ai_competitors}),
                    "employees": json.dumps([emp.__dict__ for emp in self.employees])
                }

                c.execute("INSERT INTO game_state (money, current_year, owned, price_history, income_history, expense_history, ai_competitors, employees) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                          (game_state['money'], game_state['current_year'], game_state['owned'], game_state['price_history'], game_state['income_history'], 
                           game_state['expense_history'], game_state['ai_competitors'], game_state['employees']))
                conn.commit()
                conn.close()
                console.print("[green]Game saved successfully.")
                input("\nPress Enter to return to the main menu...")
                break
            else:
                console.print("[red]Invalid slot number.")

    def load_game(self):
        while True:
            slot = Prompt.ask("Enter load slot number (1-3) or type 'menu' to return").strip().lower()
            if slot == 'menu':
                break
            if slot in ["1", "2", "3"]:
                conn = sqlite3.connect(f'car_dealership_save_{slot}.db')
                c = conn.cursor()
                c.execute("SELECT * FROM game_state ORDER BY id DESC LIMIT 1")
                row = c.fetchone()
                conn.close()

                if row:
                    self.money = row[1]
                    self.current_year = row[2]
                    self.owned = {name: Car(**car) for name, car in json.loads(row[3]).items()}
                    self.price_history = json.loads(row[4])
                    self.income_history = json.loads(row[5])
                    self.expense_history = json.loads(row[6])
                    self.ai_competitors = [AICompetitor(name, data['money']) for name, data in json.loads(row[7]).items()]
                    self.employees = [Employee(**emp) for emp in json.loads(row[8])]
                    console.print("[green]Game loaded successfully.")
                else:
                    console.print("[red]No saved game found in this slot. Starting a new game.")
                input("\nPress Enter to return to the main menu...")
                break
            else:
                console.print("[red]Invalid slot number.")

    def view_user_guide(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]User Guide:", title="Guide"))
            guide_menu = Table(show_header=False, box=None)
            guide_menu.add_row("[bold yellow]1[/bold yellow]. View available cars")
            guide_menu.add_row("[bold yellow]2[/bold yellow]. Buy a car")
            guide_menu.add_row("[bold yellow]3[/bold yellow]. View your owned cars")
            guide_menu.add_row("[bold yellow]4[/bold yellow]. Sell a car")
            guide_menu.add_row("[bold yellow]5[/bold yellow]. Add your own car")
            guide_menu.add_row("[bold yellow]6[/bold yellow]. Modify a car")
            guide_menu.add_row("[bold yellow]7[/bold yellow]. Auction a car")
            guide_menu.add_row("[bold yellow]8[/bold yellow]. Simulate next year")
            guide_menu.add_row("[bold yellow]9[/bold yellow]. Manage Employees")
            guide_menu.add_row("[bold yellow]10[/bold yellow]. Manage Marketing")
            guide_menu.add_row("[bold yellow]11[/bold yellow]. Manage Finances")
            guide_menu.add_row("[bold yellow]12[/bold yellow]. Manage Service Department")
            guide_menu.add_row("[bold yellow]13[/bold yellow]. Save game")
            guide_menu.add_row("[bold yellow]14[/bold yellow]. Load game")
            guide_menu.add_row("[bold yellow]15[/bold yellow]. Exit")
            guide_menu.add_row("[bold yellow]0[/bold yellow]. Return to Main Menu")

            console.print(guide_menu)

            try:
                choice = Prompt.ask("\nEnter '0' to return to the main menu", choices=["0"])
                if choice == "0":
                    break
            except ValueError:
                console.print("[red]Invalid input. Please enter '0' to return to the main menu.")

# Export an instance for the backend:
simulator = CarDealershipSimulator()
