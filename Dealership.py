import random
import string
import json
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from faker import Faker
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress
from datetime import datetime
from rich.text import Text
import time


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

# Car Class and its subclasses
class Car:
    def __init__(self, name, price, mileage, condition, age):
        self.name = name
        self.price = price
        self.mileage = mileage
        self.condition = condition
        self.age = age
        self.owners = 0
        self.maintenance_history = []
        self.customizations = []

    def depreciate(self):
        depreciation_rate = 0.1 if self.condition == "New" else 0.2
        self.price = max(0, self.price - self.price * depreciation_rate)

    def maintain(self, year):
        maintenance_cost = (1000 * self.age) if self.condition == "New" else (2000 * self.age)
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
                self.locations[from_location].remove(car)
                self.locations[to_location].append(car)
                console.print(f"[cyan]Moved {car.name} from {from_location} to {to_location}.")
            else:
                console.print("[red]Car not found in the specified location!")
        else:
            console.print("[red]Invalid location!")

    def check_inventory(self):
        for location, cars in self.locations.items():
            console.print(f"[bold yellow]{location}:")
            for car in cars:
                console.print(f" - {car.name} ({format_price(car.price)})")
            if len(cars) < self.low_stock_threshold:
                console.print(f"[red]Low stock in {location} - Consider ordering more cars.")

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
        discount = random.randint(0, int(car_price * (self.negotiation_skill / 10)))
        final_price = car_price - discount
        if self.trade_in_car:
            final_price -= self.trade_in_car.price * 0.8  # Trade-in value is 80% of the car's current price
        return final_price

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
        else:
            console.print(f"[red]{self.name} could not afford {car.name}.")

# Employee Class with Training Programs
class Employee:
    def __init__(self, name, role, skill_level):
        self.name = name
        self.role = role
        self.skill_level = skill_level
        self.morale = 5

    def improve_skill(self):
        self.skill_level += 1
        console.print(f"[green]{self.name}'s skill level has improved to {self.skill_level}!")

    def affect_morale(self, change):
        self.morale = max(1, min(10, self.morale + change))
        morale_status = "happy" if self.morale > 7 else "neutral" if self.morale > 4 else "unhappy"
        console.print(f"[yellow]{self.name} is now {morale_status} with morale level {self.morale}.")

# AI Competitor with Advanced Strategies
class AICompetitor:
    def __init__(self, name, money, strategy="Balanced"):
        self.name = name
        self.money = money
        self.owned_cars = {}
        self.dealerships = 1
        self.strategy = strategy

    def expand_business(self):
        if self.money >= 500_000:
            self.money -= 500_000
            self.dealerships += 1
            console.print(f"[magenta]{self.name} has opened a new dealership! Total dealerships: {self.dealerships}")
        else:
            console.print(f"[red]{self.name} doesn't have enough money to open a new dealership.")

    def steal_customer(self, customers):
        if self.strategy == "Aggressive":
            target = random.choice(customers)
            if random.random() > 0.5:
                console.print(f"[magenta]{self.name} has stolen a customer: {target.name}!")
                customers.remove(target)
            else:
                console.print(f"[cyan]{self.name} tried to steal a customer but failed.")
        elif self.strategy == "Balanced":
            pass

    def sabotage(self, player_dealership):
        if self.strategy == "Aggressive" and random.random() > 0.5:
            affected_cars = random.sample(list(player_dealership.owned.values()), k=random.randint(1, 3))
            for car in affected_cars:
                car.price -= random.randint(5000, 20000)
                console.print(f"[red]{self.name} sabotaged {car.name}, reducing its value!")

    def buy_car(self, car):
        negotiation = random.randint(-5000, 5000)
        final_price = max(0, car.price + negotiation)
        if self.money >= final_price:
            self.owned_cars[car.name] = car
            self.money -= final_price
            car.owners += 1
            console.print(f"[magenta]{self.name} bought {car.name} for {format_price(final_price)}.")
        else:
            console.print(f"[red]{self.name} couldn't afford {car.name}.")

    def sell_car(self, car):
        sell_price = car.price
        if car.name in self.owned_cars:
            del self.owned_cars[car.name]
            self.money += sell_price
            console.print(f"[magenta]{self.name} sold {car.name} for {format_price(sell_price)}.")

