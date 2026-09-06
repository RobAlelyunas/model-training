import json
from pathlib import Path
import shutil
import sys

from jinja2 import Template
from src.core.global_state import get_property, register_state_change_handler
from src.core.storage import get_datasets_dir, get_source_models_dir, get_templates_dir, get_generated_dir, get_target_models_dir
from src.core.logging import log
from src.services.run_command import TaskHandle, run_cmd


class TrainingService:
    def __init__(self):
        self._cancel_requested = False
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        """Called when global state changes."""
        pass

    def get_fused_model_path(self):
        return get_generated_dir() / f"{get_property('source_model')}-fused"

    def get_quantized_model_path(self):
        return get_generated_dir() / f"{get_property('source_model')}-fused-quantized"

    def get_adapter_path(self):
        return get_generated_dir() / "adapter"

    def get_data_dir(self):
        return get_generated_dir() / "data"
    
    def cleanup_generated_folder(self, task_handle: TaskHandle | None = None):
        """Deletes the generated folder to ensure a clean slate for training."""
        generated_dir = get_generated_dir()
        if generated_dir.exists() and generated_dir.is_dir():
            shutil.rmtree(generated_dir)
            log("TrainingService", f"Successfully deleted {generated_dir} and all its contents.", task_handle)
        else:
            log("TrainingService", f"Directory {generated_dir} does not exist.", task_handle)
        get_generated_dir().mkdir(parents=True, exist_ok=True)

    def _format_record(self, record: dict, chat_template = None) -> str:
        """Converts a single record into text using either the chat template or a clean default format."""
        prompt = record.get("prompt", "")
        completion = record.get("completion", "")

        if not chat_template:
            return f"{prompt} {completion}"
        else:
            # Use the Jinja chat template
            conversation_messages = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": completion}
            ]
            return chat_template.render(
                messages=conversation_messages, 
                add_generation_prompt=False
            )

    def prepare_data_dir(self, task_handle: TaskHandle | None = None):

        # 1. Clear and recreate the generated/data directory
        out_dir = self.get_data_dir()
        if out_dir.exists() and out_dir.is_dir():
            shutil.rmtree(out_dir)
            log("TrainingService", f"Successfully deleted {out_dir} and all its contents.", task_handle)
        else:
            log("TrainingService", f"Directory {out_dir} does not exist.", task_handle)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 2. Resolve the chat template
        chat_template = None
        template_prop = get_property("chat_template")
        if template_prop and template_prop != "None":
            chat_template_path = get_templates_dir() / template_prop
            if not chat_template_path.exists():
                raise FileNotFoundError(f"Chat template not found at {chat_template_path}. Please ensure it exists.")
            with open(chat_template_path, "r", encoding="utf-8") as f:
                chat_template = Template(f.read())

        # 3. Locate the input dataset
        in_file = get_datasets_dir() / get_property("dataset")
        if not in_file.exists():
            raise FileNotFoundError(f"Could not find input dataset at {in_file}") 
        log("TrainingService", f"Processing dataset from {in_file}", task_handle)

        # 4. Stream line-by-line, convert, and write directly to the output file
        output_file_path = Path(f"{out_dir}/train.jsonl")
        processed_count = 0
        
        with open(in_file, "r", encoding="utf-8") as fin, open(output_file_path, "w", encoding="utf-8") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue   
                record = json.loads(line)
                formatted_text = self._format_record(record, chat_template)
                out_record = {"text": formatted_text}
                fout.write(json.dumps(out_record, ensure_ascii=False) + "\n")
                processed_count += 1

        log("TrainingService", f"Successfully processed {processed_count} records into {output_file_path}", task_handle)
    
        # 5. Copy training file to validation dataset slot
        valid_file_path = self.get_data_dir() / "valid.jsonl"
        shutil.copy(output_file_path, valid_file_path)
        log("TrainingService", f"Successfully copied {output_file_path} to {valid_file_path}", task_handle)

    def train_lora(self, task_handle: TaskHandle | None = None):
        batch_size = get_property("lora_batch_size")
        num_layers = get_property("lora_num_layers")
        iters = get_property("lora_iters")
        learning_rate = get_property("lora_learning_rate")
        source_path = get_source_models_dir() / get_property("source_model")
        if not source_path.exists():
            raise FileNotFoundError(f"Source model not found at {source_path}. Please ensure it exists.")
        
        cmd_args = [
            "mlx_lm",
            "lora",
            "--model", str(source_path),
            "--data", str(self.get_data_dir()),
            "--train",
            "--batch-size", str(batch_size),
            "--num-layers", str(num_layers),
            "--iters", str(iters),
            "--learning-rate", str(learning_rate),
            "--grad-checkpoint",
            "--adapter-path", str(self.get_adapter_path())
        ]
        run_cmd(cmd_args, task_handle)

    def fuse_model(self, task_handle: TaskHandle | None = None):
        source_path = get_source_models_dir() / get_property("source_model")
        if not source_path.exists():
            raise FileNotFoundError(f"Source model not found at {source_path}. Please ensure it exists.")
        adapter_path = self.get_adapter_path()
        if not adapter_path.exists():
            raise FileNotFoundError(f"Adapter not found at {adapter_path}. Please ensure it exists.")

        # Explicity run via current Python executable: sys.executable -m mlx_lm.fuse
        cmd_args = [
            "mlx_lm",
            "fuse",
            "--model", str(source_path),
            "--save-path", str(self.get_fused_model_path()),
            "--adapter-path", str(adapter_path)
        ]
        run_cmd(cmd_args, task_handle)

    def install_chat_template(self, task_handle: TaskHandle | None = None):
        if not get_property("chat_template"):
            log("TrainingService", "No chat template, skipping install", task_handle)
            return
        if get_property("chat_template") == "None":
            log("TrainingService", "Chat template is None, skipping install", task_handle)
            return
        chat_template_path = get_templates_dir() / get_property("chat_template")
        if not chat_template_path.exists():
            raise FileNotFoundError(f"Chat template not found at {chat_template_path}. Please ensure it exists.")
        output_path = self.get_fused_model_path() / "chat_template.jinja"
        shutil.copy(chat_template_path, output_path)
        log("TrainingService", f"Successfully generated template at: {output_path}", task_handle)

    def quantize_fused_model(self, task_handle: TaskHandle | None = None):
        q_bits = get_property("quantization_bits")
        perform_quantization = get_property("perform_quantization")

        if not perform_quantization:
            log("TrainingService", "[INFO] Quantization skipped.", task_handle)
            return

        # Explicity run via current Python executable: sys.executable -m mlx_lm.convert
        cmd_args = [
            "mlx_lm",
            "convert",
            "--model", str(self.get_fused_model_path()),
            "-q",
            "--q-bits", str(q_bits),
            "--mlx-path", str(self.get_quantized_model_path())
        ]
        run_cmd(cmd_args, task_handle)

    def deploy_target_model(self, task_handle: TaskHandle | None = None):
        target_model = get_property("target_model")
        target_path = Path(get_target_models_dir() / target_model)

        if self.get_quantized_model_path().exists():
            log("TrainingService", f"[INFO] Deploying quantized fused model from {self.get_quantized_model_path()} to {target_path}.", task_handle)
            source_to_copy = self.get_quantized_model_path()
        elif self.get_fused_model_path().exists():
            log("TrainingService", f"[INFO] Deploying unquantized fused model from {self.get_fused_model_path()} to {target_path}.", task_handle)
            source_to_copy = self.get_fused_model_path()
        else:
            raise FileNotFoundError(f"[ERROR] Neither quantized nor fused model found for source '{get_property('source_model')}' in generated/")

        if target_path.exists():
            shutil.rmtree(target_path)

        shutil.copytree(source_to_copy, target_path)
        log("TrainingService", f"[INFO] Successfully deployed model to {target_path}.", task_handle)

    def download_source_model(self, repo_id: str, task_handle: TaskHandle | None = None):
        """
        Downloads a model repository from Hugging Face directly into 
        the source models directory using the huggingface-cli via run_cmd.
        
        :param repo_id: Hugging Face repository identifier (e.g., 'mlx-community/Llama-3.2-1B-Instruct-4bit')
        """
        # Extract folder name (e.g. "Llama-3.2-1B-Instruct-4bit" from "mlx-community/Llama-3.2-1B-Instruct-4bit")
        model_folder_name = repo_id.split("/")[-1]
        model_path = get_source_models_dir() / model_folder_name

        log("TrainingService", f"Starting download for Hugging Face model '{repo_id}' into {model_path}", task_handle)

        cmd_args = [
            "src.services.downloader",
            repo_id,
            str(model_path)
        ]

        run_cmd(cmd_args, task_handle)

        if task_handle and task_handle.is_cancelled():
            log("TrainingService", f"Download of model '{repo_id}' was cancelled.", task_handle)
        else:
            log("TrainingService", f"Successfully downloaded model '{repo_id}' to {model_path}", task_handle)

    def apply_pipeline(self, task_handle: TaskHandle | None = None):
        """Runs all steps sequentially as standard blocking calls."""
        
        steps = [
            ("Cleanup Generated Folder", self.cleanup_generated_folder),
            ("Prepare Data Directory", self.prepare_data_dir),
            ("Train LoRA", self.train_lora),
            ("Fuse Model", self.fuse_model),
            ("Install Chat Template", self.install_chat_template),
            ("Quantize Fused Model", self.quantize_fused_model),
            ("Deploy Target Model", self.deploy_target_model),
        ]

        for step_name, step_func in steps:
            if task_handle and task_handle.is_cancelled():
                log("PIPELINE", f"Pipeline cancelled before starting step: {step_name}", task_handle)
                break

            log("PIPELINE", f"Starting step: {step_name}", task_handle)
            # Each step blocks completely until finished
            step_func(task_handle)
            log("PIPELINE", f"Successfully completed step: {step_name}", task_handle)

        if task_handle and task_handle.is_cancelled():
            log("PIPELINE", "Pipeline successfully cancelled.", task_handle)
        else:
            log("PIPELINE", "All pipeline steps completed successfully!", task_handle)

training_service = TrainingService()