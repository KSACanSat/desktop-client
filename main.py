from app import App

if __name__ == "__main__":
    try:
        App.get_instance().show()
    finally:
        App.get_instance().stop("execution")
