from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
from src.core.global_state import get_property, register_state_change_handler
from src.core.storage import get_target_models_dir

class InferenceEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.target_model = get_property('target_model')
        register_state_change_handler(self.global_state_change)

    def global_state_change(self):
        new_model = get_property('target_model')
        if self.target_model != new_model:
            self.target_model = new_model
            self.load_model()           

    def load_model(self):
        if not self.target_model:
            return
        model_path = get_target_models_dir() / self.target_model
        if self.is_model_loaded():
            self.unload_model()  # Unload the current model before loading a new one
        self.model, self.tokenizer, *_ = load(model_path)
        print(f"Loaded MLX model from {model_path}...")

    def unload_model(self):
        """Unloads the model and forces garbage collection to free up memory."""
        if self.is_model_loaded():
            self.model = None
            self.tokenizer = None
            
            # Force Python garbage collection to clean up unreferenced tensors
            import gc
            gc.collect()
            
            # Force MLX to release cached memory back to the OS using the current API
            import mlx.core as mx
            mx.clear_cache()
                
            print("[InferenceEngine] Model unloaded to free memory.")
        else:
            print("[InferenceEngine] No model currently loaded.")

    def is_model_loaded(self) -> bool:
        return self.model is not None and self.tokenizer is not None
    
    def generate_raw_response(self, prompt: str) -> str:
        """Single point of entry for all generation against the MLX model."""
        if not self.model or not self.tokenizer:
            return "[Error: MLX model is not loaded]"

        # All generation parameters and samplers are managed here in one place

        max_inference_tokens = get_property("max_inference_tokens")
        inference_temperature = get_property("inference_temperature")
        sampler = make_sampler(temp=inference_temperature)

        return generate(
            self.model, 
            self.tokenizer, 
            prompt=prompt, 
            max_tokens=max_inference_tokens,
            sampler=sampler, 
            verbose=False
        ).strip()

    def generate_chat_response(self, prompt: str) -> str:
        """Formats the prompt using the chat template and delegates to generate_raw_response."""
        if not self.model or not self.tokenizer:
            return "[Error: MLX model is not loaded]"

        messages = [{"role": "user", "content": prompt}]
        
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
        else:
            formatted_prompt = prompt

        print(f"Formatted chat prompt sent to MLX model:\n{formatted_prompt}")
        
        # Delegate directly to the single point of entry
        return self.generate_raw_response(formatted_prompt)

inference_engine = InferenceEngine()