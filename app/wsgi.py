from main_api import create_app, log

application = create_app()
log.info(application)

if __name__ == "__main__":
    application.run()
