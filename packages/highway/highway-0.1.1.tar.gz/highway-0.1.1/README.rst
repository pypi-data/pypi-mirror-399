Highway
=======

Python SDK for Highway Workflow Engine. Build durable workflows with simple decorators.

Installation
------------

::

    pip install highway

Quick Start
-----------

.. code-block:: python

    from highway import Driver

    driver = Driver()  # Uses HIGHWAY_API_KEY env var

    @driver.task(shell=True)
    def backup_db():
        return "pg_dump mydb > backup.sql"

    @driver.task(py=True, depends=["backup_db"])
    def verify():
        import os
        return {"exists": os.path.exists("backup.sql")}

    result = driver.run()
    print(result.status)  # "completed"

Configuration
-------------

Set environment variables::

    export HIGHWAY_API_KEY="hw_k1_..."
    export HIGHWAY_API_ENDPOINT="https://highway.solutions"

Or pass directly:

.. code-block:: python

    driver = Driver(
        api_key="hw_k1_...",
        endpoint="https://highway.solutions"
    )

Task Types
----------

Shell Tasks
~~~~~~~~~~~

Execute shell commands:

.. code-block:: python

    @driver.task(shell=True)
    def list_files():
        return "ls -la /tmp"

Python Tasks
~~~~~~~~~~~~

Execute Python code in Highway's sandboxed environment:

.. code-block:: python

    @driver.task(py=True)
    def compute():
        import math
        return {"factorial": math.factorial(10)}

HTTP Tasks
~~~~~~~~~~

Make HTTP requests:

.. code-block:: python

    @driver.task(http=True)
    def call_api():
        return {
            "url": "https://api.example.com/webhook",
            "method": "POST",
            "json": {"status": "done"},
        }

Generic Tool Tasks
~~~~~~~~~~~~~~~~~~

Call any Highway tool directly:

.. code-block:: python

    @driver.task(tool="tools.llm.call")
    def summarize():
        return {
            "prompt": "Summarize: {{backup_result.stdout}}",
            "model": "claude-3-haiku-20240307"
        }

    @driver.task(tool="tools.database.query")
    def query_users():
        return {
            "connection_string": "vault:db/postgres",
            "query": "SELECT * FROM users"
        }

Workflow Execution
~~~~~~~~~~~~~~~~~~

Execute other workflows:

.. code-block:: python

    @driver.task(workflow="daily_report")
    def run_report():
        return {"inputs": {"date": "2024-01-01"}}

    @driver.task(workflow_id="uuid-here")
    def run_specific_version():
        return {"inputs": {"mode": "production"}}

Dependencies
------------

Tasks can depend on other tasks:

.. code-block:: python

    @driver.task(shell=True)
    def step_1():
        return "echo 'Step 1'"

    @driver.task(shell=True, depends=["step_1"])
    def step_2():
        return "echo 'Step 2'"

    @driver.task(shell=True, depends=["step_2"])
    def step_3():
        return "echo 'Step 3'"

Workflow Inputs
---------------

Pass variables to workflows:

.. code-block:: python

    result = driver.run(
        inputs={"email": "user@example.com", "env": "prod"},
        timeout=300
    )

Access inputs in tasks via ``{{inputs.key}}`` syntax.

Retry Configuration
-------------------

Configure automatic retries with exponential backoff:

.. code-block:: python

    @driver.task(http=True, retries=3, retry_delay=2.0, backoff=2.0)
    def call_flaky_api():
        return {"url": "https://api.example.com/endpoint"}

Durable Delays
--------------

Use Highway's native WaitOperator for delays that consume zero worker resources:

.. code-block:: python

    from datetime import timedelta

    @driver.task(shell=True, delay=timedelta(hours=2))
    def delayed_task():
        return "echo 'Runs after 2 hour delay'"

Scheduling
----------

Schedule recurring workflows:

.. code-block:: python

    @driver.task(shell=True, schedule="0 * * * *")  # Every hour
    def hourly_backup():
        return "pg_dump mydb > backup.sql"

    @driver.task(shell=True, schedule=timedelta(minutes=30))
    def interval_check():
        return "curl https://api.example.com/health"

Observability
-------------

Track running workflows:

.. code-block:: python

    # Non-blocking submit
    result = driver.run(wait=False)
    run_id = result.run_id

    # Check status
    status = driver.status(run_id)
    print(status.state)

    # Cancel
    driver.cancel(run_id)

Idempotency
-----------

Use workflow IDs for idempotent execution:

.. code-block:: python

    result1 = driver.run(workflow_id="order-12345")
    result2 = driver.run(workflow_id="order-12345")  # Returns cached result

Requirements
------------

- Python 3.11+
- Highway API key

License
-------

Apache 2.0
