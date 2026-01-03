import argparse
from pathlib import Path

from jcclang.adapter.base_adapter import BaseAdapter
from jcclang.core.const import DataType
from jcclang.core.logger import jcwLogger


class ModelArtsAdapter(BaseAdapter):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Model Training with input parameter')
        self.output = ""

    def before_task(self, inputs, context: dict):
        jcwLogger.info("modelarts before task")

    def after_task(self, outputs, context: dict):
        jcwLogger.info("modelarts after task, output", self.output)

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            if not any(a.dest == 'dataset_input' for a in self.parser._actions):
                self.parser.add_argument('--dataset_input', default='./data', type=str,
                                         help='dataset_input (default: %(default)s)')
        elif data_type == DataType.MODEL:
            if not any(a.dest == 'model_input' for a in self.parser._actions):
                self.parser.add_argument('--model_input', default='./models', type=str,
                                         help='model_input (default: %(default)s)')
        elif data_type == DataType.CODE:
            if not any(a.dest == 'code_input' for a in self.parser._actions):
                self.parser.add_argument('--code_input', default='./src', type=str,
                                         help='code_input (default: %(default)s)')
        else:
            jcwLogger.error(f"Unknown data type for input: {data_type}")
            return ""

        args, _ = self.parser.parse_known_args()

        base_path = ""
        if data_type == DataType.DATASET:
            base_path = args.dataset_input
        elif data_type == DataType.MODEL:
            base_path = args.model_input
        elif data_type == DataType.CODE:
            base_path = args.code_input

        path = Path(base_path) / file_path
        return path

    def output_prepare(self, data_type: str, file_path: str):
        if not any(a.dest == 'output' for a in self.parser._actions):
            self.parser.add_argument('--output', default='/output', type=str,
                                     help='output (default: %(default)s)')
        args, _ = self.parser.parse_known_args()
        path = Path(args.output) / file_path
        return path.as_posix()
