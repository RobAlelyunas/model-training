
if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # This main can be entered in three ways:
    # 1. When mlx spawns a multiprocessing worker
    # 2. When the user launches the GUI (no args or --ui)
    # 3. When the UI spawns a separate python process worker (e.g., downloader)
    # -------------------------------------------------------------------------

    # 1. Multiprocessing worker entry point, note it calls sys.exit(0) when finished
    import multiprocessing
    multiprocessing.freeze_support()

    import sys
    is_ui = len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "--ui")
    if is_ui:
        # 2. GUI entry point
        from src.core.initialize import init
        init()
        from src.ui.training_app import TrainingApp
        app = TrainingApp()
        from src.services.run_command import cleanup_orphan_processes
        import sys
        app.protocol("WM_DELETE_WINDOW", lambda: (cleanup_orphan_processes(), app.destroy(), sys.exit(0)))
        app.mainloop()
    else:
        # 3. Command-line module entry point
        target_module = sys.argv[1]
        sys.argv = sys.argv[1:]
        import runpy
        try:
            runpy.run_module(target_module, run_name="__main__", alter_sys=True)
            sys.exit(0)
        except Exception as e:
            print(f"Error occurred while running module '{target_module}': {e}")
            sys.exit(1)

