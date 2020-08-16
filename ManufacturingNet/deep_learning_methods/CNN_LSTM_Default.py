# Importing all the necessary files and functions

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.optim.lr_scheduler as scheduler
import torch.utils.data as data
from sklearn.model_selection import train_test_split
import time
import matplotlib.pyplot as plt


# The following class is used to create necessary inputs for dataset class and dataloader class used during training process
class ModelDataset():

    def __init__(self, X, Y, batchsize, valset_size, shuffle):

        self.x = X                      # Inputs
        self.y = Y                      # Labels
        self.batchsize = batchsize 
        self.valset_size = valset_size
        self.shuffle = shuffle
        self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(self.x, self.y, test_size = self.valset_size, shuffle = self.shuffle)
    
    def get_trainset(self):

        # Method for getting training set inputs and labels

        return self.x_train, self.y_train

    def get_valset(self):

        # Method for getting validation set inputs and labels

        return self.x_val, self.y_val

    def get_batchsize(self):

        # Method for getting batch size for training and validatioin

        return self.batchsize


# The following class is used for creating a dataset class using torch functionality. Its a standard pytorch class
class Dataset(data.Dataset):

    def __init__(self, X, Y):

        self.X = X
        self.Y = Y

    def __len__(self):

        return len(self.Y)

    def __getitem__(self,index):

        x_item = torch.from_numpy(self.X[index]).double()
        y_item = torch.from_numpy(np.array(self.Y[index]))

        return x_item, y_item


def conv2D_output_size(img_size, padding, kernel_size, stride, pool=2):
    # compute output shape of conv2D
    outshape = (np.floor(((img_size[0] + 2 * padding[0] - (kernel_size[0] - 1) - 1) / stride[0] + 1)).astype(int),
                np.floor(((img_size[1] + 2 * padding[1] - (kernel_size[1] - 1) - 1) / stride[1] + 1)).astype(int))
    return outshape

# The function that handles size if pooling layer is applied
def conv2D_pool_size(img_size,pool_size,stride):
  outshape = (np.floor(((img_size[0] - (pool_size[0] - 1) - 1) / stride[0] + 1)).astype(int),
                np.floor(((img_size[1] - (pool_size[1] - 1) - 1) / stride[1] + 1)).astype(int))
  return outshape

# This is class that creates a CNN block based on the parameters that the user defines. The block is called repeatedly CNN2D class  
class CNNBlock(nn.Module):

  def __init__(self, in_channels, out_channels, kernel_size,stride,padding, pool_size, pool_stride,batch_norm = True ,last = False,pooling = False):
      super(CNNBlock, self).__init__()
      self.in_channels = in_channels
      self.out_channels = out_channels
      self.kernel_size = kernel_size
      self.stride = stride
      self.padding = padding
      self.last = last
      self.pooling = pooling
      self.batch_norm = batch_norm
      self.conv1 = nn.Conv2d(in_channels= in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding)
      self.relu = nn.ReLU(inplace=True)
      if self.batch_norm == True:
        self.bn1 = nn.BatchNorm2d(out_channels)
      if self.pooling ==True:
        self.pool = nn.MaxPool2d(pool_size,pool_stride)

  def forward(self, x):

      out = self.conv1(x)
      if self.batch_norm == True:
        out = self.bn1(out)
      out = self.relu(out)
      if self.pooling ==True:
        out = self.pool(out)
      if self.last ==True:
        out = out.view(out.size(0), -1)
      return out
