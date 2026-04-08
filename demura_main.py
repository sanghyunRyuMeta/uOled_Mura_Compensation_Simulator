import json
from demura_functions import Meta_Demura

def main():
   
    with open('config.json', 'r') as f:
        config = json.load(f)

    processor = Meta_Demura(config)
    success = processor.run()

    if success:
        print("\n|----Demura Process Completed Successfully.----|")
    else:
        print("Demura process failed.")

if __name__ == "__main__":
    main()
