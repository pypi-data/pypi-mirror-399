# AI Conversation History API Documentation

Version: 0.1.0

## Overview

A stateless REST API for managing AI agent conversation history with multi-tenancy support. The API provides endpoints for managing tenants, conversations, and messages with features like auto-sequencing, full-text search, and JSONB metadata storage.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Key Features

- ✅ **Multi-tenancy**: Automatic tenant get-or-create by name
- ✅ **Auto-sequencing**: Messages are automatically sequenced within conversations
- ✅ **Full-text search**: PostgreSQL-powered search across conversations and messages
- ✅ **JSONB metadata**: Flexible metadata storage for conversations and messages
- ✅ **Batch operations**: Create multiple messages atomically
- ✅ **Status management**: Archive/unarchive conversations

## API Conventions

- All timestamps are in UTC (ISO 8601 format)
- Pagination uses `offset` and `limit` parameters
- Metadata fields accept arbitrary JSON objects
- Tenant names are auto-created on first use
- Message sequence numbers are auto-generated if not provided

---

# Endpoints

## Health Check

### Get Health Status

```
GET /health
```

Check if the API is running.

**Response**: `200 OK`

```json
{
  "status": "healthy"
}
```

---

## Tenants

Tenants are automatically created when conversations reference them by name. These endpoints provide read-only access to tenant information.

### List Tenants

```
GET /tenants/
```

Retrieve a paginated list of all tenants.

