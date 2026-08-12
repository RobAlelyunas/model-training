import time
from src.services.training_service import TrainingService

def main():

    print("Initializing Training Pipeline (Headless Mode)...")
    service = TrainingService()

    try:
        service.apply_pipeline()
        print("\n[SUCCESS] Pipeline completed successfully from end to end!")
        exit(0)

    except Exception as e:
        print(f"[ERROR] pipeline failed with exception: {e}")
        exit(1)



if __name__ == "__main__":
    main()