# 2D CNN train from scratch (no transfer learning)
# This is the main code used to create the CNN network. The object of this class will be passed to the to the another class to develop a complete model
class CNN2D(nn.Module):
  def __init__(self,block):
    super(CNN2D, self).__init__()
    self.block = block

    print("="*25)
    print('')
    print('Convolutional Neural Network')
    print('')

    print('1/18 - Get Image Size')
    self.img_x,self.img_y = self.get_image_size()
    print("Image: ",(self.img_y),(self.img_y))
    print("="*25)
    
    print('2/18 - Number of Convolutions')
    self.n_conv = self.get_number_convolutions()
    print("Convolutions: ", self.n_conv)
    print("="*25)

    print('3/18 - Channels')
    self.channels = self.get_channels(self.n_conv)
    print("Channels: ", self.channels)
    print("="*25)

    print('4/18 - Kernels')
    self.kernel_size = self.get_kernel_size(self.n_conv)
    print("Kernel sizes: ", self.kernel_size)
    print("="*25)

    print('5/18 - Padding and Stride')
    self.padding,self.stride =  self.get_stride_padding(self.n_conv)
    print("Padding: ", self.padding)
    print("Stride: ", self.stride)
    print("="*25)

    print("6/18 - Dropout")
    self.drop = self.get_dropout()
    print('Dropout ratio: ', self.drop)
    print("="*25)
    
    print("7/18 - Max Pooling")
    self.pooling_list,self.pooling_size,self.pooling_stride = self.get_pooling(self.n_conv)
    print("Pooling Layers: ", self.pooling_list)
    print("Pooling Size: ", self.pooling_size)
    print("Pooling Stride", self.pool_stride)
    print("="*25)

    print("8/18 - Batch Normalization")
    self.batch_normalization_list = self.get_batch_norm(self.n_conv)
    print("Batch normalization", self.batch_normalization_list)
    print("="*25)

    self.make_CNN(self.block,self.n_conv,self.pooling_list, self.drop,self.batch_normalization_list)

  def get_image_size(self): # Get image size as the input from user
    gate = 0
    while gate!=1:
      self.img_x = (input("Please enter the image width: "))
      self.img_y = (input("Please enter the image height: "))
      if (self.img_x.isnumeric() and int(self.img_x) >0) and (self.img_y.isnumeric() and int(self.img_y) >0):
        gate =1 
      else:
        gate = 0
        print("Please enter valid numeric output")
    return int(self.img_x),int(self.img_y)

  def get_number_convolutions(self): # Get number of convolutions as imput from user
    gate = 0
    while gate!=1:
      self.n_conv = (input("Please enter the number of convolutions: "))
      if (self.n_conv.isnumeric() and int(self.n_conv) > 0):
        gate = 1
      else:
        gate = 0
        print("Please enter valid number of convolutions.  The value must be an integer and greater than zero")
    return int(self.n_conv)

  def get_channels(self,n_conv):# Get the number of convolutions
    gate = 0
    self.channels = []
    while gate!=1:
      for i in range(n_conv+1):
        channel = ((input("enter the number of channels: ")))
        if (channel.isnumeric() and int(channel) > 0) :
          self.channels.append(int(channel))
          if i == n_conv:
            gate = 1
        else:
          gate =0
          print("Please enter valid number of channels.  The value must be an integer and greater than zero")
        
    return self.channels

  def get_kernel_size(self,n_conv): # Get the kernel size
    gate1 = 0 
    value = input("Do you want default values for kernel size(press y or n): ")
    while gate1!=1:
      if value!= "Y" or value!="y" or value!= 'n' or value!= 'N':
        gate1 = 1
      else:
        print("Please enter valid input it should only be (y or n)")
        value = input("Do you want default values for kernel size(press y or n)")
        gate1 =0 

    gate2 = 0
    self.kernel_list = []
    while gate2!=1:
      for i in range(n_conv):
        if value == 'N' or value =='n':
          k_size = (((input("Enter the kernel size \n For Example: 3,3: "))))
          k_split = k_size.split(",")
          if k_split[0].isnumeric() and int(k_split[0]) > 0 and k_split[1].isnumeric() and int(k_split[0]) > 0:
            self.kernel_list.append((int(k_split[0]),int(k_split[1])))
            if i == n_conv-1:
              gate2 = 1
          else:
            gate2 = 0
            print("Please enter valid numeric values.  The value must be an integer and greater than zero")
            break
          
        else:
          self.kernel_list.append((3,3))
          if i == n_conv-1:
            gate2 = 1
    return self.kernel_list
  
  def get_stride_padding(self,n_conv): # Get the stride and padding
    self.padding = []
    self.stride = []
    gate1 = 0 
    value = input("Do you want default values for padding and stride (press y or n): ")
    while gate1!=1:
      if (value!= "Y" or value!="y" or value!= 'n' or value!= 'N'):
        gate1 = 1
      else:
        print("Please enter valid input it should only be (y or n)")
        value = input("Do you want default values for padding and stride(press y or n): ")
        gate1 =0

    gate2 = 0
    while gate2!=1:
      for i in range(n_conv):
        if value == 'N' or value =='n':
          pad_size = input("Enter padding for the image \n For Example 2,2: ")
          pad_split = pad_size.split(",")
          if pad_split[0].isnumeric() and int(pad_split[0]) >= 0 and pad_split[1].isnumeric() and int(pad_split[0]) >= 0:
            self.padding.append((int(pad_split[0]),int(pad_split[1])))
            if i == n_conv-1:
              gate2 = 1
          else:
            gate2 = 0
            print("Please enter valid numeric values.  The value must be an integer and greater than or equal to zero")
            break
        else:
          self.padding.append((0,0))
          if i == n_conv-1:
            gate2 =1
          
    gate3 = 0
    while gate3!=1:
      for i in range(n_conv):
        if value == 'N' or value == 'n':
          stride_size = input("Enter stride for the convolutions \n For Example 2,2: ")
          stride_split = stride_size.split(",")
          if stride_split[0].isnumeric() and int(stride_split[0]) >= 0 and stride_split[1].isnumeric() and int(stride_split[0]) >= 0:
            self.stride.append((int(stride_split[0]),int(stride_split[1])))
            if i ==n_conv-1:
              gate3 = 1
          else:
            gate3 = 0
            print("Please enter valid numeric values.  The value must be an integer and greater than zero")
            break
        else:
          self.stride.append((1,1))
          if i == n_conv-1:
            gate3 =1
    return self.padding, self.stride 

  def get_batch_norm(self,n_conv): # Get input for batch normalization
    gate1 = 0 
    value = input("Do you want default values for batch normalization (press y or n): ")
    while gate1!=1:
      if (value!= "Y" or value!="y" or value!= 'n' or value!= 'N'):
        gate1 = 1
      else:
        print("Please enter valid input it should only be (y or n)")
        value = input("Do you want default values for batch normalization (press y or n): ")
        gate1 =0

    self.batch_norm = []
    
    gate2 = 0
    while gate2!=1:
      for i in range(n_conv):
        if value == "N" or value =='n':
          b_n = (input("Please enter 1 or 0 depending on whether you want batch normalisation"))
          if (b_n.isnumeric() and (int(b_n) ==0 or int(b_n)==1)) :
            self.batch_norm.append(int(b_n))
            if i == n_conv-1:
              gate2 =1 
          else:
            gate2 = 0
            print("Please enter valid numeric values")
            break                    
        else:
          if i <2:
            self.batch_norm.append(1)
          else:
            self.batch_norm.append(0)

      return self.batch_norm

  def get_dropout(self): # Get input for dropout from the user
    gate1 = 0 
    value = input("Do you want default values for dropout(press y or n): ")
    while gate1!=1:
      if value!= "Y" or value!="y" or value!= 'n' or value!= 'N':
        gate1 = 1
      else:
        print("Please enter valid input it should only be (y or n)")
        value = input("Do you want default values for dropout(press y or n)")
        gate1 =0 

    gate  = 0    
    if value == 'N' or value =='n':    
      drop_out = (input(("Please input the dropout probability: ")))
      while gate!=1:
        if (float(drop_out) > 0 and float(drop_out)<1):
          self.drop = drop_out
          gate  = 1
        else:
          print("Please enter the valid numeric values. The value should lie between 0 and 1")
          drop_out = (input(("Please input the dropout probability")))
          gate = 0
    else:
      self.drop = 0

    return float(self.drop)
  
  def get_pooling(self,n_conv): # get input for pooling from the user
    gate1 = 0 
    value = value = input("Do you want default pooling values (press y or n): ")
    while gate1!=1:
      if value!= "Y" or value!="y" or value!= 'n' or value!= 'N':
        gate1 = 1
      else:
        print("Please enter valid input it should only be (y or n)")
        value = input("Do you want default pooling values (press y or n): ")
        gate1 =0
    
    gate2 = 0
    self.pool_bool = []
    self.pool_size = []
    self.pool_stride = []
    while gate2!=1:
      for i in range(n_conv):
        if value == "N" or value =='n':
          pool_boolean = (input("Please enter 0(No) or 1(yes) for pooling: "))
          if (pool_boolean.isnumeric() and (int(pool_boolean) ==0 or int(pool_boolean)==1)):
            self.pool_bool.append(int(pool_boolean))
            if i == n_conv-1:
              gate2 = 1
          else:
            gate2 = 0
            print("Please enter valid numeric values")
        elif (value == "Y" or value =='y' ):
          if i <= n_conv -2:
            self.pool_bool.append(0)
          elif i > n_conv-2:
            self.pool_bool.append(1)
            if i == n_conv-1:
              gate2 = 1
    
    gate3 = 0
    while gate3!=1:
      for i in range (len(self.pool_bool)):
        if value == 'N' or value =='n':
          if self.pool_bool[i] == 0:
            self.pool_size.append((0,0))
            gate3 = 1
          else:
            pooling_size = input("Please enter pool size \n For example 2,2: ")
            pooling_size_split = pooling_size.split(',')
            if (pooling_size_split[0].isnumeric() and int(pooling_size_split[0])>0 and pooling_size_split[1].isnumeric() and int(pooling_size_split[1]) >0) :
              self.pool_size.append((int(pooling_size_split[0]), int(pooling_size_split[1])))
              if i == len(self.pool_bool) -1 :
                gate3 =1
            else:
              gate3 =0
              print("please enter valid numeric values. The value must be an integer and greater than zero")
        else:
          self.pool_size.append((2,2))
          if i == len(self.pool_bool) -1:
            gate3 = 1

    gate4 = 0
    while gate4!=1:
      for i in range (len(self.pool_bool)):
        if value == 'N' or value =='n':
          if self.pool_bool[i] == 0:
            self.pool_stride.append((0,0))
            gate4 = 1
          else:
            pooling_stride = input("Please enter pool stride \n For example 2,2: ")
            pooling_stride_split = pooling_stride.split(',')
            if (pooling_stride_split[0].isnumeric() and int(pooling_stride_split[0])>0 and pooling_stride_split[1].isnumeric() and int(pooling_stride_split[1]) >0) :
              self.pool_stride.append((int(pooling_stride_split[0]), int(pooling_stride_split[1])))
              if i == len(self.pool_bool) -1 :
                gate4 =1
            else:
              gate4 =0
              print("please enter valid numeric values. The value must be an integer and greater than zero")
        else:
          self.pool_stride.append((2,2))
          if i == len(self.pool_bool) -1:
            gate4 =1

    return self.pool_bool,self.pool_size, self.pool_stride

  def make_CNN(self,block,n_conv,pool_list,drop,batch_norm_list): # Makes the CNN with forward pass
    layers = []
    for i in range(n_conv):
      if pool_list[i] == 0:
        if i < n_conv-1:
          if batch_norm_list[i] == 0:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i], batch_norm = False,last =False,pooling =False))
          else:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i], batch_norm = True,last =False,pooling =False))
        else:
          if batch_norm_list[i] == 0:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i],batch_norm = False,last =True,pooling =False))
          else:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i],batch_norm = True,last =True,pooling =False))
      else:
        if i < n_conv-1:
          if batch_norm_list[i] == 0:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i], batch_norm = False, last =False,pooling=True))
          else:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i], batch_norm = True, last =False,pooling=True))            
        else:
          if batch_norm_list[i] == 0:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i],batch_norm = False, last =True,pooling=True))
          else:
            layers.append(block(in_channels=self.channels[i], out_channels=self.channels[i+1], kernel_size=self.kernel_size[i], stride=self.stride[i], pool_size = self.pooling_size[i], pool_stride = self.pooling_stride[i], padding=self.padding[i],batch_norm = True, last =True,pooling=True))

    conv_shape = conv2D_output_size((self.img_x,self.img_y),self.padding[0],self.kernel_size[0],self.stride[0])
    shape = [conv_shape]
    #print(pool_list)
    if len(pool_list)==1 and pool_list[0]==1:
      conv_shape_pool = conv2D_pool_size(shape[0],self.pooling_size[0],self.pooling_stride[0])
      shape.append(conv_shape_pool)
    for i in range(1,n_conv):
      if pool_list[i] == 1:
        conv_shape_rep = conv2D_output_size(shape[i-1], self.padding[i], self.kernel_size[i], self.stride[i])
        conv_shape_pool = conv2D_pool_size(conv_shape_rep, self.pooling_size[i], self.pooling_stride[i])
        shape.append(conv_shape_pool)
      else:
        conv_shape_rep = conv2D_output_size(shape[i-1], self.padding[i], self.kernel_size[i], self.stride[i])
        shape.append(conv_shape_rep)
    print("Shapes after the Convolutions", shape)
    print("="*25)

    self.linear_size = self.channels[-1] * shape[-1][0] * shape[-1][1]

    self.ConvNet = nn.Sequential(*layers)
  
  def forward(self,x):
      x = self.ConvNet(x)
      x = x.view(x.shape[0],-1)   
      return x 

