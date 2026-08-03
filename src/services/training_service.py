import json
from pathlib import Path
import shutil
import time
from src.services.process_controller import ProcessController
from src.global_state import get_property, register_state_change_handler


class TrainingService:
    def __init__(self):
        self.set_local_properties()
        self._cancel_requested = False
        register_state_change_handler(self.global_state_changed)

    def set_local_properties(self):
        """Initializes local properties from the global state."""
        self.source_model = get_property("source_model")
        self.dataset_path = get_property("dataset_path")
        self.target_model = get_property("target_model")
        self.fused_path = Path(f"generated/{self.source_model}-fused")
        self.quant_path = Path(f"generated/{self.source_model}-fused-quantized")
        self.target_path = Path(f"models/targets/{self.target_model}")
        self.source_path = Path(f"models/sources/{self.source_model}")

    def global_state_changed(self):
        """Called when global state changes, e.g., source model, target model, or dataset path changes."""
        self.set_local_properties()

    def cleanup_generated_folder(self):
        cmd = "rm -rf generated/*"
        return ProcessController(cmd).start()

    def prepare_data_dir(self):

        def _task():
            out_dir = Path("generated/data")
            if out_dir.exists() and out_dir.is_dir():
                shutil.rmtree(out_dir)
                print(f"Successfully deleted {out_dir} and all its contents.")
            else:
                print(f"Directory {out_dir} does not exist.")
            out_dir.mkdir(parents=True, exist_ok=True)

            output_file_path = "generated/data/train.jsonl"
            
            BEGIN_CONVERSATION_TOKEN = get_property("BEGIN_CONVERSATION_TOKEN")
            BEGIN_MESSAGE_TOKEN = get_property("BEGIN_MESSAGE_TOKEN")
            END_MESSAGE_HEADER_TOKEN = get_property("END_MESSAGE_HEADER_TOKEN")
            END_MESSAGE_TOKEN = get_property("END_MESSAGE_TOKEN")
            
            processed_count = 0
            in_file = Path(self.dataset_path)
            if not in_file.exists():
                raise FileNotFoundError(f"Could not find input dataset at {in_file}") 

            print(f"Processing dataset from {in_file} and writing to {output_file_path}...")

            with open(in_file, "r", encoding="utf-8") as fin, \
                 open(output_file_path, "w", encoding="utf-8") as fout:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue   
                    record = json.loads(line)
                    prompt = record.get("prompt", "")
                    completion = record.get("completion", "")
                    combined_text = (
                        f"{BEGIN_CONVERSATION_TOKEN}"
                        f"{BEGIN_MESSAGE_TOKEN}user{END_MESSAGE_HEADER_TOKEN}"
                        f"{prompt}{END_MESSAGE_TOKEN}"
                        f"{BEGIN_MESSAGE_TOKEN}assistant{END_MESSAGE_HEADER_TOKEN}"
                        f"{completion}{END_MESSAGE_TOKEN}"
                    )                
                    out_record = {"text": combined_text}
                    fout.write(json.dumps(out_record, ensure_ascii=False) + "\n")
                    processed_count += 1    
                    
            print(f"Successfully processed {processed_count} records into {output_file_path}")
        
            valid_file_path = Path("generated/data/valid.jsonl")
            shutil.copy(output_file_path, valid_file_path)
            print(f"Successfully copied {output_file_path} to {valid_file_path}")

        return ProcessController(_task).start()

    def train_lora(self):
        batch_size = get_property("lora_batch_size")
        num_layers = get_property("lora_num_layers")
        iters = get_property("lora_iters")
        learning_rate = get_property("lora_learning_rate")

        cmd = (
            "mlx_lm.lora "
            f"--model {self.source_path} "
            f"--data generated/data "
            "--train "
            f"--batch-size {batch_size} "
            f"--num-layers {num_layers} "
            f"--iters {iters} "
            f"--learning-rate {learning_rate} "
            f"--grad-checkpoint "
            f"--adapter-path generated/adapter"
        )
        return ProcessController(cmd).start()

    def fuse_model(self):
        cmd = (
            "mlx_lm.fuse "
            f"--model {self.source_path} "
            f"--save-path {self.fused_path} "
            f"--adapter-path generated/adapter"
        )
        return ProcessController(cmd).start()

    def install_chat_template(self):
        def _task():
            BEGIN_CONVERSATION_TOKEN = get_property("BEGIN_CONVERSATION_TOKEN")
            BEGIN_MESSAGE_TOKEN = get_property("BEGIN_MESSAGE_TOKEN")
            END_MESSAGE_HEADER_TOKEN = get_property("END_MESSAGE_HEADER_TOKEN")
            END_MESSAGE_TOKEN = get_property("END_MESSAGE_TOKEN")

            template_path = Path("resources/chat_template.jinja")
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            preamble_lines = [
                f"{{% set BEGIN_CONVERSATION_TOKEN = '{BEGIN_CONVERSATION_TOKEN}' %}}",
                f"{{% set BEGIN_MESSAGE_TOKEN = '{BEGIN_MESSAGE_TOKEN}' %}}",
                f"{{% set END_MESSAGE_HEADER_TOKEN = '{END_MESSAGE_HEADER_TOKEN}' %}}",
                f"{{% set END_MESSAGE_TOKEN = '{END_MESSAGE_TOKEN}' %}}"
            ]
            updated_content = "\n".join(preamble_lines) + "\n" + template_content

            self.fused_path.mkdir(parents=True, exist_ok=True)
            output_path = Path(f"{self.fused_path}/chat_template.jinja")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"Successfully generated template at: {output_path}")

        return ProcessController(_task).start()

    def quantize_fused_model(self):
        
        q_bits = get_property("quantization_bits")
        perform_quantization = get_property("perform_quantization")

        if not perform_quantization:
            cmd = "echo '[INFO] Quantization skipped.'"
        else:
            cmd = (
            "mlx_lm.convert "
            f"--model {self.fused_path} "
            f"-q "
            f"--q-bits {q_bits} "
            f"--mlx-path {self.quant_path}"
        )
        return ProcessController(cmd).start()

    def deploy_target_model(self):
    
        if self.quant_path.exists():
            print(f"[INFO] Deploying quantized fused model from {self.quant_path} to {self.target_path}.")
            source_to_copy = self.quant_path
        elif self.fused_path.exists():
            print(f"[INFO] Deploying unquantized fused model from {self.fused_path} to {self.target_path}.")
            source_to_copy = self.fused_path
        else:
            raise FileNotFoundError(f"[ERROR] Neither quantized nor fused model found for source '{self.source_model}' in generated/")

        cmd = f"cp -r {source_to_copy} {self.target_path}"
        return ProcessController(cmd).start()

    def request_cancel(self):
        """Signals the pipeline to stop after the current step completes."""
        self._cancel_requested = True
        print("\n[TrainingService] Stop requested by user. Will halt after current step.")

    def apply_pipeline(self):
        """Runs all steps sequentially, checking for cancellation between steps."""
        self._cancel_requested = False  # Reset flag at the start of a new pipeline run

        def _pipeline_task():
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
                    print(f"\n[PIPELINE] Stopping queue. Skipping remaining step: {step_name}")
                    break

                print(f"\n[PIPELINE] Starting step: {step_name}")
                controller = step_func()
                
                # Block and wait for this step to finish completely before moving to the next
                while controller.is_alive():
                    time.sleep(0.1)

                if not controller.was_successful():
                    if self._cancel_requested:
                        break
                    raise RuntimeError(f"Pipeline failed at step: '{step_name}'")
                
                print(f"[PIPELINE] Successfully completed step: {step_name}")

            if self._cancel_requested:
                print("\n[PIPELINE] Pipeline successfully stopped after current step.")
            else:
                print("\n[PIPELINE] All pipeline steps completed successfully!")

        return ProcessController(_pipeline_task).start()

training_service = TrainingService()