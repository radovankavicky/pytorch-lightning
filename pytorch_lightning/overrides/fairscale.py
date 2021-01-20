# Copyright The PyTorch Lightning team.
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
from pytorch_lightning.trainer.states import RunningStage
from pytorch_lightning.utilities import _FAIRSCALE_AVAILABLE
from pytorch_lightning.utilities.exceptions import MisconfigurationException

LightningShardedDataParallel = None
if _FAIRSCALE_AVAILABLE:
    from fairscale.nn.data_parallel.sharded_ddp import ShardedDataParallel

    class LightningShardedDataParallel(ShardedDataParallel):

        def forward(self, *inputs, **kwargs):
            if self.enable_broadcast_buffers:
                self.sync_buffers()

            if self.module.running_stage == RunningStage.TRAINING:
                outputs = self.module.training_step(*inputs, **kwargs)

            elif self.module.running_stage == RunningStage.TESTING:
                outputs = self.module.test_step(*inputs, **kwargs)

            elif self.module.running_stage == RunningStage.EVALUATING:
                outputs = self.module.validation_step(*inputs, **kwargs)

            elif self.module.running_stage == RunningStage.PREDICTING:
                outputs = self.module(*inputs, **kwargs)

            else:
                raise MisconfigurationException(
                    "running_stage should either be [TRAINING, TESTING, EVALUATING, PREDICTING]")

            return outputs
