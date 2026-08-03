import sys
from pathlib import Path
from src.global_state import load_command_line_overrides

# Ensure the root project directory is in the python path if running standalone
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.services.inference_engine import inference_engine

def test_inference_engine():
    print("--- Starting Inference Engine Test ---")

    # 1. Test initial unloaded state
    print("Testing pre-load state...")
    assert not inference_engine.is_model_loaded(), "Engine should report model as not loaded initially."
    
    raw_result = inference_engine.generate_raw_response("Hello")
    assert "[Error: MLX model is not loaded]" in raw_result, "Raw generation should fail gracefully when unloaded."
    
    chat_result = inference_engine.generate_chat_response("Hello")
    assert "[Error: MLX model is not loaded]" in chat_result, "Chat generation should fail gracefully when unloaded."
    print("Pre-load checks passed successfully.")

    # 2. Test loading the model
    print("\nLoading model via inference engine...")
    inference_engine.load_model()

    assert inference_engine.is_model_loaded(), "Engine should report model as loaded after load_model() is called."
    print("Model load checks passed successfully.")

    # 3. Test raw generation
    print("\nTesting raw generation...")
    test_prompt = "Once upon a time"
    raw_output = inference_engine.generate_raw_response(test_prompt)
    print(f"Prompt: '{test_prompt}'\nRaw Output:\n{raw_output}\n")
    assert isinstance(raw_output, str) and len(raw_output) > 0, "Raw generation should return a non-empty string."

    # 4. Test chat generation
    print("Testing chat generation...")
    chat_prompt = "What is the capital of France?"
    chat_output = inference_engine.generate_chat_response(chat_prompt)
    print(f"Prompt: '{chat_prompt}'\nChat Output:\n{chat_output}\n")
    assert isinstance(chat_output, str) and len(chat_output) > 0, "Chat generation should return a non-empty string."

    print("--- All Inference Engine Tests Passed Successfully! ---")

if __name__ == "__main__":
    load_command_line_overrides()
    test_inference_engine()