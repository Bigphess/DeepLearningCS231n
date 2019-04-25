from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3 * 32 * 32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        std = weight_scale
        self.params['W1'] = std * np.random.randn(input_dim, hidden_dim)
        self.params['W2'] = std * np.random.randn(hidden_dim, num_classes)
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['b2'] = np.zeros(num_classes)

        self.reg = reg
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        layer_1, cache_1 = affine_relu_forward(
            X, self.params['W1'], self.params['b1'])
        layer_2, cache_2 = affine_relu_forward(
            layer_1, self.params['W2'], self.params['b2'])
        scores = layer_2
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dscores = softmax_loss(scores, y)
        reg_loss = 0.0
        # Don't regularize bias terms
        reg_loss += np.sum(np.square(self.params['W1']))
        reg_loss += np.sum(np.square(self.params['W2']))

        loss += reg_loss * 0.5 * self.reg

        dx2, dw2, db2 = affine_relu_backward(dscores, cache_2)
        dx1, dw1, db1 = affine_relu_backward(dx2, cache_1)

        dw1 += self.reg * self.params['W1']
        dw2 += self.reg * self.params['W2']

        grads['W1'] = dw1
        grads['W2'] = dw2
        grads['b1'] = db1
        grads['b2'] = db2
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3 * 32 * 32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        pr_num = input_dim

        # can't use enumerate beacuse I need the number more than the size of hidden_dims
        for layer in range(self.num_layers):
            layer += 1
            weights = 'W' + str(layer)
            bias = 'b' + str(layer)

            # 这时候是最后一层(the last layer)
            if layer == self.num_layers:
                self.params[weights] = np.random.randn(
                    hidden_dims[len(hidden_dims) - 1], num_classes) * weight_scale
                self.params[bias] = np.zeros(num_classes)

                # other layers
            else:
                hidd_num = hidden_dims[layer - 1]
                self.params[weights] = np.random.randn(
                    pr_num, hidd_num) * weight_scale
                self.params[bias] = np.zeros(hidd_num)
                pr_num = hidd_num

                if self.normalization in ["batchnorm", "layernorm"]:
                    self.params['gamma' + str(layer)] = np.ones(hidd_num)
                    self.params['beta' + str(layer)] = np.zeros(hidd_num)

        # print(len(self.params))
        # print(self.params)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization == 'batchnorm':
            self.bn_params = [{'mode': 'train'}
                              for i in range(self.num_layers - 1)]
        if self.normalization in ["batchnorm", "layernorm"]:
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization == 'batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        cache = {}
        temp_out = X
        for i in range(self.num_layers):
            w = self.params['W' + str(i + 1)]
            b = self.params['b' + str(i + 1)]
            if i == self.num_layers - 1:
                scores, cache['cache' +
                              str(i + 1)] = affine_forward(temp_out, w, b)
            else:
                if self.normalization in ["batchnorm", "layernorm"]:
                    gamma = self.params['gamma' + str(i + 1)]
                    beta = self.params['beta' + str(i + 1)]
                    temp_out, cache['cache' + str(i + 1)] = self.affine_Normal_relu_dropout_forward(
                        temp_out, w, b, self.normalization, gamma, beta, self.bn_params[i])
                else:
                    # temp_out, cache['cache' +
                    #                 str(i + 1)] = affine_relu_forward(temp_out, w, b)
                    temp_out, cache['cache' + str(i + 1)] = self.affine_Normal_relu_dropout_forward(
                        temp_out, w, b, mode=self.normalization)

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale#
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dscores = softmax_loss(scores, y)
        reg_loss = 0.0
        pre_dx = dscores
        # dgamma = self.params['gamma']

        for i in reversed(range(self.num_layers)):
            i = i + 1
            reg_loss = np.sum(np.square(self.params['W' + str(i)]))
            loss += reg_loss * 0.5 * self.reg

            # 最后一层
            if i == self.num_layers:
                pre_dx, dw, db = affine_backward(
                    pre_dx, cache['cache' + str(i)])
            else:
                if self.normalization in ["batchnorm", "layernorm"]:
                    pre_dx, dw, db, dgamma, dbeta = self.affine_Normal_relu_dropout_backward(
                        pre_dx, cache['cache' + str(i)], self.normalization)
                    grads['gamma' + str(i)] = dgamma
                    grads['beta' + str(i)] = dbeta
                else:
                    pre_dx, dw, db, _, _ = self.affine_Normal_relu_dropout_backward(
                        pre_dx, cache['cache' + str(i)], self.normalization)

            dw += self.reg * self.params['W' + str(i)]
            db += self.reg * self.params['b' + str(i)]
            grads['W' + str(i)] = dw
            grads['b' + str(i)] = db

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads

    def affine_Normal_relu_dropout_forward(self, x, w, b, mode, gamma=None, beta=None, bn_params=None):
        Normal_cache = None
        dp_cache = None
        a, fc_cache = affine_forward(x, w, b)
        if mode == "batchnorm":
            mid, Normal_cache = batchnorm_forward(a, gamma, beta, bn_params)
        elif mode == "layernorm":
            mid, Normal_cache = layernorm_forward(a, gamma, beta, bn_params)
        else:
            mid = a

        dp, relu_cache = relu_forward(mid)
        if self.use_dropout:
            out, dp_cache = dropout_forward(dp, self.dropout_param)
        else:
            out = dp
        cache = (fc_cache, Normal_cache, relu_cache, dp_cache)

        return out, cache

    def affine_Normal_relu_dropout_backward(self, dout, cache, mode):
        fc_cache, Normal_cache, relu_cache, dp_cache = cache
        dgamma = 0.0
        dbeta = 0.0
        if self.use_dropout:
            ddp = dropout_backward(dout, dp_cache)
        else:
            ddp = dout
        da = relu_backward(ddp, relu_cache)
        if mode == "batchnorm":
            dmid, dgamma, dbeta = batchnorm_backward_alt(da, Normal_cache)
        elif mode == "layernorm":
            dmid, dgamma, dbeta = layernorm_backward(da, Normal_cache)
        else:
            dmid = da
        dx, dw, db = affine_backward(dmid, fc_cache)

        return dx, dw, db, dgamma, dbeta