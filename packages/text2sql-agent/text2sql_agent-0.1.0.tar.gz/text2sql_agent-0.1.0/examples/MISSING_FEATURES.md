# Missing Features: Medical Agent → Generic Toolkit

This document lists key features from `text_to_sql_agent.py` that are **missing** from `text_to_sql/agent.py`.

---

## 🔴 Critical Missing Features

### 1. **PostgreSQL/JSONB-Specific SQL Rules**

The medical agent has extensive PostgreSQL and JSONB-specific rules that are **completely missing** from the generic toolkit:

#### **JSONB Operator Rules:**
- ✅ **Medical Agent Has:**
  - Detailed rules for `->` vs `->>` operators
  - Rules about never chaining `->` after `->>`
  - Examples of correct JSONB path navigation
  - Rules for casting TEXT to JSONB before using JSON operators

- ❌ **Generic Toolkit Has:**
  - Only generic "avoid database-specific syntax" rule
  - No JSONB-specific guidance
  - Actually discourages PostgreSQL syntax (says to use CAST instead of `::`)

**Example from Medical Agent:**
```
- Use -> to access objects or arrays while keeping JSON/JSONB type
- Use ->> only for the final extraction to get text values
- CRITICAL: Never chain -> or ->> after a ->> operator
- WRONG: content::jsonb -> 'name' -> 0 ->> 'given' -> 0
- CORRECT: content::jsonb -> 'name' -> 0 -> 'given' ->> 0
```

#### **Array Handling Rules:**
- ✅ **Medical Agent Has:**
  - Rules for using `ANY` operator for array matching
  - Rules for using `EXISTS` with `unnest()` in subqueries
  - Avoids set-returning functions in WHERE clause

- ❌ **Generic Toolkit Has:**
  - No array-specific rules
  - Generic "avoid database-specific syntax" which would prevent these patterns

**Example from Medical Agent:**
```
- 'value' = ANY(array_column), for exact matches
- EXISTS (
    SELECT 1 FROM unnest(array_column) AS element 
    WHERE lower(element) ILIKE '%value%'
  ), for case-insensitive matches
```

#### **Type Casting Rules:**
- ✅ **Medical Agent Has:**
  - UUID casting rules (`::uuid`, `::text`)
  - Performance-aware casting (cast extracted string to UUID, not UUID to text)
  - Rules for JOIN type compatibility

- ❌ **Generic Toolkit Has:**
  - Generic "verify data types match" but no specific guidance

**Example from Medical Agent:**
```
-- Good: JOIN "Condition" c ON p.id = REPLACE(c.subject, 'Patient/', '')::uuid
-- Bad: JOIN "Condition" c ON p.id::text = REPLACE(c.subject, 'Patient/', '')
```

---

### 2. **Database-Specific Schema Knowledge**

- ✅ **Medical Agent Has:**
  - Hardcoded knowledge about `Condition` table structure
  - Hardcoded knowledge about `Patient` table structure
  - Common query patterns for medical data
  - Specific column naming patterns (double underscores)

- ❌ **Generic Toolkit Has:**
  - No database-specific schema knowledge
  - Relies entirely on schema inspection tools

**Example from Medical Agent:**
```
### Condition Table Structure:
- Primary columns: "id", "subject", "content" (JSONB)
- "subject" contains patient references like "Patient/uuid"
- "content" is JSONB containing: code object with coding array

### Common Query Patterns:
1. Find conditions by text: content::jsonb #>> path_to_code_text ILIKE '%search%'
2. Extract patient ID: REPLACE("subject", 'Patient/', '')::uuid
3. Join Patient-Condition: p.id = REPLACE(c."subject", 'Patient/', '')::uuid
```

---

### 3. **Double Underscore Column Naming Pattern**

- ✅ **Medical Agent Has:**
  - Specific rule about double underscore naming (`__code`, `__status`, `__category`)
  - Error recovery suggestion to try double underscore prefix

- ❌ **Generic Toolkit Has:**
  - No knowledge of this naming pattern
  - Generic "check for typos" error handling

**Example from Medical Agent:**
```
CRITICAL: Many columns use double underscore naming (e.g., __code, __status, __category). 
If you get "column does not exist" errors, try the column name with double underscores (__) prefix.
```

---

### 4. **PostgreSQL-Specific Syntax Support**

- ✅ **Medical Agent Has:**
  - Embraces PostgreSQL syntax (`::`, `ILIKE`, `->`, `->>`)
  - PostgreSQL-specific type casting
  - PostgreSQL array operators

- ❌ **Generic Toolkit Has:**
  - **Actively discourages** PostgreSQL syntax
  - Says to use `CAST(column AS type)` instead of `column::type`
  - Says to use `LOWER(column) LIKE` instead of `ILIKE`
  - This would break queries for PostgreSQL databases with JSONB

**Generic Toolkit Rule (Problematic for PostgreSQL):**
```
2. **Write Standard SQL** (compatible with multiple databases):
   - Use CAST(column AS type) instead of column::type
   - Use LOWER(column) LIKE '%value%' instead of ILIKE
   - Avoid database-specific array or JSON syntax
```

---

### 5. **Clinical Context Rules**

- ✅ **Medical Agent Has:**
  - Domain-specific conversation handling
  - Rules for interpreting vague medical terms
  - Follow-up question handling for medical context

- ❌ **Generic Toolkit Has:**
  - Generic conversation context (works for any domain)
  - No medical-specific interpretation rules

**Example from Medical Agent:**
```
## CLINICAL CONTEXT RULES:
- If the user mentions vague terms like "that patient", "those results", 
  or "previous symptoms", use the previous conversation or SQL query to interpret context
- When asked follow-up questions, modify the prior SQL query logically
- Prioritize structured medical understanding (symptoms, diagnosis codes, medication names)
```

