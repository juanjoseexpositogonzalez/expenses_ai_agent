# OpenAI Function Calling (Tools)

Function calling lets the LLM use external functions to enhance its responses. This lesson covers tool schemas and handling tool calls.


## Why Function Calling Exists

LLMs have knowledge cutoff dates and can't access real-time data:

```
User: "Convert 100 EUR to USD"
LLM: "Based on my training data from 2023, 100 EUR is approximately 108 USD"
     # Wrong! Exchange rates change daily
```

With function calling, the LLM can request current data:

```
User: "Convert 100 EUR to USD"
LLM: [calls convert_currency(100, "EUR", "USD")]
System: [returns 110.50]
LLM: "100 EUR is currently 110.50 USD"
     # Correct! Used real-time API
```


## Tool Schema Format

OpenAI uses a specific JSON format for tool definitions:

```python
CURRENCY_CONVERSION_TOOL = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another using current exchange rates",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The amount to convert"
                },
                "from_currency": {
                    "type": "string",
                    "description": "Source currency code (e.g., EUR, USD)"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target currency code (e.g., EUR, USD)"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    }
}
```


## Handling Tool Calls

The flow for handling tool calls:

```
1. Send message with tools defined
2. LLM may return a tool_call instead of content
3. Execute the tool with provided arguments
4. Send tool result back to LLM
5. LLM generates final response
```

```python
# Step 1: Initial request with tools
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[CURRENCY_CONVERSION_TOOL],
)

# Step 2: Check for tool calls
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        # Step 3: Execute the tool
        args = json.loads(tool_call.function.arguments)
        result = convert_currency(
            Decimal(str(args["amount"])),
            args["from_currency"],
            args["to_currency"],
        )

        # Step 4: Send result back
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result),
        })

    # Step 5: Get final response
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
```


## Datetime Formatter Tool

Another useful tool for our expense tracker:

```python
DATETIME_FORMATTER_TOOL = {
    "type": "function",
    "function": {
        "name": "format_datetime",
        "description": "Format a datetime for display in a specific timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "datetime_str": {
                    "type": "string",
                    "description": "ISO format datetime string"
                },
                "timezone_str": {
                    "type": "string",
                    "description": "Timezone name (e.g., Europe/Madrid, America/New_York)"
                }
            },
            "required": ["datetime_str"]
        }
    }
}
```


## When to Use Tools

**Use tools when:**

- You need real-time data (exchange rates, weather, stock prices)
- The LLM needs to perform calculations precisely
- You want to access external APIs or databases

**Don't use tools when:**

- The LLM already has the knowledge
- Simple text generation is sufficient
- Tool calls would add unnecessary latency


## Tools in Our Project

We define two tools for expense classification:

| Tool | Purpose | When Called |
|------|---------|-------------|
| `convert_currency` | Get current exchange rates | Amount needs conversion |
| `format_datetime` | Format dates for user's timezone | Displaying expense dates |


## Python Comparison

| Manual parsing | Function calling |
|---------------|------------------|
| Regex/string manipulation | Structured JSON arguments |
| Error-prone | Type-safe |
| Hard to maintain | Schema-defined |
| "Parse the response somehow" | `json.loads(tool_call.function.arguments)` |


## Further Reading

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Tools API Reference](https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools)
