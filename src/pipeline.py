import time
from src.services.training_service import TrainingService

def main():
    print("Initializing Training Pipeline (Headless Mode)...")
    service = TrainingService()
    
    # Start the non-blocking pipeline process controller
    controller = service.apply_pipeline()
    
    # Stream logs to the terminal while the pipeline runs
    while controller.is_alive():
        for line in controller.poll_new_logs():
            print(line)
        time.sleep(0.2)
        
    # Catch any remaining logs after completion
    for line in controller.poll_new_logs():
        print(line)
        
    # Final check on success state
    if controller.was_successful():
        print("\n[SUCCESS] Pipeline completed successfully from end to end!")
        exit(0)
    else:
        print(f"\n[ERROR] Pipeline failed. Please check the logs above for details.")
        exit(1)

if __name__ == "__main__":
    main()