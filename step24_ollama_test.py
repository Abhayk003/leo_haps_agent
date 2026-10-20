import time
import ollama

MODEL = "qwen2.5:3b"

messages = [
    {"role": "system", "content": "You are a network assistant. Answer briefly."},
    {"role": "user", "content": (
        "Available links right now:\n"
        "ONEWEB-0196: capacity 1009.8 Mbps\n"
        "HAPS: capacity 719.0 Mbps\n"
        "ONEWEB-0205: capacity 654.7 Mbps\n"
        "Which link has the highest capacity? Reply with only its name."
    )},
]

start = time.perf_counter()
response = ollama.chat(model=MODEL, messages=messages, options={"temperature": 0})
elapsed = time.perf_counter() - start

print("Model reply:", response["message"]["content"])
print(f"Time taken: {elapsed:.1f} s")