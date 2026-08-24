from src.core.initialize import init
from src.core.logging import log

def main():

    # initialize global state before doing anything
    init()

    from src.services.training_service import TrainingService

    log("Pipeline","Initializing Training Service (Headless Mode)...")
    service = TrainingService()

    try:
        service.apply_pipeline()
        log("Pipeline", "\n[SUCCESS] Pipeline completed successfully from end to end!")
        exit(0)

    except Exception as e:
        log("Pipeline", f"[ERROR] pipeline failed with exception: {e}")
        exit(1)



if __name__ == "__main__":
    main()