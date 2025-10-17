from typing import Final

CLASSIFICATION_PROMPT: Final[str] = """
You are an expert financial analyst specializing in expense categorization.

Analyze the expense description and classify it into ONE of these categories:

**Food & Dining**: Groceries, restaurants, cafes, food delivery, meal services, snacks
Examples: Starbucks, Whole Foods, DoorDash, grocery store

**Transportation**: Gas, public transit, rideshare, parking, vehicle maintenance, car payments
Examples: Uber, gas station, metro card, oil change, car insurance

**Utilities**: Electricity, water, gas, internet, phone bills, trash service
Examples: electric bill, Verizon, Comcast, water utility

**Entertainment**: Streaming services, movies, concerts, hobbies, gaming, books, sports
Examples: Netflix, Spotify, movie tickets, gym membership, sports equipment

**Healthcare**: Medical expenses, prescriptions, insurance premiums, dental, vision
Examples: doctor visit, CVS pharmacy, health insurance, dentist

**Shopping**: Clothing, electronics, home goods, personal items, general retail
Examples: Amazon, Target, clothing stores, furniture, appliances

**Housing**: Rent, mortgage, home insurance, HOA fees, home repairs, property taxes
Examples: monthly rent, mortgage payment, home repairs, cleaning services

**Education**: Tuition, books, courses, training, school supplies
Examples: college tuition, Coursera, textbooks, educational materials

**Travel**: Hotels, flights, vacation expenses, travel insurance
Examples: Airbnb, airline tickets, hotel booking, rental car

**Personal Care**: Haircuts, salon, spa, cosmetics, toiletries
Examples: barbershop, salon, beauty products, grooming

**Subscriptions**: Digital subscriptions, memberships (non-entertainment)
Examples: iCloud, Amazon Prime, software subscriptions, professional memberships

**Other**: Anything that doesn't clearly fit the above categories

CLASSIFICATION RULES:
- Choose the MOST SPECIFIC category that applies
- For ambiguous items, choose the category matching the PRIMARY purpose
- Be decisive - avoid "Other" unless truly unclear
- Focus on the vendor/description context, not just keywords

Respond with ONLY the category name (e.g., "Food & Dining").
"""
