#!/usr/bin/env python3

from keras.models import Model, Sequential
from keras.layers import Dense, LSTM, Input, merge, Bidirectional
import numpy as np
import json

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None

def input_gen(shape, dtype=np.float32):
    inp = np.empty(shape, dtype=dtype)
    i = 0
    for x in np.nditer(inp, op_flags=['readwrite']):
        x[...] = i + 0.05
        i+= 0.05

    print("Inputs:")
    print(inp)
    return inp

def model(timestep, dimension, output):
    inp = Input(shape=(timestep, dimension))
    forward1 = LSTM(units=int(output/2), activation='tanh', recurrent_activation='hard_sigmoid',
                unit_forget_bias=False,
                return_sequences=True)(inp)
    backward1 = LSTM(units=int(output/2), activation='tanh', recurrent_activation='hard_sigmoid',
                return_sequences=True,
                unit_forget_bias=False,
                go_backwards=True)(inp)
    blstm1 = merge([forward1, backward1], mode="concat", concat_axis=-1)

    forward2 = LSTM(units=int(output/2), activation='tanh', recurrent_activation='hard_sigmoid',
                unit_forget_bias=False,
                return_sequences=True)(blstm1)
    backward2 = LSTM(units=int(output/2), activation='tanh', recurrent_activation='hard_sigmoid',
                return_sequences=True,
                unit_forget_bias=False,
                go_backwards=True)(blstm1)
    blstm2 = merge([forward2, backward2], mode="concat", concat_axis=-1)

    model = Model(inputs=[inp], outputs=blstm2)
    print(model.summary())
    print(model.get_config())
    return model

def model2(timestep, dimension, output):
    model = Sequential()
    model.add(Bidirectional(LSTM(units=int(output/2),activation='tanh', return_sequences=True), input_shape=(timestep, dimension)))
    model.add(Bidirectional(LSTM(units=int(output/2),activation='tanh', return_sequences=True)))
    print(model.summary())
    print(model.get_config())
    return model

x = input_gen([1, 4, 6])
m = model(4, 6, 6)
predict = m.predict(x)
print(predict)

import gc; gc.collect()