**Query Parameters**:
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "name": "acme-corp",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "beta-inc",
    "created_at": "2025-01-16T14:20:00Z",
    "updated_at": "2025-01-16T14:20:00Z"
  }
]
```

---

### Get Tenant by ID

```
GET /tenants/{tenant_id}
```

Retrieve a specific tenant by ID.

**Path Parameters**:
- `tenant_id` (integer, required): Tenant ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "name": "acme-corp",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Tenant not found
- `422 Unprocessable Entity`: Invalid ID format

---

### Get Tenant by Name

```
GET /tenants/by-name/{tenant_name}
```

Retrieve a specific tenant by name.

**Path Parameters**:
- `tenant_name` (string, required): Tenant name

**Response**: `200 OK`

```json
{
  "id": 1,
  "name": "acme-corp",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Tenant not found

---

## Conversations

Manage conversations between users and AI agents.

### Create Conversation

```
POST /conversations/
```

Create a new conversation. The tenant is automatically created if it doesn't exist.

**Request Body**:

```json
{
  "tenant_name": "acme-corp",
  "user_id": "user-123",
  "title": "Customer Support Session",
  "agent_identifier": "support-agent-v1",
  "status": "active",
  "metadata": {
    "session_id": "sess-456",
    "custom_field": "custom_value"
  }
}
```

**Fields**:
- `tenant_name` (string, required): Tenant name (min: 1, max: 255). Auto-creates tenant if not exists.
- `user_id` (string, required): User identifier within the tenant (min: 1, max: 255)
- `title` (string, optional): Conversation title or summary (max: 500)
- `agent_identifier` (string, optional): Identifier for the AI agent (max: 255)
- `status` (string, optional): Conversation status - `"active"` or `"archived"` (default: `"active"`)
- `metadata` (object, optional): Agent-specific metadata as JSON object (default: `{}`)

**Response**: `201 Created`

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "active",
  "metadata": {
    "session_id": "sess-456",
    "custom_field": "custom_value"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error (invalid fields, missing required fields, etc.)

---

### Get Conversation by ID

```
GET /conversations/{conversation_id}
```

Retrieve a specific conversation by ID, optionally including messages.

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Query Parameters**:
- `include_messages` (boolean, optional): Include messages in response (default: false)

**Response**: `200 OK`

**Without messages** (`include_messages=false`):

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "active",
  "metadata": {
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**With messages** (`include_messages=true`):

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "active",
  "metadata": {
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "sequence_number": 0,
      "role": "user",
      "content": "Hello, I need help",
      "metadata": {},
      "created_at": "2025-01-15T10:31:00Z",
      "updated_at": "2025-01-15T10:31:00Z"
    },
    {
      "id": 2,
      "conversation_id": 1,
      "sequence_number": 1,
      "role": "assistant",
      "content": "How can I help you?",
      "metadata": {},
      "created_at": "2025-01-15T10:31:05Z",
      "updated_at": "2025-01-15T10:31:05Z"
    }
  ]
}
```

**Error Responses**:
- `404 Not Found`: Conversation not found
- `422 Unprocessable Entity`: Invalid ID format

---

### List Conversations

```
GET /conversations/
```

Retrieve a paginated list of conversations with optional filtering.

**Query Parameters**:
- `tenant_name` (string, optional): Filter by tenant name
- `tenant_id` (integer, optional): Filter by tenant ID
- `user_id` (string, optional): Filter by user ID
- `agent_identifier` (string, optional): Filter by agent identifier
- `status` (string, optional): Filter by status (`"active"` or `"archived"`)
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "tenant_id": 1,
  "user_id": "user-123",
    "agent_identifier": "support-agent-v1",
    "title": "Customer Support Session",
    "status": "active",
    "metadata": {},
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "tenant_id": 1,
  "user_id": "user-123",
    "agent_identifier": "sales-agent-v2",
    "title": "Sales Inquiry",
    "status": "active",
    "metadata": {},
    "created_at": "2025-01-15T11:00:00Z",
    "updated_at": "2025-01-15T11:00:00Z"
  }
]
```

**Example Requests**:

```bash
# Get all conversations for a tenant
GET /conversations/?tenant_name=acme-corp

# Get active conversations only
GET /conversations/?status=active

# Get conversations for specific agent
GET /conversations/?agent_identifier=support-agent-v1

# Pagination
GET /conversations/?offset=20&limit=10
```

---

### Search Conversations

```
GET /conversations/search
```

Search conversations by title or metadata with optional filtering.

**Query Parameters**:
- `q` (string, optional): Search query for title (case-insensitive partial match)
- `metadata_key` (string, optional): Metadata key to search
- `metadata_value` (string, optional): Metadata value to match (requires `metadata_key`)
- `tenant_name` (string, optional): Filter by tenant name
- `tenant_id` (integer, optional): Filter by tenant ID
- `user_id` (string, optional): Filter by user ID
- `agent_identifier` (string, optional): Filter by agent identifier
- `status` (string, optional): Filter by status (`"active"` or `"archived"`)
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "tenant_id": 1,
  "user_id": "user-123",
    "agent_identifier": "support-agent-v1",
    "title": "Customer Support Session",
    "status": "active",
    "metadata": {
      "environment": "production"
    },
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
]
```

**Example Requests**:

```bash
# Search by title
GET /conversations/search?q=support

# Search by metadata field
GET /conversations/search?metadata_key=environment&metadata_value=production

