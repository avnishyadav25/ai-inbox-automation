# System Architecture Documentation

## Overview

The AI Inbox Automation Agent Suite is built on a multi-agent architecture where specialized agents handle different aspects of email processing. The system uses a pipeline approach with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Gmail Inbox                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Fetcher Agent                              │
│  • Gmail API Integration                                         │
│  • Fetch unread emails                                           │
│  • Mark as processed                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Classifier Agent                            │
│  • Category: urgent, important, promotional, etc.                │
│  • Priority: high, medium, low                                   │
│  • Confidence scoring                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Summarizer Agent                            │
│  • Generate concise summary                                      │
│  • Extract key points                                            │
│  • Identify action items                                         │
│  • Analyze sentiment                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Reply Drafter Agent                           │
│  • RAG: Search similar past responses                            │
│  • Generate context-aware reply                                  │
│  • Match tone and style                                          │
│  • Refinement based on feedback                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Human Approval Interface                        │
│  • Review draft                                                  │
│  • Options: Approve / Edit / Skip                                │
│  • Feedback loop for refinement                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Gmail Sender    │                  │ Scheduler Agent  │
│  • Send reply    │                  │ • Schedule       │
│  • Threading     │                  │   follow-up      │
└────────┬─────────┘                  └────────┬─────────┘
         │                                     │
         └────────────────┬────────────────────┘
                          │
                          ▼
         ┌────────────────┴────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────┐            ┌──────────────────┐
