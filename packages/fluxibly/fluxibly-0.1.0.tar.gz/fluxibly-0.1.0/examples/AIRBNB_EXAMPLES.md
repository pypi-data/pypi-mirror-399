# Airbnb Search Examples

This directory contains examples demonstrating the integration of the Airbnb MCP server with the Fluxibly workflow engine.

## Prerequisites

### 1. Install Dependencies

```bash
# Install the Airbnb MCP server globally
npm install -g @openbnb/mcp-server-airbnb

# Verify installation
npx @openbnb/mcp-server-airbnb --version
```

### 2. Configure Environment

Create a `local.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Enable Airbnb MCP Server

The Airbnb MCP server should already be enabled in [config/mcp_servers.yaml](../config/mcp_servers.yaml):

```yaml
airbnb:
  command: "npx"
  args: ["-y", "@openbnb/mcp-server-airbnb"]
  env: {}
  enabled: true
  priority: 1
  description: "Airbnb accommodation search and listing details"
```

## Examples

### Example 1: Tokyo Accommodation Search

**File**: [workflow_airbnb_tokyo.py](workflow_airbnb_tokyo.py)

**Description**: Demonstrates a single search for Airbnb accommodations in Tokyo, Japan for 4 adults from February 20-27, 2025.

**Features**:
- Uses the `travel_assistant` profile
- Stateful conversation (follow-up questions with context)
- Detailed listing information
- Error handling

**Usage**:

```bash
uv run python examples/workflow_airbnb_tokyo.py
```

**Expected Output**:
```
======================================================================
Airbnb Search - Tokyo Accommodation
======================================================================

Search Criteria:
  Location: Tokyo, Japan
  Dates: February 20-27, 2025 (7 nights)
  Guests: 4 adults
======================================================================

Initializing Airbnb MCP server...
✓ Connected to Airbnb MCP server

Query: Find Airbnb accommodations in Tokyo, Japan for 4 adults...
Searching...
----------------------------------------------------------------------

Results:
----------------------------------------------------------------------
[Concise list of top 5 Airbnb options with prices and key features]
----------------------------------------------------------------------
```

### Example 2: Batch Search Across Multiple Cities

**File**: [workflow_airbnb_batch.py](workflow_airbnb_batch.py)

**Description**: Demonstrates batch processing to compare Airbnb accommodations across Tokyo, Osaka, and Kyoto for the same dates.

**Features**:
- Batch execution (parallel searches)
- Stateless vs stateful modes
- Comparative analysis with follow-up questions
- Value-for-money recommendations

**Usage**:

```bash
uv run python examples/workflow_airbnb_batch.py
```

**Expected Output**:
```
======================================================================
Airbnb Batch Search - Compare Multiple Destinations
======================================================================

📍 TOKYO
----------------------------------------------------------------------
[Best Tokyo option with price]
----------------------------------------------------------------------

📍 OSAKA
----------------------------------------------------------------------
[Best Osaka option with price]
----------------------------------------------------------------------

📍 KYOTO
----------------------------------------------------------------------
[Best Kyoto option with price]
----------------------------------------------------------------------

Comparative Analysis (Stateful)
----------------------------------------------------------------------
[Comparison across all cities with value analysis]
----------------------------------------------------------------------
```

## Profile Configuration

The examples use the `travel_assistant` profile defined in [config/profiles/travel_assistant.yaml](../config/profiles/travel_assistant.yaml):

```yaml
profile:
  name: "travel_assistant"
  description: "Specialized in travel planning and accommodation searches via Airbnb"

workflow:
  agent_type: "orchestrator"  # Multi-step planning
  execution_mode: "single"
  stateful: true              # Maintain conversation history

enabled_servers:
  - airbnb

orchestrator:
  model: "gpt-4o"
  temperature: 0.7
  max_mcp_calls: 15
  system_prompt: |
    You are a travel assistant specialized in finding accommodations via Airbnb.
    Provide concise, helpful summaries of search results.
