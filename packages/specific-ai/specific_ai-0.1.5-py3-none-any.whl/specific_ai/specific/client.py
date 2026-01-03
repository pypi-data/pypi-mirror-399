import time
from specific_ai.common.inference import Inference
from specific_ai.common.tracing import Tracing

class SpecificAIClient:
    def __init__(self, url: str):
        self.inference = Inference(url)
        self.tracing = Tracing(url)

    def create(self, message: str, task_name: str, project_name: str = "default"):
        response = None
        raw_logits = None
        inference_error = None

        try:
            start_time = time.time()
            responses, raw_logits = self.inference.infer(message, task_name, project_name)
            response = responses[0]
            return response
        except Exception as e:
            inference_error = str(e)
            raise Exception("Error inferring on specific.ai model") from e
        finally:
            self.tracing.collect(
                response=response,
                raw_logits=raw_logits,
                inference_error=inference_error,
                modelname="specific.ai",
                prompt=message,
                usecase_name=task_name,
                usecase_group=project_name,
                response_time=time.time() - start_time,
                is_from_specific_ai_model=True,
                logprobs=None,
            )
