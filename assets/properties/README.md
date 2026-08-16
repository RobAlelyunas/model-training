
## properties。json

### property: TOKENS
The tokens are used to create well-formatted training data and to correctly format the chat_template.jinja embedded with the model to match the training data and control the model's understnding of turns and conversations.  These will be different for each kind of model.  The default values are given for Llama 3 models, but for example for Mistral you might use something like: 
BEGIN_CONVERSATION_TOKEN = "<s>"
BEGIN_MESSAGE_TOKEN = "[INST]"
END_MESSAGE_HEADER_TOKEN = "]"
END_MESSAGE_TOKEN = "[/INST]"
And for Qwen something like:
BEGIN_CONVERSATION_TOKEN = ""
BEGIN_MESSAGE_TOKEN = "<|im_start|>"
END_MESSAGE_HEADER_TOKEN = ""
END_MESSAGE_TOKEN = "<|im_end|>"
### property: base_model 
 This code was tested mainly on Meta-LLama-3-8B which can be downloaded from HuggingFace。 Install your base model in the deps/ directory and point to it here.
### property: dist_model_name
This is the name to use to deploy the final quantized and trained model to the dist directory.  Its also the model that will be used for inferences. 
### property: dataset_path
This is the path to the file in which a working copy of your training data is kept in a jsonl format with each record having a "prompt" and "completion".  This file will be processed into single "text" and have tags added before it is fed to the training command as train.jsonl.  Since this training data uniquely defines your model behavior, this property lets you configure your current working data set.
### property: quantization 
 If you are using a 16 bit base model then you can quantize the final fused model to make it smaller for distribution. In this case, specify the number of bits. Quantization shrinks the total model size and makes it more manageable. If the base model is already quantized from original 16 bits, don't perform an additional quanitzation step because it will make the weights noisy.
### lora_*
The parameters used for LoRA training.
### max_inference_tokens and inference_temperature
These are paramters used by the inference engine during queries


## working_dataset.jsonl
The file that accrues your training data. It consists of json records, each with two text entries for prompt and completion.
## prompts.txt
A collecton of real prompts fed to LLM's.  These can be selected at random to help you develop representative training data.
## toby_dataset.jsonl
An example working data set that was used to create the Toby personality.
## chat_template.jinja
The jinja file that will be embedded in your distribution model as a chat template.  Note that TAG_1, TAG_2, END_TAG will first be replaced with values from your properties file.