# The following class builds an LSTM network
class LSTM(nn.Module):

    def __init__(self, input_size):
        
        super(LSTM, self).__init__()

        self.cnn_flatten = input_size # flattened output shape passed in from CNN
   
        self._get_input_size()

        print('')
        print('LSTM Network')
        print('')

        print('='*25)
        print('9/18 - LSTM hidden size')
        self._get_hidden_size()

        print('='*25)
        print('10/18 - LSTM number of layers')
        self._get_num_layers()

        print('='*25)
        print('11/18 - LSTM bidirectional')
        self. _get_bidirectional()

        print('='*25)
        print('12/18 - LSTM output size')
        self. _get_output_size()

        self._build_network_architecture()
         

    def _get_input_size(self):

        # Method for getting an input size parameter for the LSTM network

        self.input_size = self.cnn_flatten

    def _get_hidden_size(self):

        # Method for getting an hidden size parameter for the LSTM network

        gate = 0
        while gate!= 1:
            self.hidden_size = (input('Please enter the hidden size for the LSTM network \n For default size, please directly press enter without any input: '))
            if self.hidden_size == '':              # handling default case for hidden size
                print('Default value selected')
                self.hidden_size = '256'
            if self.hidden_size.isnumeric() and int(self.hidden_size) >0 :
                self.hidden_size = int(self.hidden_size)
                gate = 1
            else:
                print('Please enter a valid input')

    def _get_num_layers(self):

        # Method for getting a number of LSTM layer parameter for the LSTM network

        gate = 0
        while gate!= 1:
            self.nlayers = (input('Please enter the number of layer for the LSTM network \n For default option, please directly press enter without any input: '))
            if self.nlayers == '':              # handling default case for number of LSTM layer
                print('Default value selected')
                self.nlayers = '3'
            if self.nlayers.isnumeric() and int(self.nlayers) >0 :
                self.nlayers = int(self.nlayers)
                gate = 1
            else:
                print('Please enter a valid input')
    
    def _get_bidirectional(self):

        # Method for getting bidirectional input for the LSTM network

        gate = 0
        while gate!= 1:
            self.bidirection = input('Please enter 1 to have a bidirectional LSTM network else enter 0 \n For default option, please directly press enter without any input: ')
            if self.bidirection == '':
                print('Default value selected')
                self.bidirection = '0'
            if self.bidirection.isnumeric() and int(self.bidirection) > -1 and int(self.bidirection) < 2:
                if self.bidirection == '1':
                    self.bidirection_input = True
                else:
                    self.bidirection_input = False
                gate = 1
            else:
                print('Please enter a valid input')
    
    def _get_output_size(self):

        # Method for getting output size of the network
        gate = 0
        while gate!= 1:
            self.output_size = (input('Please enter the output size for the LSTM network. \n For regression please enter 1 else enter the number of classes for classification problem: '))
            if self.output_size.isnumeric() and int(self.output_size) >0 :
                self.output_size = int(self.output_size)
                gate = 1
            else:
                print('Please enter a valid input')

    def _build_network_architecture(self):

        # Method for building a network using all the information provided by a user in above functions
        self.lstm = nn.LSTM(self.input_size, self.hidden_size, bidirectional = self.bidirection_input, num_layers = self.nlayers, batch_first = True)
        if self.bidirection_input:
            self.linear_input = self.hidden_size*2
        else:
            self.linear_input = self.hidden_size
        self.linear1 = nn.Linear(self.linear_input, int(self.linear_input/2))
        self.linear2 = nn.Linear(int(self.linear_input/2), int(self.linear_input/4))
        self.linear3 = nn.Linear(int(self.linear_input/4), self.output_size)

    
    def forward(self, x):
        out,_ = self.lstm(x)
        out = self.linear1(out[:,-1,:])
        out = self.linear2(out)
        out = self.linear3(out)

        return out
    
    
