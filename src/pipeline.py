import time
from src.services.training_service import TrainingService

def main():

    print("Initializing Training Pipeline (Headless Mode)...")
    service = TrainingService()
    
    controller = service.apply_pipeline()
    
    while controller.is_alive():
        time.sleep(0.2)
 
    if controller.was_successful():
        print("\n[SUCCESS] Pipeline completed successfully from end to end!")
        exit(0)
    else:
        print(f"\n[ERROR] Pipeline failed. Please check the logs above for details.")
        exit(1)

if __name__ == "__main__":
    main()