# Financial Manager with Detailed Management
class FinancialManager:
    def __init__(self):
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
        console.print(f"[green]Loan of {format_price(amount)} taken with {interest_rate}% interest over {term_years} years. Total repayment: {format_price(total_payment)}.")

    def calculate_taxes(self, profit):
        tax_rate = 0.3
        self.taxes_due = profit * tax_rate
        console.print(f"[yellow]Taxes calculated on profit: {format_price(self.taxes_due)}")

    def pay_taxes(self):
        if self.taxes_due > 0:
            console.print(f"[green]Taxes of {format_price(self.taxes_due)} paid.")
            self.taxes_due = 0
        else:
            console.print("[cyan]No taxes due.")

    def invest_in_stock(self, stock_name, amount):
        if amount <= game.money:
            game.money -= amount
            self.investments.append({"stock": stock_name, "amount": amount, "purchase_date": datetime.now().strftime('%Y-%m-%d')})
            console.print(f"[green]Invested {format_price(amount)} in {stock_name}.")
        else:
            console.print(f"[red]Not enough money to invest in {stock_name}.")

    def invest_in_crypto(self, crypto_name, amount):
        if amount <= game.money:
            game.money -= amount
            self.crypto_portfolio[crypto_name] = self.crypto_portfolio.get(crypto_name, 0) + amount
            console.print(f"[green]Invested {format_price(amount)} in {crypto_name} cryptocurrency.")
        else:
            console.print(f"[red]Not enough money to invest in {crypto_name}.")

    def generate_financial_report(self):
        df = pd.DataFrame(self.profit_loss_statement)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        plt.figure(figsize=(10, 6))
        df['amount'].plot(kind='bar', color='teal')
        plt.title('📈 Financial Report')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.grid(True)
        plt.show()

    def generate_interactive_report(self):
        df = pd.DataFrame(self.profit_loss_statement)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        fig = px.line(df, x=df.index, y='amount', title='📊 Interactive Financial Report')
        fig.update_traces(line=dict(color='royalblue', width=4))
        fig.show()

# Auction House for Buying and Selling Cars
class AuctionHouse:
    def __init__(self):
        self.auctions = []

    def list_car(self, car):
        starting_bid = car.price // 2
        self.auctions.append({"car": car, "highest_bid": starting_bid, "highest_bidder": None})
        console.print(f"[cyan]{car.name} has been listed in the auction house with a starting bid of {format_price(starting_bid)}.")

    def conduct_auction(self):
        for auction in self.auctions:
            car = auction["car"]
            current_bid = auction["highest_bid"]
            for competitor in game.ai_competitors:
                bid = current_bid + random.randint(1000, 10000)
                if bid <= competitor.money:
                    auction["highest_bid"] = bid
                    auction["highest_bidder"] = competitor
                    console.print(f"[magenta]{competitor.name} bids {format_price(bid)} for {car.name}.")
            if auction["highest_bidder"]:
                auction["highest_bidder"].money -= auction["highest_bid"]
                console.print(f"[green]{auction['highest_bidder'].name} wins the auction for {car.name} with a bid of {format_price(auction["highest_bid"])}.")
            else:
                console.print(f"[red]No bids were placed for {car.name}.")
        self.auctions.clear()

# Market Class with Seasonal and Trend Influences
class Market:
    def __init__(self):
        self.market_trends = {"Luxury": 1.0, "Sports": 1.0, "Economy": 1.0}

    def update_market(self):
        for segment in self.market_trends:
            trend_change = random.uniform(0.9, 1.1)
            self.market_trends[segment] *= trend_change
            console.print(f"[yellow]The market trend for {segment} cars is now {self.market_trends[segment]:.2f}.")

    def apply_trends(self, car):
        if isinstance(car, LuxuryCar):
            car.price *= self.market_trends["Luxury"]
        elif isinstance(car, SportsCar):
            car.price *= self.market_trends["Sports"]
        elif isinstance(car, EconomyCar):
            car.price *= self.market_trends["Economy"]
        car.price = max(0, car.price)

