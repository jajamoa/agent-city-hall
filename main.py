from src.utils import MessagePool
from src.mechanisms import BinaryFlow

if __name__ == "__main__":
    config_file = "config.yaml"
    output_file = "data/log/test.txt"
    flow = BinaryFlow(config_file, output_file)
    flow.start_flow()