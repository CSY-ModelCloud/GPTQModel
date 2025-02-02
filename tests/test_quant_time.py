# Copyright 2025 ModelCloud
# Contact: qubitium@modelcloud.ai, x.com/qubitium
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os


os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

import unittest  # noqa: E402
import time  # noqa: E402

from datasets import load_dataset  # noqa: E402
from gptqmodel import GPTQModel  # noqa: E402
from gptqmodel.quantization.config import QuantizeConfig  # noqa: E402
from models.model_test import ModelTest  # noqa: E402


class TestQuantTime(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/Llama-3.2-1B-Instruct"
    INPUTS_MAX_LENGTH = 2048
    DATASETS_MAX_COUNT = 128
    QUANT_TIME = 94
    MAX_DELTA_FLOOR_PERCENT = 0.05
    MAX_POSITIVE_DELTA_CEIL_PERCENT = 0.5 # 3090 spends 132.33%

    def test_quant_time(self):
        quantize_config = QuantizeConfig(
            bits=4,
            group_size=128,
        )

        model = GPTQModel.load(
            self.NATIVE_MODEL_ID,
            quantize_config=quantize_config,
        )
        tokenizer = model.tokenizer

        datasets = self.load_dataset(tokenizer)

        start_time = time.time()
        model.quantize(datasets, batch_size=4)
        end_time = time.time()

        quant_time = end_time - start_time

        print("**************** Quant Time Result Info****************")
        print(f"Quant Time: {quant_time} s")
        print("**************** Quant Time Result Info End****************")

        diff_pct = (quant_time / self.QUANT_TIME) * 100
        negative_pct = 100 * (1 - self.MAX_DELTA_FLOOR_PERCENT)
        positive_pct = 100 * (1 + self.MAX_POSITIVE_DELTA_CEIL_PERCENT)

        self.assertTrue(negative_pct <= diff_pct <= positive_pct,
                        f"Quant Time Second: {quant_time} diff {diff_pct:.2f}% is out of the expected range [{negative_pct}-{positive_pct}%]")




