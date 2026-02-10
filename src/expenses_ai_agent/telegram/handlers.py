import logging
from decimal import Decimal

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from sqlmodel import Session, create_engine

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.storage.repo import (
    DBCategoryRepo,
    DBExpenseRepo,
    DBUserPreferenceRepo,
)
from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    CURRENCY_CALLBACK_PREFIX,
    CURRENCY_SYMBOLS,
    build_category_confirmation_keyboard,
    build_currency_selection_keyboard,
)
from expenses_ai_agent.utils.currency import convert_currency

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_CONFIRMATION = 0


# ------------------------------------------------------------------
# Simple command handlers
# ------------------------------------------------------------------


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    welcome = (
        "Welcome to Expenses AI Agent!\n\n"
        "I can help you track your expenses using AI-powered categorization.\n\n"
        "How to use:\n"
        "1. Send me an expense description (e.g. 'Coffee at Starbucks $5.50')\n"
        "2. I'll analyze it and suggest a category\n"
        "3. Confirm or choose a different category\n"
        "4. Your expense is saved!\n\n"
        "Commands:\n"
        "/help     - Show this help message\n"
        "/currency - Set your preferred display currency\n"
        "/cancel   - Cancel the current operation"
    )
    await update.message.reply_text(welcome)  # type: ignore[union-attr]


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show usage instructions."""
    help_text = (
        "Expenses AI Agent - Help\n\n"
        "Recording an expense:\n"
        "Simply send a text message describing your expense. Include:\n"
        "- Amount (with or without currency symbol)\n"
        "- Description of what you bought\n\n"
        "Examples:\n"
        "  Coffee at Starbucks $5.50\n"
        "  Uber ride to airport 25 EUR\n"
        "  Monthly Netflix subscription 15.99\n"
        "  Groceries at Whole Foods $87.32\n\n"
        "Commands:\n"
        "/start    - Introduction\n"
        "/help     - This help message\n"
        "/currency - Set your preferred display currency\n"
        "/cancel   - Cancel current operation"
    )
    await update.message.reply_text(help_text)  # type: ignore[union-attr]


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current conversation."""
    context.user_data.clear()  # type: ignore[union-attr]
    await update.message.reply_text(  # type: ignore[union-attr]
        "Operation cancelled. Send me an expense anytime!"
    )
    return ConversationHandler.END


# ------------------------------------------------------------------
# Currency command handler
# ------------------------------------------------------------------


class CurrencyHandler:
    """Handles the /currency command for setting preferred display currency."""

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    async def currency_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Show currency selection keyboard."""
        user = update.effective_user
        if not user:
            return

        # Get current preference
        engine = create_engine(self.db_url)
        with Session(engine) as session:
            repo = DBUserPreferenceRepo(self.db_url, session=session)
            pref = repo.get_by_user_id(user.id)
            current_currency = pref.preferred_currency if pref else Currency.EUR

        keyboard = build_currency_selection_keyboard(current_currency)

        await update.message.reply_text(  # type: ignore[union-attr]
            f"Select your preferred display currency.\n"
            f"Current: {CURRENCY_SYMBOLS.get(current_currency, '')} {current_currency.value}",
            reply_markup=keyboard,
        )

    async def handle_currency_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle currency selection callback."""
        query = update.callback_query
        assert query is not None  # noqa: S101
        await query.answer()

        callback_data: str = query.data or ""
        if not callback_data.startswith(CURRENCY_CALLBACK_PREFIX):
            return

        currency_value = callback_data[len(CURRENCY_CALLBACK_PREFIX) :]

        # Validate currency
        try:
            selected_currency = Currency(currency_value)
        except ValueError:
            await query.edit_message_text("Invalid currency selection.")
            return

        user = update.effective_user
        if not user:
            await query.edit_message_text("Could not identify user.")
            return

        # Save preference
        engine = create_engine(self.db_url)
        with Session(engine) as session:
            repo = DBUserPreferenceRepo(self.db_url, session=session)
            repo.upsert(user.id, selected_currency)

        symbol = CURRENCY_SYMBOLS.get(selected_currency, "")
        await query.edit_message_text(
            f"✅ Preferred currency set to {symbol} {selected_currency.value}\n\n"
            "All expenses will now be displayed in this currency."
        )