---

### 6. **Healthcare Awareness**

- ✅ **Medical Agent Has:**
  - Clinical terminology awareness
  - Patient identifier handling rules
  - Temporal context for medical queries

- ❌ **Generic Toolkit Has:**
  - Generic domain context (works for any domain)
  - No medical-specific awareness

**Example from Medical Agent:**
```
## HEALTHCARE AWARENESS:
- Use clinical terms appropriately
- Recognize temporal context like "last week", "past 30 days", "most recent", "since diagnosis"
- Be cautious with patient identifiers and always refer to them as "the patient"
```

---

### 7. **ILIKE with JSONB Rules**

- ✅ **Medical Agent Has:**
  - Specific rule about casting JSONB to text before ILIKE
  - Example: `LOWER(json_column_name::text) ILIKE '%hypertension%'`

- ❌ **Generic Toolkit Has:**
  - No JSONB-specific ILIKE rules
  - Actually discourages ILIKE (says to use LOWER + LIKE)

**Example from Medical Agent:**
```
- When applying ILIKE to a jsonb column, you must cast the entire field to text using ::text
- Example: LOWER(json_column_name::text) ILIKE '%hypertension%'
- Do NOT write: LOWER(json_column_name) ILIKE '%value%'
```

---

### 8. **ORDER BY with Column Aliases**

- ✅ **Medical Agent Has:**
  - Rule about using alias names in ORDER BY
  - Warning about not using table-prefixed names for JSON-derived aliases

- ❌ **Generic Toolkit Has:**
  - No specific ORDER BY rules

**Example from Medical Agent:**
```
- When using ORDER BY with column aliases, always reference the alias name defined in SELECT
- Do not use expressions or table-prefixed names (p.last_name) if the alias is derived from a JSON expression
```

---

## 📊 Summary Table

| Feature | Medical Agent | Generic Toolkit | Impact |
|---------|--------------|-----------------|--------|
| **PostgreSQL/JSONB Rules** | ✅ Extensive | ❌ None (discourages) | 🔴 **CRITICAL** - Breaks PostgreSQL queries |
| **JSONB Operator Patterns** | ✅ Detailed | ❌ None | 🔴 **CRITICAL** - Can't query JSONB properly |
| **Array Handling** | ✅ ANY/EXISTS patterns | ❌ None | 🔴 **CRITICAL** - Can't query arrays |
| **Type Casting Rules** | ✅ UUID/Text casting | ⚠️ Generic only | 🟡 **HIGH** - Performance issues |
| **Double Underscore Pattern** | ✅ Yes | ❌ No | 🟡 **HIGH** - Error recovery missing |
| **Database Schema Knowledge** | ✅ Hardcoded | ❌ None | 🟡 **MEDIUM** - Less efficient |
| **Clinical Context** | ✅ Yes | ⚠️ Generic only | 🟢 **LOW** - Domain-specific |
| **Healthcare Awareness** | ✅ Yes | ⚠️ Generic only | 🟢 **LOW** - Domain-specific |

---

## 🎯 Recommendations

### Option 1: Add PostgreSQL/JSONB Support to Generic Toolkit
Create a **database-specific prompt extension** system:

```python
def get_postgresql_jsonb_rules() -> str:
    """PostgreSQL/JSONB-specific rules"""
    return """
    ## POSTGRESQL/JSONB SPECIFIC RULES:
    [All the JSONB rules from medical agent]
    """

# In agent.py
if self.db._engine.dialect.name == 'postgresql':
    postgresql_rules = get_postgresql_jsonb_rules()
    # Add to prompt
```

### Option 2: Create Database-Specific Prompt Modules
Extend the prompts module to support database-specific rules:

```python
# prompts/postgresql.py
def get_postgresql_specific_rules():
    """PostgreSQL-specific SQL rules"""
    ...

# prompts/mysql.py  
def get_mysql_specific_rules():
    """MySQL-specific SQL rules"""
    ...
```

### Option 3: Domain-Specific Extensions
Allow domain-specific prompt extensions:

```python
# prompts/medical.py
def get_medical_domain_rules():
    """Medical domain-specific rules"""
    ...

# In agent.py
if domain_context == "medical records":
    medical_rules = get_medical_domain_rules()
    # Add to prompt
```

### Option 4: Keep Medical Agent for PostgreSQL/Medical Use Cases
- Use `text_to_sql` for generic, multi-database scenarios
- Keep `text_to_sql_agent.py` for PostgreSQL/JSONB/Medical-specific use cases
- Both can coexist

---

## ⚠️ Critical Issue

The **biggest problem** is that the generic toolkit **actively discourages** PostgreSQL syntax, which would **break** queries for PostgreSQL databases with JSONB columns. This is a fundamental incompatibility.

**Current Generic Toolkit Rule:**
```
- Use CAST(column AS type) instead of column::type
- Use LOWER(column) LIKE '%value%' instead of ILIKE
- Avoid database-specific array or JSON syntax
```

**This would break:**
- All JSONB queries (`content::jsonb -> 'field'`)
- All array queries (`'value' = ANY(array_column)`)
- All PostgreSQL-specific type casting (`REPLACE(...)::uuid`)

---

## ✅ Conclusion

The medical agent has **critical PostgreSQL/JSONB-specific features** that are missing from the generic toolkit. The generic toolkit's "standard SQL only" approach would **break** PostgreSQL/JSONB queries.

**Recommendation:** Add database-specific prompt extensions to the generic toolkit, or keep the medical agent for PostgreSQL/JSONB use cases.

