import torch
import argparse
import numpy as np
import matplotlib.pylab as plt
from apis.tts.riri_tts.text import text_to_sequence
from apis.tts.riri_tts.model.model import Tacotron2
from apis.tts.riri_tts.hparams import hparams as hps
from apis.tts.riri_tts.utils.util import mode, to_arr
from apis.tts.riri_tts.utils.audio import save_wav, inv_melspectrogram
import torch
import os
from scipy.io.wavfile import write
from apex import amp



def load_model(ckpt_pth):
    ckpt_dict = torch.load(ckpt_pth, map_location=torch.device('cpu'))
    model = Tacotron2()
    model.load_state_dict(ckpt_dict['model'])
    # model.load_state_dict(ckpt)
    model = mode(model, False).eval()
    return model


def infer(text, model):
    sequence = text_to_sequence(text, hps.text_cleaners)
    sequence = mode(torch.IntTensor(sequence)[None, :]).long()
    mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
    return (mel_outputs, mel_outputs_postnet, alignments)


def plot_data(data, figsize = (16, 4)):
    fig, axes = plt.subplots(1, len(data), figsize = figsize)
    for i in range(len(data)):
        axes[i].imshow(data[i], aspect = 'auto', origin = 'lower')


def plot(output, pth):
    mel_outputs, mel_outputs_postnet, alignments = output
    plot_data((to_arr(mel_outputs[0]),
                to_arr(mel_outputs_postnet[0]),
                to_arr(alignments[0]).T))
    plt.savefig(pth+'.png')


def audio(output, pth):
    print(f"saving audio at {pth}")
    mel_outputs, mel_outputs_postnet, _ = output
    wav_postnet = inv_melspectrogram(to_arr(mel_outputs_postnet[0]))
    # print(wav_postnet,1111111111111111)
    save_wav(wav_postnet, pth+'.wav')


def save_mel(output, pth):
    mel_outputs, mel_outputs_postnet, _ = output
    np.save(pth+'.npy', to_arr(mel_outputs_postnet))

def save_waveglow(npy_ary,file_name, waveglow,sigma, output_dir, sampling_rate, is_fp16):
         # denoiser_strength):
    MAX_WAV_VALUE = 32768.0
    # path = "../waveglow/checkpoints/waveglow_24000"
    

    # if denoiser_strength > 0:
    #     denoiser = Denoiser(waveglow).cuda()

    # mel = torch.autograd.Variable(npy_ary.cuda())
    # mel = torch.autograd.Variable(mel.cuda())
    mel = torch.autograd.Variable(npy_ary)
    mel = torch.autograd.Variable(mel)
    # mel = torch.unsqueeze(mel, 0)
    mel = mel.half() if is_fp16 else mel
    with torch.no_grad():
        audio = waveglow.infer(mel, sigma=sigma)
        # if denoiser_strength > 0:
        #     audio = denoiser(audio, denoiser_strength)
        audio = audio * MAX_WAV_VALUE
    audio = audio.squeeze()
    audio = audio.cpu().numpy()
    audio = audio.astype('int16')
    audio_path = os.path.join(
        output_dir, "{}.wav".format(file_name))
    print(f"Saving audio at {audio_path}")
    write(audio_path, sampling_rate, audio)
    return audio_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--ckpt_pth', type = str, default = '',
                        required = True, help = 'path to load checkpoints')
    parser.add_argument('-f', '--filename', type = str, default = 'result',
                        help = 'text to synthesize')
    parser.add_argument('-i', '--img_pth', type = str, default = '',
                        help = 'path to save images')
    parser.add_argument('-o', '--output_dir', type = str, default = '', required=True,
                        help = 'path to save wavs')
    parser.add_argument('-n', '--npy_pth', type = str, default = '',
                        help = 'path to save mels')
    parser.add_argument('-t', '--text', type = str, default = 'Tacotron is awesome.',
                        help = 'text to synthesize')
    parser.add_argument('-w', '--waveglow_path',
                        help='Path to waveglow decoder checkpoint with model')
    # parser.add_argument('-o', "--output_dir", required=True)
    parser.add_argument("-s", "--sigma", default=1.0, type=float)

    parser.add_argument("--sampling_rate", default=22050, type=int)
    # parser.add_argument("--is_fp16", action="store_true")

    args = parser.parse_args()
    
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = False
    model = load_model(args.ckpt_pth )
    output = infer(args.text, model)
    npy_ary = output[1]
    waveglow = torch.load(args.waveglow_path, map_location=torch.device('cpu'))['model']
    waveglow = waveglow.remove_weightnorm(waveglow)
    # waveglow.cuda().eval()
    waveglow.eval()
    
    # if args.is_fp16:
    #     from apex import amp
    #     waveglow, _ = amp.initialize(waveglow, [], opt_level="O3")
    
    save_waveglow(npy_ary,args.filename, waveglow,args.sigma, args.output_dir, args.sampling_rate, False)
    # print(output)
    
    # if args.img_pth != '':
    #     plot(output, args.img_pth)
    # if args.wav_pth != '':
    #     audio(output, args.wav_pth)
    # if args.npy_pth != '':
    #     save_mel(output, args.npy_pth)