│  Vector Store    │            │  Google Sheets   │
│  • ChromaDB      │            │  • Activity log  │
│  • RAG storage   │            │  • Analytics     │
└──────────────────┘            └──────────────────┘
```

## Core Components

### 1. Main Orchestrator (`main.py`)

**Purpose**: Coordinates all agents and manages the email processing pipeline

**Key Methods**:
- `process_emails()`: Main entry point for email processing
- `_process_single_email()`: Processes one email through the pipeline
- `_get_human_approval()`: Handles user interaction for approval
- `_send_reply()`: Sends approved replies
- `check_follow_ups()`: Processes due follow-ups
- `run_continuous()`: Runs automation in continuous mode

**Flow**:
1. Initialize all agents
2. Fetch emails
3. Process each email sequentially
4. Handle approvals
5. Send replies and log
6. Schedule follow-ups

### 2. Agents Layer

#### Fetcher Agent (`agents/fetcher.py`)

**Responsibilities**:
- Authenticate with Gmail API
- Fetch unread emails from inbox
- Mark emails as processed
- Retrieve specific emails by ID

**Key Methods**:
- `fetch_new_emails()`: Returns list of unread email dicts
- `mark_as_processed()`: Marks email as read
- `get_email_by_id()`: Fetches specific email

**Data Structure**:
```python
{
    'id': str,
    'thread_id': str,
    'subject': str,
    'from': str,
    'date': str,
    'body': str,
    'snippet': str
}
```

#### Classifier Agent (`agents/classifier.py`)

**Responsibilities**:
- Categorize emails into types
- Assign priority levels
- Determine if auto-response is appropriate
- Provide confidence scores

**Categories**:
- `urgent`: Time-sensitive, immediate action needed
- `important`: Business-critical, key contacts
- `promotional`: Marketing, advertisements
- `newsletter`: Subscriptions, updates
- `spam`: Unwanted messages
- `general`: Everything else

**Priority Levels**:
- `high`: Action within 24h
- `medium`: Action within a week
- `low`: FYI, no action needed

**Key Methods**:
- `classify_email()`: Returns classification dict
- `should_auto_respond()`: Boolean decision
- `get_priority_score()`: Numeric score for sorting

**Output Structure**:
```python
{
    'category': str,
    'priority': str,
    'confidence': float,
    'reasoning': str
}
```

#### Summarizer Agent (`agents/summarizer.py`)

**Responsibilities**:
- Generate concise summaries
- Extract key points
- Identify action items
- Analyze sentiment

**Key Methods**:
- `summarize_email()`: Returns summary dict
- `extract_sender_info()`: Parses sender details

**Output Structure**:
```python
{
    'summary': str,
    'key_points': List[str],
    'action_items': List[str],
    'sentiment': str  # positive, neutral, negative, urgent
}
```

#### Reply Drafter Agent (`agents/reply_drafter.py`)

**Responsibilities**:
- Search similar past responses (RAG)
- Generate context-aware replies
- Match tone to incoming email
- Refine based on feedback

**Key Methods**:
- `draft_reply()`: Generates initial draft
- `refine_reply()`: Improves based on feedback
- `_format_rag_context()`: Formats similar responses
- `_extract_sender_name()`: Gets sender details

**RAG Pipeline**:
1. Query vector store for similar emails
2. Include top 3 similar responses as context
3. Generate reply using LLM with context
4. Return structured response

**Output Structure**:
```python
{
    'subject': str,
    'body': str,
    'tone': str,  # formal, professional, casual, friendly
    'confidence': float
}
```

#### Scheduler Agent (`agents/scheduler.py`)

**Responsibilities**:
- Schedule follow-up reminders
- Track pending follow-ups
- Mark follow-ups as completed
- Provide statistics

**Key Methods**:
- `schedule_follow_up()`: Creates follow-up reminder
- `get_due_follow_ups()`: Returns due items
- `mark_completed()`: Marks as done
- `get_follow_up_stats()`: Returns analytics

**Storage**: JSON file (`data/follow_ups.json`)

### 3. Core Layer

#### Gmail Client (`core/gmail_client.py`)

**Purpose**: Low-level Gmail API wrapper

**Key Methods**:
- `fetch_unread_emails()`: API call to fetch emails
- `send_email()`: API call to send
- `mark_as_read()`: Modify labels
- `_get_email_details()`: Parse email data
- `_get_email_body()`: Extract body from payload

**Authentication Flow**:
1. Check for `token.json`
2. If valid, use existing token
3. If expired, refresh token
4. If no token, run OAuth flow
5. Save token for future use

#### LLM Client (`core/llm_client.py`)

**Purpose**: Unified interface for LLM providers

**Supported Providers**:
- Anthropic Claude (Sonnet 4)
- OpenAI GPT-4 Turbo

**Key Methods**:
- `generate()`: Text completion
- `generate_json()`: Structured JSON output

**Features**:
- Provider abstraction
- Consistent interface
- Error handling
- Temperature control

#### Vector Store (`core/vector_store.py`)

**Purpose**: RAG storage and retrieval

**Technology**: ChromaDB with Sentence Transformers

**Key Methods**:
- `add_email_pair()`: Store email-response pair
- `search_similar_responses()`: Semantic search
- `get_collection_size()`: Stats

**Embedding Model**: `all-MiniLM-L6-v2`

**Storage**: Persistent on disk (`data/vector_store/`)

**RAG Flow**:
1. Encode email body as vector
2. Store with response text and metadata
3. For new emails, encode and search
4. Return top K similar responses
5. Use as context for reply generation

### 4. Utils Layer

#### Logger (`utils/logger.py`)

**Purpose**: Centralized logging

**Features**:
- Console output with colors
- File logging with rotation
- Different log levels
- Timestamped entries

**Log Locations**:
- Console: INFO and above
- File: DEBUG and above
- Rotation: Daily
- Retention: 30 days

#### Sheets Client (`utils/sheets_client.py`)

**Purpose**: Google Sheets integration for logging

**Key Methods**:
- `log_email_activity()`: Log processed email
- `update_reply_status()`: Update after sending
- `_ensure_headers()`: Initialize spreadsheet

**Logged Data**:
- Timestamp
- Email ID, From, Subject
- Category, Priority
- Summary
- Reply status
- Processing time
- Follow-up date

#### Helpers (`utils/helpers.py`)

**Purpose**: Utility functions

**Functions**:
- `format_email_preview()`: Display formatting
- `format_reply_preview()`: Reply display
- `get_priority_emoji()`: Visual indicators
- `get_category_emoji()`: Visual indicators
- `extract_email_address()`: Parse emails

## Data Flow

### Email Processing Pipeline

```
1. FETCH
   Input: None
   Output: List[EmailDict]

