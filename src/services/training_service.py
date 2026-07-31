import json
from pathlib import Path
import shutil
import time

from src.services.process_controller import ProcessController
from src.config import get_property


class TrainingService:
    def __init__(self):
        self.base_model_name = get_property("base_model")
        self.dataset_path = get_property("dataset_path")
        self.dist_model_name = get_property("dist_model_name")

    def cleanup_generated_folder(self):
        cmd = "rm -rf generated/*"
        return ProcessController(cmd).start()

    def prepare_data_dir(self, dataset_path=None):
        if dataset_path is None:
            dataset_path = self.dataset_path

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
            in_file = Path(dataset_path)
            if not in_file.exists():
                raise FileNotFoundError(f"Could not find input dataset at {in_file}") 
                
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

    def train_lora(self, batch_size=None, num_layers=None, iters=None, learning_rate=None):
        if batch_size is None:
            batch_size = get_property("lora_batch_size")
        if num_layers is None:
            num_layers = get_property("lora_num_layers")
        if iters is None:
            iters = get_property("lora_iters")
        if learning_rate is None:
            learning_rate = get_property("lora_learning_rate")

        cmd = (
            "mlx_lm.lora "
            f"--model deps/{self.base_model_name} "
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
            f"--model deps/{self.base_model_name} "
            f"--save-path generated/{self.base_model_name}-fused "
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
            
            fused_model_path = Path(f"generated/{self.base_model_name}-fused")
            fused_model_path.mkdir(parents=True, exist_ok=True)
            output_path = Path(f"{fused_model_path}/chat_template.jinja")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"Successfully generated template at: {output_path}")

        return ProcessController(_task).start()

    def quantize_fused_model(self, q_bits=None):
        if q_bits is None:
            q_bits = get_property("quantization_bits")

        cmd = (
            "mlx_lm.convert "
            f"--model generated/{self.base_model_name}-fused "
            f"-q "
            f"--q-bits {q_bits} "
            f"--mlx-path generated/{self.base_model_name}-fused_{q_bits}bit"
        )
        return ProcessController(cmd).start()

    def deploy_dist_model(self):
        cmd = f"cp -r generated/{self.base_model_name}-fused_4bit dist/{self.dist_model_name}"
        return ProcessController(cmd).start()

    def apply_pipeline(self):
        """Runs all steps sequentially, printing everything directly to standard output."""
        def _pipeline_task():
            steps = [
                ("Cleanup Generated Folder", self.cleanup_generated_folder),
                ("Prepare Data Directory", self.prepare_data_dir),
                ("Train LoRA", self.train_lora),
                ("Fuse Model", self.fuse_model),
                ("Install Chat Template", self.install_chat_template),
                ("Quantize Fused Model", self.quantize_fused_model),
                ("Deploy Distribution Model", self.deploy_dist_model),
            ]

            for step_name, step_func in steps:
                print(f"\n[PIPELINE] Starting step: {step_name}")
                controller = step_func()
                
                # Block and wait for this step to finish completely before moving to the next
                while controller.is_alive():
                    time.sleep(0.1)

                if not controller.was_successful():
                    raise RuntimeError(f"Pipeline failed at step: '{step_name}'")
                
                print(f"[PIPELINE] Successfully completed step: {step_name}")

            print("\n[PIPELINE] All pipeline steps completed successfully!")

        return ProcessController(_pipeline_task).start()

training_service = TrainingService()