# Combined search
GET /conversations/search?q=customer&status=active&tenant_name=acme-corp
```

---

### Update Conversation

```
PATCH /conversations/{conversation_id}
```

Update a conversation's title, status, or metadata. All fields are optional (partial update).

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Request Body**:

```json
{
  "title": "Updated Title",
  "status": "archived",
  "metadata": {
    "new_field": "new_value"
  }
}
```

**Fields** (all optional):
- `user_id` (string, optional): New user identifier (min: 1, max: 255)
- `title` (string, optional): New conversation title (max: 500)
- `status` (string, optional): New status - `"active"` or `"archived"`
- `metadata` (object, optional): New metadata object (replaces entire metadata field)

**Response**: `200 OK`

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Updated Title",
  "status": "archived",
  "metadata": {
    "new_field": "new_value"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Conversation not found
- `422 Unprocessable Entity`: Validation error

---

### Archive Conversation

```
POST /conversations/{conversation_id}/archive
```

Archive a conversation (sets status to `"archived"`).

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "archived",
  "metadata": {},
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Conversation not found

---

### Unarchive Conversation

```
POST /conversations/{conversation_id}/unarchive
```

Unarchive a conversation (sets status to `"active"`).

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "active",
  "metadata": {},
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T12:15:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Conversation not found

---

### Delete Conversation

```
DELETE /conversations/{conversation_id}
```

Permanently delete a conversation and all its messages (cascade delete).

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Response**: `204 No Content`

**Error Responses**:
- `404 Not Found`: Conversation not found

---

## Messages

Manage messages within conversations. Messages are immutable once created.

### Create Message

```
POST /conversations/{conversation_id}/messages
```

Create a single message in a conversation. Sequence number is auto-generated if not provided.

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Request Body**:

```json
{
  "role": "user",
  "content": "What are your business hours?",
  "sequence_number": 2,
  "metadata": {
    "user_id": "user-123",
    "client_ip": "192.168.1.1"
  }
}
```

**Fields**:
- `role` (string, required): Message role - `"user"`, `"assistant"`, or `"system"`
- `content` (string, required): Message content/text (min: 1)
- `sequence_number` (integer, optional): Order of message in conversation (0-indexed, min: 0). Auto-generated if not provided.
- `metadata` (object, optional): Tool calls, function results, tokens, model info, etc. (default: `{}`)

**Response**: `201 Created`

```json
{
  "id": 3,
  "conversation_id": 1,
  "sequence_number": 2,
  "role": "user",
  "content": "What are your business hours?",
  "metadata": {
    "user_id": "user-123",
    "client_ip": "192.168.1.1"
  },
  "created_at": "2025-01-15T10:32:00Z",
  "updated_at": "2025-01-15T10:32:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Conversation not found
- `409 Conflict`: Duplicate sequence number
- `422 Unprocessable Entity`: Validation error

---

### Create Messages Batch

```
POST /conversations/{conversation_id}/messages/batch
```

Create multiple messages atomically in a conversation. All messages are created in a single transaction.

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Request Body**:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "metadata": {}
    },
    {
      "role": "user",
      "content": "I need information",
      "sequence_number": 5,
      "metadata": {}
    }
  ]
}
```

**Fields**:
- `messages` (array, required): List of messages to create (min: 1 message)
  - Each message has the same fields as single message creation
  - Sequence numbers are auto-generated for messages without explicit `sequence_number`

**Response**: `201 Created`

```json
[
  {
    "id": 10,
    "conversation_id": 1,
    "sequence_number": 0,
    "role": "user",
    "content": "Hello",
    "metadata": {},
    "created_at": "2025-01-15T10:35:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  },
  {
    "id": 11,
    "conversation_id": 1,
    "sequence_number": 1,
    "role": "assistant",
    "content": "Hi! How can I help?",
    "metadata": {},
    "created_at": "2025-01-15T10:35:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  },
  {
    "id": 12,
    "conversation_id": 1,
    "sequence_number": 5,
    "role": "user",
    "content": "I need information",
    "metadata": {},
    "created_at": "2025-01-15T10:35:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  }
]
```

**Error Responses**:
- `404 Not Found`: Conversation not found
- `409 Conflict`: Duplicate sequence number
- `422 Unprocessable Entity`: Validation error

---

### List Messages in Conversation

```
GET /conversations/{conversation_id}/messages
```

Retrieve a paginated list of messages in a conversation, ordered by sequence number.

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Query Parameters**:
- `role` (string, optional): Filter by role (`"user"`, `"assistant"`, or `"system"`)
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "sequence_number": 0,
    "role": "user",
    "content": "Hello",
    "metadata": {},
    "created_at": "2025-01-15T10:31:00Z",
    "updated_at": "2025-01-15T10:31:00Z"
  },
  {
    "id": 2,
    "conversation_id": 1,
    "sequence_number": 1,
    "role": "assistant",
    "content": "Hi! How can I help?",
    "metadata": {},
    "created_at": "2025-01-15T10:31:05Z",
    "updated_at": "2025-01-15T10:31:05Z"
  }
]
```

**Example Requests**:

```bash
# Get all messages
GET /conversations/1/messages

# Get only user messages
GET /conversations/1/messages?role=user

# Pagination
GET /conversations/1/messages?offset=10&limit=20
```

---

### Search Messages in Conversation

```
GET /conversations/{conversation_id}/messages/search
```

Search messages within a specific conversation using PostgreSQL full-text search.

**Path Parameters**:
- `conversation_id` (integer, required): Conversation ID

**Query Parameters**:
- `q` (string, required): Search query for message content (min: 1)
- `role` (string, optional): Filter by role (`"user"`, `"assistant"`, or `"system"`)
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 5,
    "conversation_id": 1,
    "sequence_number": 4,
    "role": "user",
    "content": "Can you help me with Python programming?",
    "metadata": {},
    "created_at": "2025-01-15T10:35:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  }
]
```

**Example Requests**:

```bash
# Search for "python"
GET /conversations/1/messages/search?q=python

# Search with role filter
GET /conversations/1/messages/search?q=error&role=assistant
```

**Error Responses**:
- `422 Unprocessable Entity`: Missing or empty search query

---

### Get Message by ID

```
GET /messages/{message_id}
```

Retrieve a specific message by ID.

**Path Parameters**:
- `message_id` (integer, required): Message ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "conversation_id": 1,
  "sequence_number": 0,
  "role": "user",
  "content": "Hello",
  "metadata": {},
  "created_at": "2025-01-15T10:31:00Z",
  "updated_at": "2025-01-15T10:31:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Message not found
- `422 Unprocessable Entity`: Invalid ID format

---

### Search Messages Globally

```
GET /messages/search
```

Search messages across all conversations using PostgreSQL full-text search.

**Query Parameters**:
- `q` (string, required): Search query for message content (min: 1)
- `conversation_id` (integer, optional): Filter by conversation ID
- `role` (string, optional): Filter by role (`"user"`, `"assistant"`, or `"system"`)
- `offset` (integer, optional): Number of items to skip (default: 0, min: 0)
- `limit` (integer, optional): Number of items to return (default: 100, min: 1, max: 1000)

**Response**: `200 OK`

```json
[
  {
    "id": 5,
    "conversation_id": 1,
    "sequence_number": 4,
    "role": "user",
    "content": "Can you help me with Python programming?",
    "metadata": {},
    "created_at": "2025-01-15T10:35:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  },
  {
    "id": 42,
    "conversation_id": 7,
    "sequence_number": 2,
    "role": "assistant",
    "content": "Sure! Python is a great language for beginners.",
    "metadata": {},
    "created_at": "2025-01-16T09:20:00Z",
    "updated_at": "2025-01-16T09:20:00Z"
  }
]
```

**Example Requests**:

```bash
# Search all messages for "python"
GET /messages/search?q=python

# Search with filters
GET /messages/search?q=error&role=assistant&conversation_id=5
```

**Error Responses**:
- `422 Unprocessable Entity`: Missing or empty search query

---

## Error Responses

The API uses standard HTTP status codes and returns consistent error response formats.

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": [
    {
      "field": "field_name",
      "message": "Specific error message",
      "code": "validation_code"
    }
  ]
}
```

### HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Request succeeded with no response body (e.g., delete)
- `400 Bad Request`: Invalid request format
- `404 Not Found`: Resource not found
- `409 Conflict`: Conflict with existing resource (e.g., duplicate sequence number)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Common Error Examples

**404 Not Found**:

```json
{
  "error": "not_found",
  "message": "Conversation with id 999 not found"
}
```

**409 Conflict** (Duplicate sequence number):

```json
{
  "error": "conflict",
  "message": "Message with sequence_number 0 already exists in conversation 1"
}
```

**422 Validation Error**:

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": [
    {
      "field": "tenant_name",
      "message": "String should have at least 1 character",
      "code": "string_too_short"
    },
    {
      "field": "status",
      "message": "Input should be 'active' or 'archived'",
      "code": "enum"
    }
  ]
}
```

---

## Data Models

### Tenant

```json
{
  "id": 1,
  "name": "acme-corp",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Fields**:
- `id` (integer): Unique identifier
- `name` (string): Tenant name (max: 255, unique)
- `created_at` (string): Creation timestamp (ISO 8601)
- `updated_at` (string): Last update timestamp (ISO 8601)

---

### Conversation

```json
{
  "id": 1,
  "tenant_id": 1,
  "user_id": "user-123",
  "agent_identifier": "support-agent-v1",
  "title": "Customer Support Session",
  "status": "active",
  "metadata": {
    "custom_field": "value"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Fields**:
- `id` (integer): Unique identifier
- `tenant_id` (integer): Tenant ID (foreign key)
- `user_id` (string): User identifier within the tenant (max: 255)
- `agent_identifier` (string, nullable): AI agent identifier (max: 255)
- `title` (string, nullable): Conversation title (max: 500)
- `status` (string): Status - `"active"` or `"archived"` (default: `"active"`)
- `metadata` (object): JSONB metadata object (default: `{}`)
- `created_at` (string): Creation timestamp (ISO 8601)
- `updated_at` (string): Last update timestamp (ISO 8601)

---

### Message

```json
{
  "id": 1,
  "conversation_id": 1,
  "sequence_number": 0,
  "role": "user",
  "content": "Hello, I need help",
  "metadata": {
    "tokens": 5,
    "model": "gpt-4"
  },
  "created_at": "2025-01-15T10:31:00Z",
  "updated_at": "2025-01-15T10:31:00Z"
}
```

**Fields**:
- `id` (integer): Unique identifier
- `conversation_id` (integer): Conversation ID (foreign key)
- `sequence_number` (integer): Order in conversation (0-indexed, unique per conversation)
- `role` (string): Message role - `"user"`, `"assistant"`, or `"system"`
- `content` (string): Message content/text
- `metadata` (object): JSONB metadata (tool calls, tokens, model info, etc., default: `{}`)
- `created_at` (string): Creation timestamp (ISO 8601)
- `updated_at` (string): Last update timestamp (ISO 8601)

---

## Examples

### Complete Workflow Example

```bash
# 1. Create a conversation (auto-creates tenant if needed)
curl -X POST http://localhost:8000/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "acme-corp",
    "title": "Customer Support Chat",
    "agent_identifier": "support-bot-v1",
    "metadata": {"user_id": "user-123"}
  }'

# Response: {"id": 1, "tenant_id": 1,
  "user_id": "user-123", ...}

