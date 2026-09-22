



if __name__ == "__main__":
    # worker process mode due to --worker flag
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        sys.argv = sys.argv[2:]
        target_module = sys.argv[0]
        import runpy
        runpy.run_module(target_module, run_name="__main__", alter_sys=True)
        sys.exit(0)

    # Standard path: Launch GUI
    from src.core.initialize import init
    init()
    from src.ui.training_app import TrainingApp
    app = TrainingApp()
    from src.services.run_command import cleanup_orphan_processes
    import sys
    app.protocol("WM_DELETE_WINDOW", lambda: (cleanup_orphan_processes(), app.destroy(), sys.exit(0)))
    app.mainloop()