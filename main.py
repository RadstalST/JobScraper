from src import App
import argparse 

parser = argparse.ArgumentParser()
# is init 
parser.add_argument("--init", help="initialize the app", action="store_true")

if __name__ == "__main__":



    app = App()
    app()