# 2. Add messages to the conversation
curl -X POST http://localhost:8000/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hello, I need help with my order"
  }'

# 3. Add batch messages
curl -X POST http://localhost:8000/conversations/1/messages/batch \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "assistant", "content": "I can help you with that!"},
      {"role": "user", "content": "My order number is 12345"}
    ]
  }'

# 4. Search messages
curl "http://localhost:8000/conversations/1/messages/search?q=order"

# 5. List all messages
curl "http://localhost:8000/conversations/1/messages?include_messages=true"

# 6. Archive conversation
curl -X POST http://localhost:8000/conversations/1/archive

# 7. Search across all conversations
curl "http://localhost:8000/conversations/search?q=support&status=active"
```

---

## Notes

- **Idempotency**: POST requests are not idempotent. Creating the same resource twice will create duplicates (except for duplicate sequence numbers, which will return 409).
- **Immutability**: Messages cannot be edited or updated once created. Only conversations can be updated.
- **Cascading Deletes**: Deleting a conversation deletes all associated messages.
- **Auto-sequencing**: If you don't provide `sequence_number` when creating messages, they will be auto-assigned starting from the next available number.
- **Full-Text Search**: Uses PostgreSQL's full-text search with GIN indexes for optimal performance. Supports stemming and stop words.
- **Metadata**: Both conversations and messages support arbitrary JSON metadata. Use this for storing custom fields, tool calls, token counts, model information, etc.

---

## Rate Limits

Currently, there are no rate limits implemented. This should be added in production environments.

---

## Authentication

Currently, there is no authentication. All endpoints are public. Authentication should be added before deploying to production.

---

## Versioning

Currently, the API does not use versioning in the URL path. Future versions may introduce versioning such as `/v1/`, `/v2/`, etc.
