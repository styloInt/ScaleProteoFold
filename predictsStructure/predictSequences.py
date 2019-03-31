import numpy as np 
from parse import *
import keras
import keras.backend as K
from keras.models import Model
# Optimizer and regularization
from keras.regularizers import l2
from keras.losses import mean_squared_error, mean_absolute_error
from keras.models import Sequential, load_model, Model
# Keras layers
from keras.layers.convolutional import Conv1D
from keras.layers import Dense, Dropout, Flatten, Input, BatchNormalization, Activation
from keras.layers.pooling import MaxPooling1D, AveragePooling1D, MaxPooling2D, AveragePooling2D
# Models architectures
from modelsNetworks.elu_resnet_2d_distances import resnet_v2 as restnet_distance, softMaxAxis2, weighted_categorical_crossentropy
from modelsNetworks.resnet_1d_angles import resnet_v2 as resnet_angle, custom_mse_mae


# MODEL_DISTANCE = "models/old_distances/trained_models_h5/tester_28.h5"
MODEL_DISTANCE = "models/old_distances/elu_resnet_2d_distances.h5"
MODEL_ANGLE = "models/angles/resnet_1d_angles.h5"
SAVE_DIR = "predictsStructure/saveResults/"

key = "HRKDENQSYTCPAVLIGFWM"
key_map = {}
for index_key in range(len(key)):
    key_map[key[index_key]] = index_key

def computePSSM(seq):
    """
        Compute PSSM from primary sequence
        certainly an error
    """
    
    if len(seq) == 0:
        return None
    ppm = np.zeros((len(seq), len(key)))
    for i in range(len(seq)):
        ppm[i, key_map[seq[i]]] += 1
    

    ppm /= len(seq)
    return ppm.tolist()


def wider(seq, l=200, n=20):
    """ Converts a seq into a one-hot tensor. Not LxN but LxLxN"""
    key = "HRKDENQSYTCPAVLIGFWM"
    tensor = []
    for i in range(l):
        d2 = []
        for j in range(l):
            d1 = [1 if (j<len(seq) and i<len(seq) and key[x] == seq[i] and key[x] == seq[j]) else 0 for x in range(n)]
    
            d2.append(d1)
        tensor.append(d2)
    
    return np.array(tensor)

def wider_pssm(pssm, l=200, n=20):
    """ Converts a seq into a one-hot tensor. Not LxN but LxLxN"""
    tensor = []
    for i in range(l):
        d2 = []
        for j in range(l):
            if (j<len(seq) and i<len(seq) and key[x] == seq[i] and key[x] == seq[j]):
                d1 = [aa[i] for aa in pssm]
            else:
                d1 = [0 for i in range(n)]
    
            d2.append(d1)
        tensor.append(d2)
    
    return np.array(tensor)

# Length of masking - 17x2 AAs
def onehotter_aa(seq):
    pad = 17
    # Pad sequence
    key = "HRKDENQSYTCPAVLIGFWM"
    # Van der Waals radius
    vdw_radius = {"H": 118, "R": 148, "K": 135, "D": 91, "E": 109, "N": 96, "Q": 114,
                  "S": 73, "Y": 141, "T": 93, "C": 86, "P": 90, "A": 67, "V": 105,
                  "L": 124, "I": 124, "G": 48, "F": 135, "W": 163, "M": 124}
    radius_rel = vdw_radius.values()
    basis = min(radius_rel)/max(radius_rel)
    # Surface exposure 
    surface = {"H": 151, "R": 196, "K": 167, "D": 106, "E": 138, "N": 113, "Q": 144,
                  "S": 80, "Y": 187, "T": 102, "C": 104, "P": 105, "A": 67, "V": 117,
                  "L": 137, "I": 140, "G": 0, "F": 175, "W": 217, "M": 160}
    surface_rel = surface.values()
    surface_basis = min(surface_rel)/max(surface_rel)
    # One-hot encoding
    one_hot = []
    for i in range(0, len(seq)): # alponer los guiones ya tiramos la seq para un lado
        vec = [0 for i in range(22)]
        # mark as 1 the corresponding indexes
        for j in range(len(key)):
            if seq[i] == key[j]:
                vec[j] = 1
                # Add Van der Waals relative radius
                vec[-2] = vdw_radius[key[j]]/max(radius_rel)-basis
                vec[-1] = surface[key[j]]/max(surface_rel)-surface_basis
        
        one_hot.append(vec) 
    
    return np.array(one_hot)

def get_input_network_distance(primary_sequence, ppsms):
    inputs_aa = np.array(wider(seq))
    inputs_pssm = np.array(wider(pssms))

    return np.expand_dims(np.concatenate((inputs_aa, inputs_pssm), axis=2), 0)

def get_input_network_angle(primary_sequence, pssms):
    inputs_onehot = onehotter_aa(primary_sequence)
    # Concatenate input features
    pssms = np.array(pssms)
    print("Shape inputs_onehot : {}".format(inputs_onehot.shape))
    print("Shape pssm : {}".format(pssms.shape))
    inputs = np.concatenate((inputs_onehot[:, :20], pssms, inputs_onehot[:, 20:]), axis=1) 
    return np.expand_dims(inputs, 0)


step = 100
if __name__ == '__main__':

	# pass the name of the file you want ti convert to primary
    if(len(sys.argv)>1):

        # Load the sequence : 
        primary_sequence = ARN_TO_PRIMARY(sys.argv[1])
        # primary_sequences = []
        # for index_step in range(0, len(primary_sequence), step):
        #     primary_sequences.append(primary_sequence[index_step:index_step+step])
        #Compute SSM Matrix

        primary_sequence_flat = "".join(primary_sequence)
        pssms = computePSSM(primary_sequence_flat)
        # Load distance model and predict the distance
        # model_distance = restnet_distance(input_shape=(200,200, 42), depth=28, num_classes=7)
        model_distance = load_model(MODEL_DISTANCE,
                   custom_objects={'loss': weighted_categorical_crossentropy(np.array([0.0001,1.5,2,1.5,1,1,1])),
                                  'softMaxAxis2': softMaxAxis2})

        #L Load angle model and predict the angle
        # model_angle = resnet_angle(input_shape=(17*2,42), depth=20, num_classes=4, conv_first=True)
        model_angle = load_model(MODEL_ANGLE,
                   custom_objects={'custom_mse_mae': custom_mse_mae})

        size_sequence = 34
        # angle_predictions = []
        # distances_prediction = []
        for pos_sequence in range(0, len(primary_sequence_flat), size_sequence):
            print("Predicting pos sequence : {}".format(pos_sequence))
            seq = primary_sequence_flat[pos_sequence:pos_sequence+size_sequence]
            pssm_croped = pssms[:][pos_sequence:pos_sequence+size_sequence]
            inputs_distance = get_input_network_distance(seq, pssm_croped)
            inputs_angles = get_input_network_angle(seq, pssm_croped)

            angle_predictions = model_angle.predict(inputs_angles)
            distances_prediction = model_distance.predict(inputs_distance)
            np.save(SAVE_DIR + "angle_seq_pos_{}".format(pos_sequence), angle_predictions)
            np.save(SAVE_DIR + "distances_seq_pos_{}".format(pos_sequence), distances_prediction)

            print("Shape inputs_aa.shape : {}".format(inputs_angles.shape))
            print(angle_predictions)
    else :
        print("Non file given")

    
    print ("Angle predictions : {}".format(angle_predictions))