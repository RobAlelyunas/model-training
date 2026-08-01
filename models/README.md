## Overview
The pipeline takes a model from the models/sources directory,  applies a training data set to it and deposits the result in the models/targets directory.  The source model can be any MLX compatible model.  If you don't wanna blow up memory, don't use a source model that is very much larger than about 2/3 the size of your total available memory.  If you want a model to get started, there's a base model on hugging face that can be downloaded like this into your models/sources directory.  Make sure to update the properties.json to match the source model name and the desired target model name.

source .venv/bin/activate (if needed)
cd models/sources
hf download ralelyunas/Llama-3.2-3B-4bit