# ------------------------------------------------------------------
# Conversation handler class
# ------------------------------------------------------------------


class ExpenseConversationHandler:
    """Manages the expense-recording conversation flow.

    States:
        Entry -> handle_expense_text -> WAITING_FOR_CONFIRMATION
        WAITING_FOR_CONFIRMATION -> handle_category_selection -> END
    """

    def __init__(
        self,
        db_url: str,
        openai_api_key: str,
        model: str = "gpt-4.1-nano-2025-04-14",
    ) -> None:
        self.db_url = db_url
        self.openai_api_key = openai_api_key
        self.model = model
        self.preprocessor = InputPreprocessor()

    def build(self) -> ConversationHandler:
        """Build and return the ConversationHandler."""
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handle_expense_text,
                )
            ],
            states={
                WAITING_FOR_CONFIRMATION: [
                    CallbackQueryHandler(self.handle_category_selection),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)],
            name="expense_conversation",
            persistent=False,
        )

    # ------------------------------------------------------------------
    # Step 1: receive text -> classify -> present keyboard
    # ------------------------------------------------------------------

    async def handle_expense_text(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        """Preprocess and classify an expense, then ask for confirmation."""
        message = update.message
        assert message is not None  # noqa: S101
        user = update.effective_user
        text = message.text or ""

        logger.info(
            "User %s sent expense: %s",
            user.id if user else "unknown",
            text[:80],
        )

        # 1. Preprocess
        result = self.preprocessor.preprocess(text)
        if not result.is_valid:
            errors = "\n".join(result.validation_errors)
            await message.reply_text(f"Invalid input:\n{errors}")
            return ConversationHandler.END

        if result.warnings:
            await message.reply_text("Note: " + "; ".join(result.warnings))

        # 2. Show processing indicator
        processing_msg = await message.reply_text("Analyzing your expense...")

        # 3. Classify
        try:
            assistant = self._build_assistant()
            service = ClassificationService(assistant=assistant)
            classification = service.classify(
                expense_description=result.cleaned_text,
                persist=False,
            )
        except Exception:
            logger.exception("Classification failed")
            await processing_msg.edit_text(
                "Sorry, I couldn't classify your expense. Please try again."
            )
            return ConversationHandler.END

        # 4. Delete processing message
        await processing_msg.delete()

        # 5. Store in context for the next step
        context.user_data["expense_description"] = result.cleaned_text  # type: ignore[index]
        context.user_data["llm_response"] = classification.response  # type: ignore[index]

        # 6. Build confirmation message + keyboard
        resp = classification.response
        confidence_icon = (
            "\U0001f7e2"
            if resp.confidence > 0.8
            else "\U0001f7e1"
            if resp.confidence > 0.5
            else "\U0001f534"
        )

        # Get user's preferred currency
        preferred_currency = Currency.EUR
        if user:
            engine = create_engine(self.db_url)
            with Session(engine) as session:
                pref_repo = DBUserPreferenceRepo(self.db_url, session=session)
                pref = pref_repo.get_by_user_id(user.id)
                if pref:
                    preferred_currency = pref.preferred_currency

        # Build amount string with optional conversion
        amount_str = self._format_amount_with_conversion(
            amount=resp.total_amount,
            expense_currency=resp.currency,
            preferred_currency=preferred_currency,
        )

        confirmation_text = (
            "💰 Expense Classification\n\n"
            f"Amount: {amount_str}\n"
            f"Suggested Category: {resp.category}\n"
            f"{confidence_icon} Confidence: {resp.confidence:.0%}\n"
        )
        if resp.comments:
            confirmation_text += f"\n{resp.comments}\n"
        confirmation_text += "\nPlease confirm or choose a different category:"

        keyboard = build_category_confirmation_keyboard(
            suggested_category=resp.category,
        )

        await message.reply_text(text=confirmation_text, reply_markup=keyboard)
        return WAITING_FOR_CONFIRMATION

    # ------------------------------------------------------------------
    # Step 2: user picks a category -> persist -> confirm
    # ------------------------------------------------------------------

    async def handle_category_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        """Persist the expense with the user-selected category."""
        query = update.callback_query
        assert query is not None  # noqa: S101
        await query.answer()

        callback_data: str = query.data or ""
        if not callback_data.startswith(CATEGORY_CALLBACK_PREFIX):
            await query.edit_message_text("Invalid selection. Please try again.")
            return ConversationHandler.END

        selected_category = callback_data[len(CATEGORY_CALLBACK_PREFIX) :]

        expense_description: str | None = context.user_data.get("expense_description")  # type: ignore[union-attr]
        llm_response: ExpenseCategorizationResponse | None = context.user_data.get(
            "llm_response"
        )  # type: ignore[union-attr]

        if not expense_description or llm_response is None:
            await query.edit_message_text(
                "Session expired. Please send your expense again."
            )
            return ConversationHandler.END

        user = update.effective_user
        telegram_user_id = user.id if user else None
        logger.info(
            "User %s selected category: %s", telegram_user_id, selected_category
        )

        try:
            engine = create_engine(self.db_url)
            with Session(engine) as session:
                category_repo = DBCategoryRepo(self.db_url, session=session)
                expense_repo = DBExpenseRepo(self.db_url, session=session)

                service = ClassificationService(
                    assistant=self._build_assistant(),
                    category_repo=category_repo,
                    expense_repo=expense_repo,
                )

                result = service.persist_with_category(
                    expense_description=expense_description,
                    llm_response=llm_response,
                    selected_category=selected_category,
                    telegram_user_id=telegram_user_id,
                )

                resp = result.response

                # Get user's preferred currency for display
                preferred_currency = Currency.EUR
                if telegram_user_id:
                    pref_repo = DBUserPreferenceRepo(self.db_url, session=session)
                    pref = pref_repo.get_by_user_id(telegram_user_id)
                    if pref:
                        preferred_currency = pref.preferred_currency

            amount_str = self._format_amount_with_conversion(
                amount=resp.total_amount,
                expense_currency=resp.currency,
                preferred_currency=preferred_currency,
            )

            success_text = (
                "✅ Expense saved!\n\n"
                f"Amount: {amount_str}\n"
                f"Category: {resp.category}\n"
                f"Description: {expense_description}\n\n"
                "Send another expense to record it, or use /cancel to stop."
            )
            await query.edit_message_text(success_text)

        except Exception:
            logger.exception("Error persisting expense")
            await query.edit_message_text(
                "Sorry, I couldn't save your expense. Please try again."
            )
        finally:
            context.user_data.clear()  # type: ignore[union-attr]

        return ConversationHandler.END

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_assistant(self) -> OpenAIAssistant:
        return OpenAIAssistant(
            provider=LLMProvider.OPENAI,
            api_key=self.openai_api_key,
            model=self.model,
            max_response_tokens=500,
            temperature=0.3,
            top_p=1.0,
            structured_output=ExpenseCategorizationResponse,
        )  # type: ignore[return-value]

    def _format_amount_with_conversion(
        self,
        amount: "Decimal",
        expense_currency: Currency,
        preferred_currency: Currency,
    ) -> str:
        """Format amount with optional currency conversion.

        Args:
            amount: The expense amount.
            expense_currency: The original expense currency.
            preferred_currency: The user's preferred display currency.

        Returns:
            Formatted string like "$5.50 USD" or "$5.50 USD (≈ €5.20 EUR)".
        """
        from decimal import Decimal

        original_symbol = CURRENCY_SYMBOLS.get(expense_currency, "")
        original_str = f"{original_symbol}{amount} {expense_currency.value}"

        if expense_currency == preferred_currency:
            return original_str

        # Try to convert
        try:
            converted = convert_currency(
                amount=Decimal(str(amount)),
                from_currency=expense_currency,
                to_currency=preferred_currency,
            )
            pref_symbol = CURRENCY_SYMBOLS.get(preferred_currency, "")
            return f"{original_str} (≈ {pref_symbol}{converted:.2f} {preferred_currency.value})"
        except Exception:
            logger.warning(
                "Currency conversion failed from %s to %s",
                expense_currency,
                preferred_currency,
            )
            return original_str
