# bananaproai-com

The `bananaproai-com` package provides a streamlined interface for interacting with the bananaproai-com platform, simplifying common tasks and showcasing its core capabilities. This library allows developers to quickly integrate and leverage the power of bananaproai-com within their Python applications.

## Installation

To install the `bananaproai-com` package, use pip:
bash
pip install bananaproai-com

## Basic Usage

Here are a few examples demonstrating how to use the `bananaproai-com` package:

**1. Running a Simple Inference:**

This example shows how to execute a basic inference task using a pre-configured model on bananaproai-com.
python
from bananaproai_com import BananaClient

# Replace with your API key and model ID
api_key = "YOUR_API_KEY"
model_id = "YOUR_MODEL_ID"

client = BananaClient(api_key=api_key, model_id=model_id)

input_data = {"prompt": "A photo of a cat wearing a hat"}

try:
    result = client.call_model(input_data)
    print(f"Inference Result: {result}")
except Exception as e:
    print(f"Error: {e}")

**2. Checking Model Status:**

This example demonstrates how to retrieve the current status of a specific model.
python
from bananaproai_com import BananaClient

# Replace with your API key and model ID
api_key = "YOUR_API_KEY"
model_id = "YOUR_MODEL_ID"

client = BananaClient(api_key=api_key, model_id=model_id)

try:
    status = client.get_model_status()
    print(f"Model Status: {status}")
except Exception as e:
    print(f"Error: {e}")

**3. Asynchronous Inference:**

For longer-running tasks, you can use asynchronous inference to avoid blocking your main thread.
python
import asyncio
from bananaproai_com import BananaClient

# Replace with your API key and model ID
api_key = "YOUR_API_KEY"
model_id = "YOUR_MODEL_ID"

async def run_inference():
    client = BananaClient(api_key=api_key, model_id=model_id)
    input_data = {"prompt": "Generate a long story about a robot."}

    try:
        result = await client.call_model_async(input_data)
        print(f"Asynchronous Inference Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(run_inference())

**4. Handling Errors Gracefully:**

This example illustrates how to catch and handle potential errors during API calls.
python
from bananaproai_com import BananaClient

# Replace with your API key and model ID
api_key = "YOUR_API_KEY"
model_id = "YOUR_MODEL_ID"

client = BananaClient(api_key=api_key, model_id=model_id)

input_data = {"prompt": "Generate something creative."}

try:
    result = client.call_model(input_data)
    if result and "error" in result:
        print(f"API Error: {result['error']}")
    else:
        print(f"Inference Result: {result}")
except Exception as e:
    print(f"Unexpected Error: {e}")

**5. Working with Multiple Models:**

Showcasing how to switch between and call multiple models.
python
from bananaproai_com import BananaClient

# Replace with your API key and model IDs
api_key = "YOUR_API_KEY"
model_id_1 = "MODEL_ID_1"
model_id_2 = "MODEL_ID_2"

client_1 = BananaClient(api_key=api_key, model_id=model_id_1)
client_2 = BananaClient(api_key=api_key, model_id=model_id_2)


input_data_1 = {"text": "Translate this to French."}
input_data_2 = {"image": "path/to/image.jpg"}

try:
    result_1 = client_1.call_model(input_data_1)
    print(f"Result from Model 1: {result_1}")

    result_2 = client_2.call_model(input_data_2)
    print(f"Result from Model 2: {result_2}")

except Exception as e:
    print(f"Error: {e}")

## Features

*   Simplified API interaction with bananaproai-com.
*   Synchronous and asynchronous inference support.
*   Error handling and exception management.
*   Model status retrieval.
*   Easy integration with existing Python projects.
*   Clear and concise documentation.

## License

MIT License

This project is a gateway to the bananaproai-com ecosystem. For advanced features and full capabilities, please visit: https://bananaproai.com/