# Training Programs for Employees
class TrainingProgram:
    def __init__(self, name, cost, skill_boost, morale_boost):
        self.name = name
        self.cost = cost
        self.skill_boost = skill_boost
        self.morale_boost = morale_boost

    def enroll_employee(self, employee):
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
        customer.budget -= service_cost
        car.maintain(datetime.now().year)
        self.revenue += service_cost
        console.print(f"[green]{customer.name} paid {format_price(service_cost)} for servicing {car.name}. Revenue added: {format_price(service_cost)}.")

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
            AICompetitor("Competitor A", 800_000, strategy="Aggressive"),
            AICompetitor("Competitor B", 1_200_000, strategy="Balanced")
        ]
        self.customers = [
            Customer("John Doe", 150_000, "Luxury", 8),
            Customer("Jane Smith", 50_000, "Economy", 5)
        ]
        self.employees = [
            Employee("Alice", "Salesperson", 5),
            Employee("Bob", "Mechanic", 7)
        ]
        self.inventory = Inventory()
        self.financial_manager = FinancialManager()
        self.auction_house = AuctionHouse()
        self.market = Market()
        self.service_department = ServiceDepartment()

        self.luxury_cars = {
            "Rolls Royce": LuxuryCar("Rolls Royce", 500_000, 10, "New", 0),
            "Maybach": LuxuryCar("Maybach", 200_000, 15, "New", 0),
            "Bmw Alphina": LuxuryCar("Bmw Alphina", 150_000, 20, "New", 0),
            "Bentley": LuxuryCar("Bentley", 250_000, 8, "New", 0),
            "Aston Martin": LuxuryCar("Aston Martin", 180_000, 12, "New", 0),
            "Mercedes-Benz S-Class": LuxuryCar("Mercedes-Benz S-Class", 110_000, 5, "New", 1),
            "Jaguar XJ": LuxuryCar("Jaguar XJ", 100_000, 18, "Used", 3),
            "Lexus LS": LuxuryCar("Lexus LS", 90_000, 22, "New", 2),
            "Audi A8": LuxuryCar("Audi A8", 95_000, 20, "Used", 2),
            "Maserati Quattroporte": LuxuryCar("Maserati Quattroporte", 120_000, 15, "New", 1),
            "Tesla Model S Plaid": LuxuryCar("Tesla Model S Plaid", 130_000, 0, "New", 0),
            "Cadillac CT6": LuxuryCar("Cadillac CT6", 75_000, 28, "Used", 4),
            "Infiniti Q70": LuxuryCar("Infiniti Q70", 65_000, 25, "Used", 5),
            "Bentley Mulsanne": LuxuryCar("Bentley Mulsanne", 300_000, 10, "New", 1),
            "Rolls Royce Phantom": LuxuryCar("Rolls Royce Phantom", 450_000, 5, "New", 0),
            "Lamborghini Urus": LuxuryCar("Lamborghini Urus", 200_000, 8, "New", 1),
            "Porsche Panamera": LuxuryCar("Porsche Panamera", 150_000, 12, "New", 2),
            "Mercedes-Maybach GLS": LuxuryCar("Mercedes-Maybach GLS", 170_000, 3, "New", 0),
            "Land Rover Range Rover": LuxuryCar("Land Rover Range Rover", 160_000, 25, "Used", 4),
            "BMW 7 Series": LuxuryCar("BMW 7 Series", 100_000, 20, "Used", 3),
            "Genesis G90": LuxuryCar("Genesis G90", 85_000, 15, "New", 2),
            "Lexus LX": LuxuryCar("Lexus LX", 90_000, 18, "Used", 4),
            "Volvo XC90": LuxuryCar("Volvo XC90", 80_000, 22, "Used", 5),
            "Jaguar F-Pace": LuxuryCar("Jaguar F-Pace", 75_000, 30, "Used", 6),
            "Alfa Romeo Giulia Quadrifoglio": LuxuryCar("Alfa Romeo Giulia Quadrifoglio", 80_000, 35, "Used", 3),
            }

        self.sports_cars = {
            "Mclaren": SportsCar("Mclaren", 400_000, 5, "New", 0),
            "Lamborghini": SportsCar("Lamborghini", 300_000, 8, "New", 0),
            "Porsche": SportsCar("Porsche", 150_000, 18, "New", 0),
            "Ferrari": SportsCar("Ferrari", 350_000, 6, "New", 0),
            "Bugatti": SportsCar("Bugatti", 700_000, 4, "New", 0),
            "Chevrolet Corvette": SportsCar("Chevrolet Corvette", 85_000, 25, "Used", 2),
            "Nissan GT-R": SportsCar("Nissan GT-R", 115_000, 12, "New", 1),
            "Ford Mustang": SportsCar("Ford Mustang", 60_000, 30, "Used", 3),
            "Dodge Viper": SportsCar("Dodge Viper", 95_000, 20, "Used", 5),
            "BMW M3": SportsCar("BMW M3", 70_000, 22, "New", 2),
            "Aston Martin Vantage": SportsCar("Aston Martin Vantage", 140_000, 10, "New", 1),
            "Toyota Supra": SportsCar("Toyota Supra", 55_000, 35, "Used", 3),
            "Subaru WRX STI": SportsCar("Subaru WRX STI", 50_000, 40, "Used", 4),
            "Lamborghini Huracan": SportsCar("Lamborghini Huracan", 200_000, 8, "New", 0),
            "Ferrari 488": SportsCar("Ferrari 488", 250_000, 10, "New", 1),
            "Porsche 911": SportsCar("Porsche 911", 120_000, 20, "Used", 2),
            "Audi R8": SportsCar("Audi R8", 160_000, 15, "New", 1),
            "Mercedes-AMG GT": SportsCar("Mercedes-AMG GT", 140_000, 12, "New", 2),
            "Chevrolet Camaro ZL1": SportsCar("Chevrolet Camaro ZL1", 65_000, 35, "Used", 3),
            "Ford GT": SportsCar("Ford GT", 500_000, 4, "New", 0),
            "Jaguar F-Type": SportsCar("Jaguar F-Type", 90_000, 18, "Used", 4),
            "Maserati GranTurismo": SportsCar("Maserati GranTurismo", 120_000, 20, "Used", 3),
            "Acura NSX": SportsCar("Acura NSX", 150_000, 10, "New", 2),
            "Aston Martin DB11": SportsCar("Aston Martin DB11", 200_000, 5, "New", 0),
            "BMW i8": SportsCar("BMW i8", 130_000, 22, "Used", 2),
            "Lexus LC": SportsCar("Lexus LC", 100_000, 18, "New", 1),
            "Alfa Romeo 4C": SportsCar("Alfa Romeo 4C", 70_000, 25, "Used", 3),
            "McLaren 720S": SportsCar("McLaren 720S", 300_000, 7, "New", 0),
            "Lamborghini Aventador": SportsCar("Lamborghini Aventador", 400_000, 4, "New", 0),
        }

        self.economy_cars = {
            "Alfa Romeo": EconomyCar("Alfa Romeo", 50_000, 25, "Used", 3),
            "Ford": EconomyCar("Ford", 40_000, 30, "Used", 5),
            "Toyota": EconomyCar("Toyota", 50_000, 35, "Used", 4),
            "Mini Cooper": EconomyCar("Mini Cooper", 60_000, 28, "Used", 6),
            "Honda": EconomyCar("Honda", 30_000, 40, "Used", 5),
            "Nissan": EconomyCar("Nissan", 35_000, 38, "Used", 4),
            "Hyundai Elantra": EconomyCar("Hyundai Elantra", 20_000, 50, "Used", 8),
            "Kia Soul": EconomyCar("Kia Soul", 25_000, 45, "Used", 6),
            "Volkswagen Golf": EconomyCar("Volkswagen Golf", 25_000, 50, "Used", 7),
            "Mazda 3": EconomyCar("Mazda 3", 22_000, 55, "Used", 6),
            "Chevrolet Cruze": EconomyCar("Chevrolet Cruze", 18_000, 60, "Used", 7),
            "Toyota Corolla": EconomyCar("Toyota Corolla", 20_000, 55, "Used", 5),
            "Honda Civic": EconomyCar("Honda Civic", 19_000, 60, "Used", 6),
            "Ford Focus": EconomyCar("Ford Focus", 21_000, 58, "Used", 6),
            "Kia Rio": EconomyCar("Kia Rio", 15_000, 65, "Used", 7),
            "Hyundai Accent": EconomyCar("Hyundai Accent", 14_000, 70, "Used", 8),
            "Nissan Versa": EconomyCar("Nissan Versa", 13_000, 75, "Used", 8),
            "Volkswagen Jetta": EconomyCar("Volkswagen Jetta", 18_000, 60, "Used", 7),
            "Subaru Impreza": EconomyCar("Subaru Impreza", 17_000, 63, "Used", 7),
            "Chevrolet Sonic": EconomyCar("Chevrolet Sonic", 12_000, 80, "Used", 9),
            "Toyota Yaris": EconomyCar("Toyota Yaris", 16_000, 68, "Used", 7),
            "Honda Fit": EconomyCar("Honda Fit", 17_000, 65, "Used", 6),
            "Mazda 2": EconomyCar("Mazda 2", 14_000, 70, "Used", 7),
            "Hyundai i20": EconomyCar("Hyundai i20", 13_000, 75, "Used", 8),
            "Renault Clio": EconomyCar("Renault Clio", 15_000, 72, "Used", 7),
            "Peugeot 208": EconomyCar("Peugeot 208", 16_000, 70, "Used", 6),
            "Citroen C3": EconomyCar("Citroen C3", 14_000, 73, "Used", 7),
            "Fiat 500": EconomyCar("Fiat 500", 13_000, 75, "Used", 8),
            "Ford Fiesta": EconomyCar("Ford Fiesta", 14_000, 72, "Used", 7),
            "Dacia Sandero": EconomyCar("Dacia Sandero", 11_000, 80, "Used", 8),
            "Suzuki Swift": EconomyCar("Suzuki Swift", 13_000, 75, "Used", 7),
            "Chevrolet Spark": EconomyCar("Chevrolet Spark", 10_000, 85, "Used", 9),
            "Mitsubishi Mirage": EconomyCar("Mitsubishi Mirage", 12_000, 80, "Used", 8),
        }


    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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
                ("13", "Generate Financial Report"),
                ("14", "Generate Interactive Report"),
                ("15", "Save Game"),
                ("16", "Load Game"),
                ("17", "View User Guide"),
                ("18", "Exit")
            ]

            for key, value in options:
                table.add_row(f"[yellow]{key}[/yellow]", f"[white]{value}[/white]")

            body_panel = Panel(table, style="green", padding=(1, 2))
            layout["body"].update(body_panel)

            footer_text = Text(f"Year: {self.current_year} | Money: {format_price(self.money)} | Reputation: {self.reputation}", style="dim white", justify="center")
            footer_panel = Panel(footer_text, style="bold cyan")
            layout["footer"].update(footer_panel)

            console.print(layout)

            choice = Prompt.ask("\n[bold yellow]Enter your choice: [/bold yellow]", choices=[opt[0] for opt in options])

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
                self.manage_marketing()
            elif choice == '11':
                self.manage_finances()
            elif choice == '12':
                self.manage_service_department()
            elif choice == '13':
                self.financial_manager.generate_financial_report()
            elif choice == '14':
                self.financial_manager.generate_interactive_report()  # Fixed the method call here
            elif choice == '15':
                self.save_game()
            elif choice == '16':
                self.load_game()
            elif choice == '17':
                self.view_user_guide()
            elif choice == '18':
                console.print("[cyan]Exiting the game. Goodbye!")
                break

    # Add additional methods for managing marketing, finances, and service department
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
            elif choice == 'menu':
                break

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
                car = next((car for car in self.owned.values() if car.name == car_name), None)
                if car:
                    self.service_department.service_car(car, customer)
                else:
                    console.print("[red]Car not found.")
                break


    # Methods for viewing, buying, and selling cars, and simulation remain the same...
    # Additional features like storylines, achievements, and competitions can be integrated similarly.

    def view_available_cars(self):
        while True:
            self.clear_console()
            console.print(Panel("🚗 [bold green]Available Cars:[/bold green]", title="[bold white]Car Listings[/bold white]"))

            table = Table(show_header=True, header_style="bold magenta", title="Current Inventory")
            table.add_column("Name", style="dim")
            table.add_column("Price", justify="right")
            table.add_column("Mileage", justify="right")
            table.add_column("Condition", justify="center")
            table.add_column("Age", justify="center")

            for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
                for car in category.values():
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

            choice = Prompt.ask("\nEnter your choice", choices=categories.keys())

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

            for car in car_list.values():
                table.add_row(car.name, format_price(car.price), f"{car.mileage}k miles", car.condition, f"{car.age} years")

            console.print(table)
            carname = Prompt.ask("\nWhich car would you like to buy?", choices=[car.name for car in car_list.values()])

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
            carname = Prompt.ask("\nWhich car would you like to sell?", choices=list(self.owned.keys()))
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
            carname = Prompt.ask("\nWhich car would you like to modify?", choices=list(self.owned.keys()))
            if carname.lower() == 'menu':
                break
            if carname in self.owned:
                car = self.owned[carname]
                console.print(f"[yellow]{carname}: 1 car | Value: {format_price(car.price)}")
                options = {"1": "Performance Upgrade (+$10,000)", "2": "Luxury Upgrade (+$5,000)", "3": "Efficiency Upgrade (+$2,000)"}
                for key, value in options.items():
                    console.print(f"[yellow]{key}. {value}")

                upgrade_choice = Prompt.ask("Choose an upgrade (1-3)", choices=options.keys())
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
            carname = Prompt.ask("\nWhich car would you like to auction?", choices=list(self.owned.keys()))
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
        while True:
            self.clear_console()
            console.print(Panel("[bold cyan]Simulating Car Prices for the next year...", title="Simulation"))
            with Progress() as progress:
                task = progress.add_task("[cyan]Simulating...", total=100)
                for _ in range(100):
                    time.sleep(0.03)  # Simulate processing time
                    progress.advance(task)
            
            self.current_year += 1
            self.random_event()
            maintenance_costs = self.calculate_maintenance_costs()
            for category in [self.luxury_cars, self.sports_cars, self.economy_cars]:
                for car in category.values():
                    car.depreciate()
                    self.price_history.setdefault(car.name, []).append(car.price)
                    car.age += 1  # Increase the age of each car by 1 year

            # Corrected this line: wrapping the text with Panel
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

            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
                break


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
        console.print(f"[green]Total value of your assets: {format_price(total_assets)}")
        console.print(f"[green]Profit from car sales: {format_price(profit - maintenance_costs)}")

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
        if random.choice([True, False]):
            available_cars = random.choice([self.luxury_cars, self.sports_cars, self.economy_cars])
            car = random.choice(list(available_cars.values()))
            competitor.buy_car(car)
        else:
            if competitor.owned_cars:
                car = random.choice(list(competitor.owned_cars.values()))
                competitor.sell_car(car)

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
                    self.employees[choice].improve_skill()
                else:
                    console.print("[red]Invalid selection.")
            except ValueError:
                console.print("[red]Please enter a valid number.")
            input("\nPress Enter to return to the previous menu...")

    def yearly_report(self, maintenance_costs):
        while True:
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
            choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
            if choice == 'menu':
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
                choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
                if choice == 'menu':
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
                choice = Prompt.ask("\nType 'menu' to return to the main menu or press Enter to continue...").strip().lower()
                if choice == 'menu':
                    break
            else:
                console.print("[red]Invalid slot number.")

    def view_user_guide(self):
        while True:
            self.clear_console()
            console.print(Panel("[bold green]User Guide:", title="Guide"))
            menu = Table(show_header=False, box=None)
            menu.add_row("[bold yellow]1[/bold yellow]. View available cars: Displays the list of cars available for purchase with their details.")
            menu.add_row("[bold yellow]2[/bold yellow]. Buy a car: Allows you to purchase a car if you have enough money.")
            menu.add_row("[bold yellow]3[/bold yellow]. View your owned cars: Shows the cars you currently own along with their details.")
            menu.add_row("[bold yellow]4[/bold yellow]. Sell a car: Enables you to sell one of your owned cars.")
            menu.add_row("[bold yellow]5[/bold yellow]. Add your own car: Allows you to add a car of your own to the dealership.")
            menu.add_row("[bold yellow]6[/bold yellow]. Modify a car: Lets you apply upgrades to your cars, increasing their value.")
            menu.add_row("[bold yellow]7[/bold yellow]. Auction a car: Puts a car up for auction, allowing AI competitors to bid against you.")
            menu.add_row("[bold yellow]8[/bold yellow]. Simulate next year: Advances the game by one year, applying random events and updating car prices.")
            menu.add_row("[bold yellow]9[/bold yellow]. Manage Employees: Train and manage your employees to improve their skills and boost dealership performance.")
            menu.add_row("[bold yellow]10[/bold yellow]. Manage Marketing: Launch marketing campaigns to boost your dealership's reputation and attract customers.")
            menu.add_row("[bold yellow]11[/bold yellow]. Manage Finances: Handle your dealership's finances, including loans, investments, and tax payments.")
            menu.add_row("[bold yellow]12[/bold yellow]. Manage Service Department: Offer car maintenance services to customers and generate additional revenue.")
            menu.add_row("[bold yellow]13[/bold yellow]. Save game: Saves your current game state in one of three slots.")
            menu.add_row("[bold yellow]14[/bold yellow]. Load game: Loads a previously saved game from one of three slots.")
            menu.add_row("[bold yellow]15[/bold yellow]. Exit: Exits the game.")
            menu.add_row("[bold yellow]0[/bold yellow]. Return to Main Menu")

            console.print(menu)

            choice = Prompt.ask("\nEnter your choice", choices=["0"])
            if choice == '0':
                break
            else:
                console.print("[red]Invalid choice. Please try again.")
                input("\nPress Enter to return to the user guide...")

if __name__ == "__main__":
    game = CarDealershipSimulator()
    game.main_menu()
