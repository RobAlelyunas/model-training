import sys
import os
import time
import argparse
import threading
from pathlib import Path
from huggingface_hub import snapshot_download, HfApi

# Minimum byte change (10 MB) required to trigger a new progress log statement
PROGRESS_DELTA_THRESHOLD = 10 * 1024 * 1024 

def get_total_repo_bytes(repo_id: str) -> int:
    """Queries Hugging Face API to sum expected repository file sizes."""
    try:
        api = HfApi()
        info = api.model_info(repo_id=repo_id, files_metadata=True)

        siblings = info.siblings or ()
        return sum(sibling.size or 0 for sibling in siblings)

    except Exception as e:
        print(
            f"[DOWNLOADER] Warning: Unable to fetch repo total size: {e}",
            file=sys.stderr,
        )
        return 0
    
def monitor_disk_usage(target_dir: Path, total_bytes: int, stop_event: threading.Event):
    """
    Background thread:
    - Prints full MB progress when bytes change by >= 10 MB.
    - Prints a simple 'Downloading...' heartbeat if 10 seconds pass without a 10 MB increase.
    """
    start_time = time.time()
    last_logged_bytes = -1
    last_log_time = time.time()

    while not stop_event.is_set():
        if target_dir.exists():
            current_bytes = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
        else:
            current_bytes = 0

        now = time.time()
        bytes_changed_enough = (
            last_logged_bytes == -1 or 
            (current_bytes - last_logged_bytes) >= PROGRESS_DELTA_THRESHOLD
        )
        heartbeat_due = (now - last_log_time) >= 10.0

        if bytes_changed_enough:
            # Significant progress made: Print actual byte metrics
            last_logged_bytes = current_bytes
            last_log_time = now
            
            elapsed = now - start_time
            speed_mbps = (current_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
            curr_mb = current_bytes / (1024 * 1024)
            
            if total_bytes > 0:
                total_mb = total_bytes / (1024 * 1024)
                pct = (current_bytes / total_bytes) * 100
                print(
                    f"\n[DOWNLOADER] Progress: {curr_mb:.1f} / {total_mb:.1f} MB ({pct:.1f}%) @ {speed_mbps:.2f} MB/s",
                    flush=True
                )
            else:
                print(
                    f"\n[DOWNLOADER] Downloaded: {curr_mb:.1f} MB @ {speed_mbps:.2f} MB/s",
                    flush=True
                )

        elif heartbeat_due:
            # Progress stalled or buffering: Print a reassuring heartbeat
            last_log_time = now
            print("\n[DOWNLOADER] Downloading...", flush=True)

        # Poll every 0.5s, broken into 100ms chunks so thread cancellation stays snappy
        stop_event.wait(0.5)

def main():
    parser = argparse.ArgumentParser(description="Standalone Hugging Face Model Downloader")
    parser.add_argument("repo_id", type=str, help="Hugging Face Repository ID (e.g., owner/model)")
    parser.add_argument("local_dir", type=str, help="Absolute destination directory path")
    
    args = parser.parse_args()

    # Enable fast downloads if hf_transfer is available
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    # Safely enable line buffering for real-time streaming to run_cmd
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(line_buffering=True)

    print(f"[DOWNLOADER] Starting download for: {args.repo_id}")
    print(f"[DOWNLOADER] Target directory: {args.local_dir}")

    target_path = Path(args.local_dir)

    # 1. Fetch total download size up front
    total_bytes = get_total_repo_bytes(args.repo_id)
    if total_bytes > 0:
        print(f"[DOWNLOADER] Repository total size: {total_bytes / (1024 * 1024):.1f} MB ({total_bytes} bytes)")

    # 2. Start disk monitoring thread
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_disk_usage,
        args=(target_path, total_bytes, stop_event),
        daemon=True
    )
    monitor_thread.start()

    try:
        # 3. Blocking download call
        snapshot_download(
            repo_id=args.repo_id,
            local_dir=args.local_dir
        )
        
        # Log final completion status
        if target_path.exists():
            final_bytes = sum(f.stat().st_size for f in target_path.rglob("*") if f.is_file())
            final_mb = final_bytes / (1024 * 1024)
            print(f"[DOWNLOADER] Progress: {final_mb:.1f} / {final_mb:.1f} MB (100.0%) - Download Complete", flush=True)

        print("[DOWNLOADER] Status: SUCCESS")
        sys.exit(0)
    except KeyboardInterrupt:
        print("[DOWNLOADER] Status: CANCELLED")
        sys.exit(130)
    except Exception as e:
        print(f"[DOWNLOADER] Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        # 4. Guarantee monitor thread shuts down cleanly
        stop_event.set()
        monitor_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()