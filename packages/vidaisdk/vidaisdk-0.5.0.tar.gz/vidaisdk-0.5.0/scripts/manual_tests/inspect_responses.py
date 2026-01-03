import inspect
try:
    from openai.resources.responses import Responses
    print("Signature:", inspect.signature(Responses.create))
    print("Docstring:", Responses.create.__doc__)
except ImportError:
    print("Could not import Responses")
except Exception as e:
    print(f"Error: {e}")
