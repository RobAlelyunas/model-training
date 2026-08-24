import json
from pathlib import Path
import shutil
import sys
import subprocess

from jinja2 import Template
from src.core.global_state import get_property, register_state_change_handler
from src.core.storage import get_datasets_dir, get_source_models_dir, get_templates_dir, get_generated_dir, get_target_models_dir
from src.core.logging import log


class TrainingService:
    def __init__(self):
        self._cancel_requested = False
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        """Called when global state changes."""
        pass

    def _run_cmd(self, cmd: str):
        """Helper to run a shell command synchronously, streaming stdout live to sys.stdout."""
        log("TrainingService", f"Running command: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            bufsize=1
        )

        # Stream line-by-line so it hits StdoutRedirector in real time
        if process.stdout:
            for line in process.stdout:
                sys.stdout.write(line)

        process.wait()
        
        if process.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {process.returncode}: {cmd}")

    def get_fused_model_path(self):
        return get_generated_dir() / f"{get_property('source_model')}-fused"

    def get_quantized_model_path(self):
        return get_generated_dir() / f"{get_property('source_model')}-fused-quantized"

    def get_adapter_path(self):
        return get_generated_dir() / "adapter"

    def get_data_dir(self):
        return get_generated_dir() / "data"
    
    def cleanup_generated_folder(self):
        """Deletes the generated folder to ensure a clean slate for training."""
        generated_dir = get_generated_dir()
        if generated_dir.exists() and generated_dir.is_dir():
            shutil.rmtree(generated_dir)
            log("TrainingService", f"Successfully deleted {generated_dir} and all its contents.")
        else:
            log("TrainingService", f"Directory {generated_dir} does not exist.")
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

    def prepare_data_dir(self):

        # 1. Clear and recreate the generated/data directory
        out_dir = self.get_data_dir()
        if out_dir.exists() and out_dir.is_dir():
            shutil.rmtree(out_dir)
            log("TrainingService", f"Successfully deleted {out_dir} and all its contents.")
        else:
            log("TrainingService", f"Directory {out_dir} does not exist.")
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
        log("TrainingService", f"Processing dataset from {in_file}")

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

        log("TrainingService", f"Successfully processed {processed_count} records into {output_file_path}")
    
        # 5. Copy training file to validation dataset slot
        valid_file_path = self.get_data_dir() / "valid.jsonl"
        shutil.copy(output_file_path, valid_file_path)
        log("TrainingService", f"Successfully copied {output_file_path} to {valid_file_path}")

    def train_lora(self):
        batch_size = get_property("lora_batch_size")
        num_layers = get_property("lora_num_layers")
        iters = get_property("lora_iters")
        learning_rate = get_property("lora_learning_rate")
        source_path = get_source_models_dir() / get_property("source_model")
        if not source_path.exists():
            raise FileNotFoundError(f"Source model not found at {source_path}. Please ensure it exists.")
        
        cmd = (
            "mlx_lm.lora "
            f"--model {source_path} "
            f"--data {self.get_data_dir()} "
            "--train "
            f"--batch-size {batch_size} "
            f"--num-layers {num_layers} "
            f"--iters {iters} "
            f"--learning-rate {learning_rate} "
            f"--grad-checkpoint "
            f"--adapter-path {self.get_adapter_path()}"
        )
        self._run_cmd(cmd)

    def fuse_model(self):
        source_path = get_source_models_dir() / get_property("source_model")
        if not source_path.exists():
            raise FileNotFoundError(f"Source model not found at {source_path}. Please ensure it exists.")
        adapter_path = self.get_adapter_path()
        if not adapter_path.exists():
            raise FileNotFoundError(f"Adapter not found at {adapter_path}. Please ensure it exists.")

        cmd = (
            "mlx_lm.fuse "
            f"--model {source_path} "
            f"--save-path {self.get_fused_model_path()} "
            f"--adapter-path {adapter_path}"
        )
        self._run_cmd(cmd)

    def install_chat_template(self):
        if not get_property("chat_template"):
            log("TrainingService", "No chat template, skipping install")
            return
        if get_property("chat_template") == "None":
            log("TrainingService", "Chat template is None, skipping install")
            return
        chat_template_path = get_templates_dir() / get_property("chat_template")
        if not chat_template_path.exists():
            raise FileNotFoundError(f"Chat template not found at {chat_template_path}. Please ensure it exists.")
        output_path = self.get_fused_model_path() / "chat_template.jinja"
        shutil.copy(chat_template_path, output_path)
        log("TrainingService", f"Successfully generated template at: {output_path}")

    def quantize_fused_model(self):
        q_bits = get_property("quantization_bits")
        perform_quantization = get_property("perform_quantization")

        if not perform_quantization:
            cmd = "echo '[INFO] Quantization skipped.'"
        else:
            cmd = (
                "mlx_lm.convert "
                f"--model {self.get_fused_model_path()} "
                f"-q "
                f"--q-bits {q_bits} "
                f"--mlx-path {self.get_quantized_model_path()}"
            )
        self._run_cmd(cmd)

    def deploy_target_model(self):
        target_model = get_property("target_model")
        target_path = Path(get_target_models_dir() / target_model)

        if self.get_quantized_model_path().exists():
            log("TrainingService", f"[INFO] Deploying quantized fused model from {self.get_quantized_model_path()} to {target_path}.")
            source_to_copy = self.get_quantized_model_path()
        elif self.get_fused_model_path().exists():
            log("TrainingService", f"[INFO] Deploying unquantized fused model from {self.get_fused_model_path()} to {target_path}.")
            source_to_copy = self.get_fused_model_path()
        else:
            raise FileNotFoundError(f"[ERROR] Neither quantized nor fused model found for source '{get_property('source_model')}' in generated/")

        if target_path.exists():
            shutil.rmtree(target_path)

        shutil.copytree(source_to_copy, target_path)
        log("TrainingService", f"[INFO] Successfully deployed model to {target_path}.")

    def request_cancel(self):
        """Signals the pipeline to stop after the current step completes."""
        self._cancel_requested = True
        log("TrainingService", "Stop requested by user. Will halt after current step.")

    def apply_pipeline(self):
        """Runs all steps sequentially as standard blocking calls."""
        self._cancel_requested = False

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
            if self._cancel_requested:
                log("PIPELINE", f"Stopping queue. Skipping remaining step: {step_name}")
                break

            log("PIPELINE", f"Starting step: {step_name}")
            # Each step blocks completely until finished
            step_func()
            log("PIPELINE", f"Successfully completed step: {step_name}")

        if self._cancel_requested:
            log("PIPELINE", "Pipeline successfully stopped after current step.")
        else:
            log("PIPELINE", "All pipeline steps completed successfully!")

training_service = TrainingService()