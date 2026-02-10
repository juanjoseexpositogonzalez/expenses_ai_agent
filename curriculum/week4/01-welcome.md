# Welcome to Week 4: Telegram Integration

Welcome to Week 4! This week you will build a Telegram bot interface for your expense classification agent. You will learn how to validate user input, create multi-step conversation flows, implement human-in-the-loop confirmation, and build interactive inline keyboards. By the end of this week, users can track expenses from their mobile device with AI-powered classification and manual override capabilities.


## What You'll Learn

Week 4 introduces these essential patterns:

- **Input Preprocessing** - Validate, sanitize, and normalize user input before LLM processing
- **Conversation Handlers** - Build multi-step bot interactions with state management
- **Human-in-the-Loop (HITL)** - Let users confirm or override AI classifications
- **Inline Keyboards** - Create interactive buttons for category selection


## The Mental Model Shift

**Week 3 mindset:** "The CLI is the interface - users type commands, we return results"

**Week 4 mindset:** "The bot is a conversation - users interact through messages and buttons, with AI suggestions they can accept or override"

Think of the CLI as a vending machine: insert a command, get a result. The Telegram bot is more like a helpful assistant at a store. You describe what you need, the assistant makes a suggestion, and you confirm or ask for something different. This conversational pattern requires state management (remembering what the user said) and graceful handling of unexpected inputs.


## What Success Looks Like

By the end of this week, your bot handles this conversation:

```
User: Coffee at Starbucks $5.50

Bot: Classified as Food (95% confidence)
     Amount: $5.50 USD

     [>> Food <<] [Transport] [Entertainment]
     [Shopping]   [Health]    [Bills]

User: (taps Food button)

Bot: Saved! Expense recorded as Food.
```

The bot also supports currency preferences:

```
User: /currency

Bot: Select your preferred currency:
     [EUR] [USD] [GBP]
     [JPY] [CHF] [CAD]

User: (taps EUR)

Bot: Currency preference saved as EUR.
```


## Why Telegram for AI Agents?

Telegram provides an ideal platform for AI agents because it offers:

1. **Ubiquitous Access** - Users can interact from any device without installing a custom app
2. **Rich Interactions** - Inline keyboards enable structured user feedback
3. **Asynchronous by Design** - The async API matches Python's async/await patterns
4. **Zero Deployment Friction** - No app store approval, instant availability

For expense tracking specifically, Telegram lets users capture expenses in real-time - at the coffee shop, in the taxi, at the restaurant - when the context is fresh.


## Why Human-in-the-Loop Matters

AI classification is not perfect. Even the best models make mistakes:

```
"Uber to airport" -> Transport (Correct)
"Uber Eats dinner" -> Transport (Wrong! Should be Food)
```

Human-in-the-loop solves this by:

1. **Improving Accuracy** - Human confirmation catches AI errors
2. **Building Trust** - Users feel in control of their data
3. **Collecting Feedback** - Corrections can improve future models
4. **Handling Edge Cases** - Ambiguous expenses get human judgment

The pattern is simple: AI suggests, human confirms. When confidence is low, the keyboard makes it easy to select the correct category.


## Architecture: Week 4's Place

```
+------------------------------------------------------------------+
|                    WEEK 4: TELEGRAM INTEGRATION                   |
+------------------------------------------------------------------+

    Telegram Message: "Coffee at Starbucks $5.50"
                              |
                              v
                    +-------------------+
                    | InputPreprocessor |  <- Validate & sanitize
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Classification-   |  <- Week 3 service (reused)
                    | Service           |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | InlineKeyboard    |  <- Category buttons
                    +-------------------+
                              |
                              v
                    User taps category button
                              |
                              v
                    +-------------------+
                    | persist_with_     |  <- Week 3 method (reused)
                    | category()        |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Confirmation      |
                    | Message           |
                    +-------------------+
```


## Technical Milestones

By the end of Week 4, you'll have:

- [ ] `InputPreprocessor` with validation, XSS protection, currency normalization
- [ ] `PreprocessingResult` dataclass with `is_valid`, `text`, `warnings`, `error`
- [ ] `build_category_confirmation_keyboard()` with highlighted suggestion
- [ ] `build_currency_selection_keyboard()` for user preferences
- [ ] `ExpenseConversationHandler` with multi-step flow
- [ ] `CurrencyHandler` for preference management
- [ ] Custom exceptions: `TelegramBotError`, `InvalidInputError`, `ClassificationError`
- [ ] All 33 tests passing


## Ready?

This week transforms your expense agent from a command-line tool into an interactive assistant. The ClassificationService and persist_with_category() method from Week 3 will be reused - you are adding a new interface layer, not rewriting the core logic.

Let's start by reviewing the Week 3 components you'll build upon.
