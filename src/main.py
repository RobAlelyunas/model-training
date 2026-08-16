
if __name__ == "__main__":
    from src.core.initialize import init
    init()
    from src.ui.training_app import TrainingApp
    app = TrainingApp()
    app.mainloop()