```

## Available Airbnb MCP Tools

The Airbnb MCP server provides the following tools (discovered automatically):

1. **`search_listings`**
   - Search for Airbnb listings by location, dates, guests
   - Parameters: location (string), check_in (date), check_out (date), adults (number), children (number), etc.

2. **`get_listing_details`**
   - Get detailed information about a specific listing
   - Parameters: listing_id (string)

3. **`get_amenities`**
   - List available amenities for filtering
   - No parameters

4. **`search_by_amenities`**
   - Search for listings with specific amenities
   - Parameters: location, dates, guests, amenities (array)

## How It Works

### Parameter Resolution

The orchestrator automatically:

1. **Extracts search criteria** from natural language:
   - "Tokyo, Japan" → location parameter
   - "February 20-27, 2025" → check_in/check_out dates
   - "4 adults" → adults parameter

2. **Generates execution plan**:
   ```json
   [
     {
       "step_id": 1,
       "description": "Search for Tokyo accommodations",
       "tool": "search_listings",
       "tool_args": {
         "location": "Tokyo, Japan",
         "check_in": "2025-02-20",
         "check_out": "2025-02-27",
         "adults": 4
       },
       "dependencies": []
     }
   ]
   ```

3. **Executes tools and synthesizes results** into concise answers

### Stateful Conversations

When `stateful: true` is enabled:

```python
# First query
response1 = await engine.execute("Find accommodations in Tokyo for 4 adults, Feb 20-27")

# Follow-up with context
response2 = await engine.execute("Show me more details about the first option")
# ✓ Agent remembers previous search results
```

### Batch Processing

```python
# Independent searches (preserve_state=False)
results = await engine.execute_batch(
    ["Find Tokyo accommodation", "Find Osaka accommodation"],
    preserve_state=False
)
# Each search is independent, no shared context

# Sequential searches with context (preserve_state=True)
results = await engine.execute_batch(
    ["Find Tokyo accommodation", "Compare with Osaka", "Which is better?"],
    preserve_state=True
)
# Each search builds on previous results
```

## Troubleshooting

### Issue: "Tool 'search_listings' not found"

**Solution**: Ensure the Airbnb MCP server is installed and enabled:

```bash
npm install -g @openbnb/mcp-server-airbnb
```

Check `config/mcp_servers.yaml` has `enabled: true` for airbnb.

### Issue: "No results found"

**Possible Causes**:
- Invalid dates (past dates, check-in after check-out)
- Location not recognized (try more specific: "Shibuya, Tokyo, Japan")
- No availability for those dates/guest count

**Solution**: Try different dates or locations.

### Issue: MCP server connection timeout

**Solution**: Increase timeout in profile:

```yaml
orchestrator:
  mcp_timeout: 60  # Increase to 60 seconds
```

## Advanced Usage

### Custom Search with Specific Amenities

```python
search_query = (
    "Find Airbnb in Tokyo for 4 adults, Feb 20-27, 2025 "
    "with WiFi, kitchen, and washing machine. Budget under $200/night."
)
response = await engine.execute(search_query)
```

### Multi-Step Itinerary Planning

```python
# Create stateful session for multi-day trip planning
engine = WorkflowEngine.from_profile("travel_assistant")
await engine.initialize()

# Day 1-3: Tokyo
tokyo = await engine.execute("Find Tokyo accommodation for 4 adults, Feb 20-23")

# Day 4-7: Kyoto (context preserved)
kyoto = await engine.execute("Now find Kyoto accommodation for the same group, Feb 23-27")

# Compare and decide
comparison = await engine.execute("Compare these two options and recommend the best itinerary")
```

## Next Steps

- Explore other MCP servers: [mcpservers.org](https://mcpservers.org)
- Combine Airbnb with weather MCP for trip planning
- Create custom profiles for different travel styles
- Implement booking workflow with confirmation steps

## References

- [Airbnb MCP Server Documentation](https://mcpservers.org/servers/openbnb-org/mcp-server-airbnb)
- [Fluxibly Workflow Documentation](../docs/workflow.md)
- [Profile Configuration Guide](../docs/profiles.md)
