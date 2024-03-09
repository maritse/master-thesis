import tensorflow as tf
import numpy as np

class NeuralNetwork:
    def __init__(self,
                 train_X = None,
                 train_Y = None,
                 test_X = None,
                 test_Y = None,
                 size = 0,
                 id = "test",
                 rounds = 10):
        self.id = id
        self.train_X = train_X,
        self.train_Y = train_Y
        self.test_X = test_X,
        self.test_Y = test_y,
        self.rounds = rounds,
        self.size = size,
        self.n_hidden_1 = 256,
        self.n_hidden_2 = 256,
        self.num_input = 784,
        self.num_classes = 10
        self.sess = tf.Session()


    def build(self, base):
        self.train_X = tf.placeholder("float", [None, self.num_input])
        self.train_Y = tf.placeholder("float", [None, self.num_classes])

        self.weights = {
            'w1': tf.Variable(base['w1'],name="w1"),
            'w2': tf.Variable(base['w2'],name="w2"),
            'wo': tf.Variable(base['wo'],name="wo")
        }
        self.biases = {
            'b1': tf.Variable(base['b1'],name="b1"),
            'b2': tf.Variable(base['b2'],name="b2"),
            'bo': tf.Variable(base['bo'],name="bo")
        }

        self.layer_1 = tf.add(tf.matmul(self.X, self.weights['w1']), self.biases['b1'])
        self.layer_2 = tf.add(tf.matmul(self.layer_1, self.weights['w2']),self.biases['b2'])
        self.out_layer = tf.matmul(self.layer_2, self.weights['wo'])+self.biases['bo']
        self.logits = self.out_layer
        self.correct_pred = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
        self.init = tf.global_variables_initializer()
        self.sess.run(self.init)

    def build_base(self):

        ''' 
        Function to initialize/build network with random initialization
        '''
        
        self.train_X = tf.placeholder("float", [None, self.num_input])
        self.train_Y = tf.placeholder("float", [None, self.num_classes])
        self.weights = {
            'w1': tf.Variable(tf.random_normal([self.num_input, self.n_hidden_1]),name="w1"),
            'w2': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_hidden_2]),name="w2"),
            'wo': tf.Variable(tf.random_normal([self.n_hidden_2, self.num_classes]),name="wo")
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([self.n_hidden_1]),name="b1"),
            'b2': tf.Variable(tf.random_normal([self.n_hidden_2]),name="b2"),
            'bo': tf.Variable(tf.random_normal([self.num_classes]),name="bo")
        }
        
        self.layer_1 = tf.add(tf.matmul(self.X, self.weights['w1']), self.biases['b1'])
        self.layer_2 = tf.add(tf.matmul(self.layer_1, self.weights['w2']),self.biases['b2'])
        self.out_layer = tf.matmul(self.layer_2, self.weights['wo'])+self.biases['bo']
        self.logits = self.out_layer
        self.correct_pred = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
        self.init = tf.global_variables_initializer()
        self.sess.run(self.init)