2. CLASSIFY
   Input: EmailDict
   Output: ClassificationDict

3. SUMMARIZE
   Input: EmailDict, ClassificationDict
   Output: SummaryDict

4. DRAFT
   Input: EmailDict, ClassificationDict, SummaryDict
   Process: RAG search → LLM generation
   Output: ReplyDict

5. APPROVE
   Input: ReplyDict
   Output: UserDecision (approve/edit/skip)

6. SEND
   Input: EmailDict, ReplyDict
   Side Effects: Email sent, Vector store updated

7. LOG
   Input: All processing data
   Side Effects: Google Sheets updated

8. SCHEDULE
   Input: EmailDict, ClassificationDict
   Side Effects: Follow-up scheduled
```

## Configuration Management

### Environment Variables (`.env`)

**Categories**:
1. **Authentication**: API keys, credentials paths
2. **Processing**: Intervals, limits, thresholds
3. **Storage**: Paths for data and logs
4. **Features**: Approval required, follow-up days

### Settings Class (`core/config.py`)

**Purpose**: Type-safe configuration management

**Features**:
- Pydantic validation
- Default values
- Type checking
- Auto-loading from `.env`

## Security Considerations

### Credential Storage
- Gmail credentials: `credentials.json` (not in git)
- OAuth token: `token.json` (not in git)
- API keys: `.env` file (not in git)

### Data Privacy
- Email content not permanently stored
- Only vector embeddings stored for RAG
- Logs contain metadata only
- Google Sheets controlled by user

### API Security
- OAuth 2.0 for Gmail
- HTTPS for all API calls
- Token refresh handled automatically
- Rate limiting respected

## Performance Optimization

### Processing Speed
- Average: 5-10s per email
- Parallel processing possible for independent operations
- Vector search: O(log n) with HNSW index

### Caching
- Vector embeddings cached
- Token refresh cached
- Gmail API responses not cached (real-time data)

### Scalability
- Handles 50+ emails per batch
- Vector store scales to millions of embeddings
- Stateless design allows horizontal scaling

## Error Handling

### Retry Logic
- Gmail API: Exponential backoff
- LLM API: Single retry with error logging
- Network errors: Graceful degradation

### Fallbacks
- Classification failure → Default to "general" + "medium"
- Summarization failure → Use email snippet
- RAG failure → Generate without context
- Sheets logging failure → Log locally only

### Monitoring
- All operations logged
- Errors captured with context
- Daily log rotation
- Stats dashboard available

## Extension Points

### Adding New Agents
1. Create agent class in `agents/`
2. Implement required methods
3. Register in orchestrator
4. Update pipeline flow

### Custom Classifications
1. Modify `ClassifierAgent.classify_email()`
2. Update prompt with new categories
3. Adjust decision logic

### Alternative LLM Providers
1. Add provider to `LLMClient.__init__()`
2. Implement generation methods
3. Update config options

### Additional Integrations
1. Create client in `utils/` or `core/`
2. Add to orchestrator
3. Update logging/monitoring

## Testing Strategy

### Unit Tests
- Each agent independently
- Mock external APIs
- Test edge cases

### Integration Tests
- Full pipeline with test emails
- Gmail API sandbox
- Vector store operations

### End-to-End Tests
- Real Gmail account (test)
- Manual review of outputs
- Performance benchmarks

## Deployment Options

### Local
- Run on personal machine
- Manual start/stop
- Development and testing

### Server
- Deploy to cloud VM
- Systemd service
- Continuous operation

### Docker
- Containerized deployment
- Easy scaling
- Environment isolation

### Serverless
- Cloud Functions/Lambda
- Event-driven triggers
- Cost-effective for low volume

---

This architecture provides a flexible, scalable foundation for intelligent inbox automation while maintaining simplicity and maintainability.
