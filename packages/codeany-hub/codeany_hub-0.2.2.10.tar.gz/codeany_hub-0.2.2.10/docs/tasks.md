# Task Management

This guide covers how to manage tasks within a hub using the improved Python SDK. The `TasksClient` provides methods for creating, updating, and managing tasks, statements, and test data.

## Creating a Task

Create a new task with strongly typed arguments for better validation and discoverability.

```python
from codeany_hub import CodeanyClient

client = CodeanyClient()
hub_slug = "my-hub"

task = client.tasks.create(
    hub=hub_slug,
    name="Two Sum",
    time_limit=1000,   # milliseconds
    memory_limit=256,  # megabytes
    type="batch",      # optional, defaults to "batch" ("classic", "interactive", "output-only", "code")
    visibility="private" # optional, defaults to "private"
)

# Available Task Types:
# - "classic" (or "batch"): Standard stdin/stdout tasks
# - "interactive": Tasks where solution interacts with a judge program
# - "output-only": Submission is just the output file
# - "code": Generic code submission task

print(f"Created task: {task.name} (ID: {task.id})")
```

## Task Operations

Basic operations to manage the task lifecycle.

```python
# Rename a task
client.tasks.rename(hub=hub_slug, task_id=task.id, new_name="New Name")

# Toggle visibility (private <-> public)
client.tasks.toggle_visibility(hub=hub_slug, task_id=task.id)

# Delete a task
client.tasks.delete(hub=hub_slug, task_id=task.id)
```

## Managing Statements

Statements can be managed per language. The SDK now enforces consistent naming conventions (e.g., `language` instead of `lang`) to avoid confusion.

### Creating/Updating a Statement

Use `create_statement_language` or `upsert_statement_language` to add content for a specific locale.

```python
# specific language content
content = {
    "title": "Two Sum",
    "legend": "Given an array of integers...",
    "input_format": "The first line contains...",
    "output_format": "Print the indices..."
}

# Create English statement
client.tasks.create_statement_language(
    hub=hub_slug,
    task_id=task.id,
    language="en",
    content=content
)

# Update Azerbaijani statement
client.tasks.upsert_statement_language(
    hub=hub_slug,
    task_id=task.id,
    language="az",
    content={"title": "İki Cəm", "legend": "..."}
)
```

### Retrieving Statements

Fetch statements for a specific language or all available languages.

```python
# Get English statement
statement = client.tasks.get_statement(
    hub=hub_slug, 
    task_id=task.id
)

# List all available statement summaries
summaries = client.tasks.list_statements(hub=hub_slug, task_id=task.id)
for s in summaries:
    print(f"{s.language}: {s.title}")

# Upload an image for use in statements
image_url = client.tasks.upload_statement_image(
    hub=hub_slug,
    task_id=task.id,
    file=open("diagram.png", "rb"),
    content_type="image/png"
)
print(f"Image uploaded: {image_url}")
```

## Updating Limits

Time and memory limits can be updated easily.

```python
limits = client.tasks.update_limits(
    hub=hub_slug,
    task_id=task.id,
    time_limit=2000,
    memory_limit=512
)
print(f"New limits: {limits.time_limit}ms, {limits.memory_limit}MB")
```

## Checkers and Graders

- **Checkers**: Define how outputs are promoted invalid.
- **Graders**: Programs that interact with the user's solution.

Note: `programming_language` is used here to distinguish from natural `language`.

```python
# Update checker
client.tasks.update_checker(
    hub=hub_slug,
    task_id=task.id,
    payload={
        "checker_type": "custom_checker",
        "checker_language": "cpp", # programming language
        "checker": "// C++ checker code"
    }
)

# Available Checker Types:
# - "token_checker": Standard token-based comparison
# - "line_checker": Line-by-line comparison
# - "epsilon_checker": Floating point float comparison (requires 'precision' field)
# - "custom_checker": Custom C++ checker (requires 'checker' and 'checker_language')
```

# Add a grader
client.tasks.add_grader(
    hub=hub_slug,
    task_id=task.id,
    payload={
        "programming_language": "python",
        "code": "print('grader')"
    }
)
```

## Testset Management

You can manage testsets, including uploading test data via zip files.

```python
# Upload a zip file for a specific testset
# usage: client.tasks.upload_testset_zip(hub, task_id, testset_id, zip_path)

with open("tests.zip", "rb") as f:
    client.tasks.upload_testset_zip(
        hub=hub_slug,
        task_id=task.id,
        testset_id=1,
        zip_path=f
    )

```

### Advanced Testset Management

For more granular control over testsets and testcases.

```python
# Create a new empty testset
testset = client.tasks.create_testset(hub=hub_slug, task_id=task.id)

# Upload a single test case (input/output pair)
with open("1.in", "rb") as fin, open("1.out", "rb") as fout:
    client.tasks.upload_single_test(
        hub=hub_slug,
        task_id=task.id,
        testset_id=testset.id,
        input_path=fin,
        answer_path=fout
    )

# Delete a specific testset
client.tasks.delete_testset(hub=hub_slug, task_id=task.id, testset_id=testset.id)
```

### Configuring Testsets

You can update testset properties such as scores.

```python
# Update testset score
client.tasks.update_testset(
    hub=hub_slug,
    task_id=task.id,
    testset_id=1,
    score=10,        # Points for this testset
    test_count=5     # Expected number of tests (optional)
)
```

## Managing Examples

You can set or append examples that are shown in the problem statement.

```python
# Set all examples at once
client.tasks.set_examples(
    hub=hub_slug,
    task_id=task.id,
    inputs=["1 2", "3 4"],
    outputs=["3", "7"]
)

# Add a single example
client.tasks.add_example(
    hub=hub_slug,
    task_id=task.id,
    input="5 6",
    output="11"
)
```

## Type Hints & Validation

The SDK now uses Pydantic models for inputs, providing better IDE support and early validation errors.

```python
from codeany_hub.models.inputs import TaskCreateInput

# IDEs will autocomplete these fields
input_data = TaskCreateInput(
    name="My Task",
    time_limit=1000,
    memory_limit=256,
    type="batch"
)
```
