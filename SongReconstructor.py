import numpy
import scipy.io.wavfile as sciwav
import greedy_tsp
import random
import os

# This piece of code takes a wave file and reconstructed it in a new fashion based on the following steps:
# 1. take a song segment and break the wav file into parts of 100 ms each
# 2. transform each part to the frequency domain using FFT
# 3. calculate the euclidean distance between every pair of parts
# 4. build a weighted graph where the nodes are the parts original location and the edges are the distance between them
# 5. calculate the Hamiltonian path of the graph
# 6. reconstruct the wave file based on the order of the path

class SongReconstructor():
    
    def __init__(self, sound_data, sample_rate, time_window, nsamples_crossover):
        self.nsamples_crossover = nsamples_crossover
        self.stereo_data = sound_data
        self.sample_rate = sr
        self.nparts = int(len(sound_data)/(time_window*sample_rate))
        self.mono_data = self.convert_to_mono()
        self.stereo_parts = self.deconstruct_stereo()
        self.mono_parts = self.deconstruct_mono()
        self.fft = self.transform_parts()
        self.distance_matrix = self.distance_matrix()
        self.new_order = self.compute_tsp()
        self.new_stereo_data = self.reconstruct()
        
    def convert_to_mono(self):
        return (self.stereo_data[:,0] + self.stereo_data[:,1]) / 2
        
    def deconstruct_stereo(self):
        stereo_parts = list()
        part_length = len(self.stereo_data) /self.nparts
        for i in range(self.nparts):
            start = i*part_length
            end = (i+1)*part_length
            stereo_parts.append(self.stereo_data[start:end])
        return stereo_parts
            
    def deconstruct_mono(self):
        mono_parts = list()
        part_length = len(self.mono_data) /self.nparts
        for i in range(self.nparts):
            start = i*part_length
            end = (i+1)*part_length
            mono_parts.append(self.mono_data[start:end])
        return mono_parts
            
    def transform_parts(self):
        all_parts_fft = list()
        for i in range(self.nparts):
            fft = numpy.fft.rfft(self.mono_parts[i])
            #fft_normalized = fft / range(1, len(fft) + 1)
            all_parts_fft.append(fft)
        return all_parts_fft
            
    def distance_matrix(self):
        distance_matrix = numpy.zeros(self.nparts*self.nparts).reshape((self.nparts,self.nparts))
        for i in range(self.nparts):
            for j in range(self.nparts):
                dist_vec = abs(self.fft[i] - self.fft[j])
                dist = numpy.linalg.norm(dist_vec,1)
                distance_matrix[i,j] = dist
        return distance_matrix
                
    def compute_tsp(self):
        path = greedy_tsp.solve_tsp_numpy(self.distance_matrix)
        return path
    
    def compute_random_path(self):
        path = range(self.nparts)
        random.shuffle(path)
        return path
            
    def reconstruct(self):
        nsamples_crossover = self.nsamples_crossover
        new_data = numpy.zeros((nsamples_crossover, 2), dtype = self.stereo_data.dtype)
        fade_in = [x * 1/float(nsamples_crossover) for x in range(nsamples_crossover)]
        fade_out = [x * 1/float(nsamples_crossover) for x in range(nsamples_crossover)]
        fade_out.reverse()
        nparts_to_add = 0

        ##add new part
        for i in range(self.nparts):
            new_part_ind = self.new_order[i]
            new_part = self.stereo_parts[new_part_ind]

            ##lengthen new part
            if (random.randint(i*2, self.nparts) > 0.98*self.nparts):
                nparts_to_add = nparts_to_add + 1 ##the parts become longer while the reconstruction proceeds
                
            for j in range(nparts_to_add):
                if (self.new_order[i] < self.nparts-j-1):
                    new_part = numpy.vstack([new_part, self.stereo_parts[new_part_ind+j+1]])
            
            [new_data_padded, new_part_padded] = self.pad_transition(new_data, new_part, nsamples_crossover, fade_in, fade_out)
            for k in range(nsamples_crossover):
                    new_data_padded[-nsamples_crossover+k] += new_part_padded[k]
            new_data = numpy.vstack([new_data_padded, new_part_padded[nsamples_crossover:,:]])

            if (new_part_ind < self.nparts*0.9 and new_part_ind > self.nparts*0.7 and nparts_to_add > 5):
                for h in range(new_part_ind+1, self.nparts):
                    new_data = numpy.vstack([new_data, self.stereo_parts[h]])
                return new_data
            
        return new_data
    
    def pad_transition(self, data, new_part, nsamples_fade, fade_in, fade_out):
        new_part[:nsamples_fade,0] *= fade_in
        new_part[:nsamples_fade,1] *= fade_in
        data[-nsamples_fade:,0] *= fade_out
        data[-nsamples_fade:,1] *= fade_out
        return [data, new_part]
    
        
file_shortname = 'Radiohead The National Anthem'
file_fullname = os.getcwd() + '/' + file_shortname + '.wav'
print file_fullname
[sr,old_wav] = sciwav.read(file_fullname)
time_window = 0.1
nsamples_crossover = 200
reconstructor = SongReconstructor(old_wav, sr, time_window, nsamples_crossover)

### assemble the parts into one wav file ###
new_filename = os.getcwd() + '/' + file_shortname + '_' + str(time_window) + '_' + 'reconstructed.wav'
sciwav.write(new_filename, sr, reconstructor.new_stereo_data)

