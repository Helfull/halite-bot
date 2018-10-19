import time
import uuid
import numpy as np
from keras.models import Model, load_model
from keras.layers import Input, Conv2D, GlobalMaxPooling2D, Dense, Dropout, concatenate
from keras.utils import plot_model

class Network:
    def __init__(self, headless=True, labels=2):
        self.model = QModel(headless=headless, labels=labels)

        self.s = None
        self.y = 0
        self.eps = 0.5
        self.decay_factor = 0.999
        self.headless = headless
        self.time = str(int(time.time()))
        self.id = uuid.uuid4()

    def predict(self, r, secondary, new_s, actions):
        self.eps *= self.decay_factor

        a = self.select_action(secondary, self.s, actions)
        self.learn(r, a, secondary, new_s)

        self.s = new_s

    def select_action(self, secondary, state, actions):

        if np.random.random() < self.eps:
            a = np.random.randint(0, len(actions)-1)
        else:
            a = np.argmax(self._predict(np.array(secondary), state))

        return a

    def learn(self, r, a, secondary, new_s):
        target = r + self.y * np.max(self._predict(new_s))
        target_vec = self._predict(self.s)[0]
        target_vec[a] = target

        self.model.fit({
                'vision_input': s,
                'secondary_input': secondary
            }, 
            target_vec.reshape(-1, 2),
            epochs=1, 
            verbose=0
        )

    def _predict(self, secondary, state):
        return self.model.predict(secondary, state)

    def draw(self):
        self.model.draw()

    def save(self):
        self.model.save(self.time, self.id)

    def load(self, name):
        self.model.load(name)

class QModel:
    def __init__(self, headless=True, labels=2):
        self.headless = headless
        self.model_storage = "model"

        input_conv, model_conv = self._conv_model()
        input_secondary, model_secondary = self._secondary_model()

        self.model = self._finish_model(
            inputs=[input_conv, input_secondary],
            outputs=[model_conv, model_secondary],
            labels=labels
        )

    def _conv_model(self, conv_layers=2):
        input_conv = Input(shape=(None, None, 3), name="vision_input")
        model_conv = Conv2D(filters=10, 
             kernel_size=(3, 3), 
             input_shape=(None, None, 3),
             padding="same",
             data_format='channels_last')(input_conv)

        for layer in range(conv_layers-1):
            model_conv = Conv2D(filters=10, 
                 kernel_size=(3, 3), 
                 input_shape=(None, None, 3),
                 padding="same",
                 data_format='channels_last')(model_conv)

        model_conv = GlobalMaxPooling2D()(model_conv)
        model_conv = Dense(128, activation='relu')(model_conv)
        model_conv = Dropout(0.2)(model_conv)
        model_conv = Dense(128, activation='sigmoid')(model_conv)

        return (input_conv, model_conv)

    def _secondary_model(self):
        input_secondary = Input(shape=(1,), name="secondary_input")
        model_secondary = Dense(128, input_shape=(1,), activation='relu')(input_secondary)

        return (input_secondary, model_secondary)

    def _finish_model(self, inputs, outputs, labels=8):

        added_outputs = concatenate(outputs)
        out = Dense(labels, activation='relu')(added_outputs)

        return Model(inputs=inputs, outputs=out)

    def predict(self, secondary, state):
        image = np.expand_dims(state, axis=0)
        return self.model.predict({
            'vision_input': image,
            'secondary_input': secondary
        })

    def draw(self):
        if not self.headless:
            plot_model(self.model, to_file="model.png")

    def save(self, time, id):
        self.model.save("{}/{}-{}.model".format(self.model_storage, time, id))

    def load(self, name):
        self.model.save("{}/{}.model".format(self.model_storage, name))



if __name__ == '__main__':
    network = QNetwork(False)
    network.draw()
    network.save()