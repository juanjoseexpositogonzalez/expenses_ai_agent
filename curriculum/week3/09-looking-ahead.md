# Looking Ahead: Week 4

Congratulations on completing Week 3! You now have a working classification pipeline with CLI.


## What's Next

In Week 4, you will add the Telegram bot interface:

- **Input Preprocessing** - Validate and clean user input
- **Conversation Handlers** - Multi-step bot interactions
- **Human-in-the-Loop** - Let users confirm or change categories
- **Inline Keyboards** - Category selection buttons


## How Week 3 Connects to Week 4

Your ClassificationService will be reused by the Telegram bot:

```
Telegram Message: "Coffee at Starbucks $5.50"
     |
     v
InputPreprocessor (Week 4)
     |
     v
ClassificationService (Week 3)  <-- Reused!
     |
     v
ExpenseCategorizationResponse
     |
     v
InlineKeyboard for category confirmation (Week 4)
     |
     v
User selects category
     |
     v
persist_with_category() (Week 3)  <-- Reused!
```


## HITL in the Telegram Bot

The `persist_with_category()` method you implemented enables HITL:

1. LLM classifies expense (e.g., "Food", 75% confidence)
2. Bot shows inline keyboard with category buttons
3. User taps to confirm or change
4. Bot calls `persist_with_category()` with user's choice


## Prepare for Week 4

Before starting Week 4, make sure you:

1. Have all 30 Week 3 tests passing
2. Understand how ClassificationService works
3. Have a Telegram Bot Token (get one from @BotFather)

See you in Week 4!
