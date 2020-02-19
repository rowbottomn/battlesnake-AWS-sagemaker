import os
import json
import numpy as np
import mxnet as mx
from mxnet import gluon 
import glob

def model_fn(model_dir):
    #load pretrained model
    print(glob.glob("{}/*".format(model_dir)))
    print("dir {}".format(model_dir))
    model = gluon.SymbolBlock.imports(
        '{}/local-symbol.json'.format(model_dir),
        ['data0', 'data1', 'data2', 'data3'],
        '{}/local-0000.params'.format(model_dir),
    ) 
    return model
    
def transform_fn(model, data, content_type, output_content_type):
    """
    Transform incoming requests.
    """
    
    #check if GPUs area available
    ctx = mx.gpu() if mx.context.num_gpus() > 0 else mx.cpu()
    
    data = json.loads(data)
    #convert input data into MXNet NDArray
    state = mx.nd.array(data["state"], ctx=ctx)
    snake_id = mx.nd.array(data["snake_id"], ctx=ctx)
    turn_count = mx.nd.array(data["turn_count"], ctx=ctx)
    snake_health = mx.nd.array(data["health"], ctx=ctx)
    
    #inference
    action = model(state, snake_id, turn_count, snake_health)
    
    #convert results to a list
    result = [action.asnumpy()[0].tolist()]
    
    #decode result as json string
    response_body = json.dumps(result)
    
    return response_body, output_content_type