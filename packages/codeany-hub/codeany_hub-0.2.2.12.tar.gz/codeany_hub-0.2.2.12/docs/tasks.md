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

## Choosing a Checker

The checker defines how the problem's output is compared against the official answer. Choosing the right checker is crucial for tasks where multiple outputs might be correct (e.g., floating point precision or multiple valid paths).

### Available Checker Types

Set the `checker_type` in your payload to one of the following:

| Checker Type | Description |
| :--- | :--- |
| `no_checker` | **Default**. No output validation is performed. |
| `compare_lines_not_ignore_whitespaces` | Strict line-by-line comparison, including all whitespaces. |
| `compare_lines_ignore_whitespaces` | Line-by-line comparison, ignoring leading/trailing/extra whitespaces. |
| `single_yes_or_no_case_insensitive` | Validates a single "Yes" or "No" answer, regardless of case. |
| `single_or_multiple_yes_or_no_case_insensitive` | Validates one or more "Yes" or "No" answers, case-insensitively. |
| `single_or_multiple_int64_ignore_whitespaces` | Validates 64-bit integers, ignoring surrounding whitespace. |
| `single_or_multiple_double_ignore_whitespaces` | Validates doubles, ignoring whitespaces. Supports `precision` (default: 6). |
| `custom_checker` | Provide your own C++17 source code for complex validation logic. |

### Updating the Checker

```python
from codeany_hub.models import CheckerType

# Configure a floating point checker with custom precision
client.tasks.update_checker(
    hub=hub_slug,
    task_id=task.id,
    payload={
        "checker_type": CheckerType.DOUBLE_IGNORE_WS,
        "precision": 9
    }
)

# Use strict line comparison
client.tasks.update_checker(
    hub=hub_slug,
    task_id=task.id,
    payload={"checker_type": CheckerType.LINES_STRICT}
)

# Upload a custom C++ checker
client.tasks.update_checker(
    hub=hub_slug,
    task_id=task.id,
    payload={
        "checker_type": CheckerType.CUSTOM,
        "checker_language": "cpp",
        "checker": "#include \"testlib.h\"\n\nint main(int argc, char* argv[]) {\n    registerTestlibCmd(argc, argv);\n    // Your logic here\n    quitf(_ok, \"passed\");\n}"
    }
)
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
# usage: client.tasks.upload_testset_zip(hub, task_id, testset_id, zip_path, progress_callback=...)

# Example with progress tracking
def progress(bytes_read: int):
    print(f"\rUploaded {bytes_read} bytes...", end="", flush=True)

try:
    with open("tests.zip", "rb") as f:
        events = client.tasks.upload_testset_zip(
            hub=hub_slug,
            task_id=task.id,
            testset_id=1,
            zip_path=f,
            progress_callback=progress
        )
        print("\nUpload started. Processing on server...")
        for event in events:
            print(f"Server status: {event.status} - {event.message}")
            if event.status == "completed":
                print("Testset upload finished successfully.")

except Exception as e:
    print(f"\nUpload failed: {e}")

# Note: The SDK streams the file by default for memory efficiency.

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