# Following class combines the CNN and LSTM network
class CNN_LSTM(nn.Module):

    def __init__(self, CNNNetwork, LSTMNetwork):
        super(CNN_LSTM, self).__init__()
        
        self.cnn = CNNNetwork
        
        self.lstm = LSTMNetwork

    def forward(self, x):
        
        b,num_channels,h,w = x.shape
        lstm_input = torch.zeros((b,num_channels,self.lstm.input_size)).double()
        for i in range(num_channels):
            lstm_input[:,i,:] = self.cnn.forward(x[:,i,:,:].reshape(b,1,h,w))
        
        output = self.lstm(lstm_input)
            
        return output
    
    def predict(self, x):

        b,num_channels,h,w = x.shape
        lstm_input = torch.zeros((b,num_channels,self.lstm.input_size)).double()
        for i in range(num_channels):
            lstm_input[:,i,:] = self.cnn.forward(x[:,i,:,:].reshape(b,1,h,w))
        
        output = self.lstm(lstm_input)
            
        return output


# The following class will be called by a user. The class calls other necessary classes to build a complete pipeline required for training
class CNNLSTMModel():
    """
    Documentation Link:

    """
    def __init__(self,X,Y, shuffle = True):

        # Lists used in the functions below
        self.criterion_list = {1:nn.CrossEntropyLoss(),2:torch.nn.L1Loss(),3:torch.nn.SmoothL1Loss(),4:torch.nn.MSELoss()}
        
        self.x_data = X
        self.y_data = Y
        self.shuffle = shuffle

        self.cnn_network = CNN2D(CNNBlock).double()           # building a network architecture

        self.lstm_network = LSTM(self.cnn_network.linear_size).double()

        self.net = CNN_LSTM(self.cnn_network, self.lstm_network)             # building a network architecture

        print('='*25)
        print('13/18 - Batch size input')
        self._get_batchsize_input()             # getting a batch size for training and validation

        print('='*25)
        print('14/18 - Validation set size')
        self._get_valsize_input()                # getting a train-validation split

        self.model_data = ModelDataset(self.x_data, self.y_data, batchsize = self.batchsize, valset_size = self.valset_size, shuffle = self.shuffle)          # splitting the data into training and validation sets

        print('='*25)
        print('15/18 - Loss function')
        self._get_loss_function()               # getting a loss function

        print('='*25)
        print('16/18 - Optimizer')
        self._get_optimizer()               # getting an optimizer input

        print('='*25)
        print('17/18 - Scheduler')
        self._get_scheduler()               # getting a scheduler input

        self._set_device()              # setting the device to gpu or cpu

        print('='*25)
        print('18/18 - Number of epochs')
        self._get_epoch()           # getting an input for number oftraining epochs

        self.main()             # run function
    
    def _get_batchsize_input(self):

        # Method for getting batch size input

        gate = 0
        while gate!= 1:
            self.batchsize = (input('Please enter the batch size: '))
            if self.batchsize.isnumeric() and int(self.batchsize) >0 :
                self.batchsize = int(self.batchsize)
                gate = 1
            else:
                print('Please enter a valid input')
    
    def _get_valsize_input(self):

        # Method for getting validation set size input
        
        gate = 0
        while gate!= 1:
            self.valset_size = (input('Please enter the validation set size (size > 0 and size < 1) \n For default size, please directly press enter without any input: '))
            if self.valset_size == '':              # handling default case for valsize
                print('Default value selected')
                self.valset_size = '0.2'
            if self.valset_size.replace('.','').isdigit() :
                if float(self.valset_size) >0 and float(self.valset_size) < 1 :
                    self.valset_size = float(self.valset_size)
                    gate = 1
            else:
                print('Please enter a valid input')
        
    def _get_loss_function(self):

        # Method for getting a loss function for training
        
        gate = 0
        while gate!= 1:
            self.criterion_input = (input('Please enter the appropriate loss function for the problem: \n Criterion_list - [1: CrossEntropyLoss, 2: L1Loss, 3: SmoothL1Loss, 4: MSELoss]: '))

            if self.criterion_input.isnumeric() and int(self.criterion_input) < 5 and int(self.criterion_input)> 0:
                gate = 1
            else:
                print('Please enter a valid input')
            
        self.criterion = self.criterion_list[int(self.criterion_input)]

    def _get_optimizer(self):

        # Method for getting a optimizer input

        gate = 0
        while gate!= 1:
            self.optimizer_input = (input('Please enter the optimizer for the problem \n Optimizer_list - [1: Adam, 2: SGD] \n For default optimizer, please directly press enter without any input: '))
            if self.optimizer_input == '':              # handling default case for optimizer
                print('Default optimizer selected')
                self.optimizer_input = '1'

            if self.optimizer_input.isnumeric() and int(self.optimizer_input) >0  and int(self.optimizer_input) < 3:
                gate = 1
            else:
                print('Please enter a valid input')
                
        gate = 0
        while gate!= 1:
            self.user_lr = input('Please enter a required postive value for learning rate \n For default learning rate, please directly press enter without any input: ')
            if self.user_lr == '':               # handling default case for learning rate
                print('Default value selected')
                self.user_lr = '0.001'
            if self.user_lr.replace('.','').isdigit():
                if float(self.user_lr) > 0:
                    self.lr = float(self.user_lr)
                    gate = 1
            else:
                print('Please enter a valid input')

        
        self.optimizer_list = {1:optim.Adam(self.net.parameters(),lr = self.lr), 2:optim.SGD(self.net.parameters(),lr = self.lr)}
        self.optimizer = self.optimizer_list[int(self.optimizer_input)]


    def _get_scheduler(self):

        # Method for getting scheduler

        gate = 0
        while gate!= 1:
            self.scheduler_input = input('Please enter the scheduler for the problem: Scheduler_list - [1: None, 2:StepLR, 3:MultiStepLR] \n For default option of no scheduler, please directly press enter without any input: ')
            if self.scheduler_input == '':
                print('By default no scheduler selected')
                self.scheduler_input = '1'
            if self.scheduler_input.isnumeric() and int(self.scheduler_input) >0  and int(self.scheduler_input) <4:
                gate = 1
            else:
                print('Please enter a valid input')
        
        if self.scheduler_input == '1':
            self.scheduler =  None

        elif self.scheduler_input == '2':
            gate = 0
            while gate!= 1:
                self.step = (input('Please enter a step value: '))
                if self.step.isnumeric() and int(self.step) >0 :
                    self.step = int(self.step)
                    gate = 1
                else:
                    print('Please enter a valid input')
            print(' ')
            gate = 0
            while gate!= 1:
                self.gamma = (input('Please enter a gamma value (Multiplying factor): '))
                if self.gamma.replace('.','').isdigit():
                    if float(self.gamma) >0 :
                        self.gamma = float(self.gamma)
                        gate = 1
                else:
                    print('Please enter a valid input')

            self.scheduler =  scheduler.StepLR(self.optimizer, step_size = self.step, gamma = self.gamma)

        elif self.scheduler_input == '3':
            gate = 0
            while gate != 1:
                self.milestones_input = (input('Please enter values of milestone epochs: '))
                self.milestones_input = self.milestones_input.split(',')
                for i in range(len(self.milestones_input)):
                    if self.milestones_input[i].isnumeric() and int(self.milestones_input[i]) >0 :
                        gate = 1
                    else:
                        gate = 0
                        break
                if gate == 0:
                    print('Please enter a valid input')
                    
            self.milestones = [int(x) for x in self.milestones_input if int(x)>0]
            print(' ')
            
            gate = 0
            while gate!= 1:
                self.gamma = (input('Please enter a gamma value (Multiplying factor): '))
                if self.gamma.replace('.','').isdigit():
                    if float(self.gamma) >0 :
                        self.gamma = float(self.gamma)
                        gate = 1
                else:
                    print('Please enter a valid input')
            self.scheduler =  scheduler.MultiStepLR(self.optimizer, milestones = self.milestones, gamma = self.gamma)
        
    def _set_device(self):

        # Method for setting device type if GPU is available

        if torch.cuda.is_available():
            self.device=torch.device('cuda')
        else:
            self.device=torch.device('cpu')

    def _get_epoch(self):

        # Method for getting number of epochs for training the model

        
        gate = 0
        while gate!= 1:
            self.numEpochs = (input('Please enter the number of epochs to train the model: '))
            if self.numEpochs.isnumeric() and int(self.numEpochs) >0 :
                self.numEpochs = int(self.numEpochs)
                gate =1
            else:
                print('Please enter a valid input')

    def main(self):

        # Method integrating all the functions and training the model

        self.net.to(self.device)
        print('='*25)

        print('Network architecture: ')
        print(' ')
        print(self.net)         # printing model architecture
        print('='*25)

        self.get_model_summary()        # printing summaray of the model
        print(' ')
        print('='*25)
        
        xt, yt = self.model_data.get_trainset()         # getting inputs and labels for training set

        xv, yv = self.model_data.get_valset()           # getting inputs and labels for validation set

        self.train_dataset = Dataset(xt, yt)            # creating the training dataset

        self.val_dataset = Dataset(xv, yv)              # creating the validation dataset

        self.train_loader = torch.utils.data.DataLoader(self.train_dataset, batch_size = self.model_data.get_batchsize(), shuffle = True)           # creating the training dataset dataloadet

        self.dev_loader = torch.utils.data.DataLoader(self.val_dataset, batch_size = self.model_data.get_batchsize())           # creating the validation dataset dataloader

        self.train_model()          # training the model

        self.get_loss_graph()           # saving the loss graph

        if self.criterion_input == '1':

            self.get_accuracy_graph()           # saving the accuracy graph

        self._save_model()              # saving model paramters

        print(' Call get_prediction() to make predictions on new data')
        print(' ')
        print('=== End of training ===')

    def _save_model(self):

        # Method for saving the model parameters if user wants to

        gate=0
        while gate  != 1:
            save_model = input('Do you want to save the model weights? (y/n): ')
            if save_model.lower() =='y' or save_model.lower() =='yes':
                path = 'model_parameters.pth'
                torch.save(self.net.state_dict(),path)
                gate = 1
            elif save_model.lower() =='n' or save_model.lower() =='no':
                gate = 1
            else:
                print('Please enter a valid input')
        print('='*25)
        
        
    def get_model_summary(self):

        # Method for getting the summary of the model
        print('Model Summary:')
        print(' ')
        print('Bidirectional: ', self.lstm_network.bidirection_input)
        print('Number of layer: ', self.lstm_network.nlayers)
        print('Criterion: ', self.criterion)
        print('Optimizer: ', self.optimizer)
        print('Scheduler: ', self.scheduler)
        print('Validation set size: ', self.valset_size)
        print('Batch size: ', self.batchsize)
        print('Initial learning rate: ', self.lr)
        print('Number of training epochs: ', self.numEpochs)
        print('Device: ', self.device)
    

    def train_model(self):

        # Method for training the model

        self.net.train()
        self.training_loss = []
        self.training_acc = []
        self.dev_loss = []
        self.dev_accuracy = []
        total_predictions = 0.0
        correct_predictions = 0.0

        print('Training the model...')

        for epoch in range(self.numEpochs):
            
            start_time = time.time()
            self.net.train()
            print('Epoch_Number: ',epoch)
            running_loss = 0.0
            

            for batch_idx, (data, target) in enumerate(self.train_loader):   

                self.optimizer.zero_grad()   
                data = data.to(self.device)
                target = target.to(self.device) 

                outputs = self.net(data)

                if self.criterion_input == '1':             # calculating the batch accuracy only if the loss function is Cross entropy

                    loss = self.criterion(outputs, target.long())
                    _, predicted = torch.max(outputs.data, 1)
                    total_predictions += target.size(0)
                    correct_predictions += (predicted == target).sum().item()

                else:

                    loss = self.criterion(outputs, target)
                
                running_loss += loss.item()
                loss.backward()
                self.optimizer.step()
        
            
            running_loss /= len(self.train_loader)              
            self.training_loss.append(running_loss)
            print('Training Loss: ', running_loss)

            if self.criterion_input == '1':             # printing the epoch accuracy only if the loss function is Cross entropy
                
                acc = (correct_predictions/total_predictions)*100.0
                self.training_acc.append(acc)
                print('Training Accuracy: ', acc, '%')

            dev_loss,dev_acc = self.validate_model()
    
            if self.scheduler_input != '1':

                self.scheduler.step()
                print('Current scheduler status: ', self.optimizer)
            
            end_time = time.time()
            print( 'Epoch Time: ',end_time - start_time, 's')
            print('#'*50)

            self.dev_loss.append(dev_loss)

            if self.criterion_input == '1':             # saving the epoch validation accuracy only if the loss function is Cross entropy
                
                self.dev_accuracy.append(dev_acc)
    

    def validate_model(self):

        with torch.no_grad():
            self.net.eval()
        running_loss = 0.0
        total_predictions = 0.0
        correct_predictions = 0.0
        acc = 0

        for batch_idx, (data, target) in enumerate(self.dev_loader): 

            data = data.to(self.device)
            target = target.to(self.device)
            outputs = self.net(data)

            if self.criterion_input == '1':

                loss = self.criterion(outputs, target.long())
                _, predicted = torch.max(outputs.data, 1)
                total_predictions += target.size(0)
                correct_predictions += (predicted == target).sum().item()

            else:
                loss = self.criterion(outputs, target)
            running_loss += loss.item()


        running_loss /= len(self.dev_loader)
        print('Validation Loss: ', running_loss)

        if self.criterion_input == '1':             # calculating and printing the epoch accuracy only if the loss function is Cross entropy
            
            acc = (correct_predictions/total_predictions)*100.0
            print('Validation Accuracy: ', acc, '%')
        
        return running_loss,acc

    def get_loss_graph(self):

        # Method for showing and saving the loss graph in the root directory

        plt.figure(figsize=(8,8))
        plt.plot(self.training_loss,label='Training Loss')
        plt.plot(self.dev_loss,label='Validation Loss')
        plt.legend()
        plt.title('Model Loss')
        plt.xlabel('Epochs')
        plt.ylabel('loss')
        plt.savefig('loss.png')
    
    def get_accuracy_graph(self):

        # Method for showing and saving the accuracy graph in the root directory

        plt.figure(figsize=(8,8))
        plt.plot(self.training_acc,label='Training Accuracy')
        plt.plot(self.dev_accuracy,label='Validation Accuracy')
        plt.legend()
        plt.title('Model accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('acc')
        plt.savefig('accuracy.png') 

    def get_prediction(self, x_input):

        """

        Pass in an input numpy array for making prediction.
        For passing multiple inputs, make sure to keep number of examples to be the first dimension of the input.
        For example, 5 data points need to be checked and each point has 14 input size, the shape of the array must be (5,14).
        For more information, please see documentation.

        """

        # Method to use at the time of inference

        if len(x_input.shape) == 3:             # handling the case of single
            
            x_input = (x_input).reshape(1,x_input.shape[0], x_input.shape[1], x_input.shape[3])
            
        x_input = torch.from_numpy(x_input).to(self.device)

        net_output = self.net.predict(x_input)

        if self.criterion_input == '1':             # handling the case of classification problem
            
            _, net_output = torch.max(net_output.data, 1)

        return net_output