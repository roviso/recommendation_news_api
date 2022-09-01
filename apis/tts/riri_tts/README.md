
Compatible Pytorch and cuda

pip3 install torch==1.8.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html

for cuda-11.7


tensorboard dev upload --logdir logdir/log_riri_final




# Tacotron2-PyTorch
Yet another PyTorch implementation of [Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions](https://arxiv.org/pdf/1712.05884.pdf). The project is highly based on [these](#References). I made some modification to improve speed and performance of both training and inference.

## TODO
- [x] Add Colab demo.
- [x] Update README.
- [x] Upload pretrained models.
- [x] Compatible with [WaveGlow](https://github.com/NVIDIA/waveglow) and [Hifi-GAN](https://github.com/jik876/hifi-gan).

## Requirements
- Python >= 3.5.2
- torch >= 1.0.0
- numpy
- scipy
- pillow
- inflect
- librosa
- Unidecode
- matplotlib
- tensorboardX

## Preprocessing
Currently only support [LJ Speech](https://keithito.com/LJ-Speech-Dataset/). You can modify `hparams.py` for different sampling rates. `prep` decides whether to preprocess all utterances before training or online preprocess. `pth` sepecifies the path to store preprocessed data.

## Training
1. For training Tacotron2, run the following command.
```bash
python3 train.py \
    --data_dir=<dir/to/dataset> \
    --ckpt_dir=<dir/to/models>
```

2. If you have multiple GPUs, try [distributed.launch](https://pytorch.org/docs/stable/distributed.html#launch-utility).
```bash
python -m torch.distributed.launch --nproc_per_node <NUM_GPUS> train.py \
    --data_dir=<dir/to/dataset> \
    --ckpt_dir=<dir/to/models>
```
Note that the training batch size will become <NUM_GPUS> times larger.

3. For training using a pretrained model, run the following command.
```bash
python3 train.py \
    --data_dir=<dir/to/dataset> \
    --ckpt_dir=<dir/to/models> \
    --ckpt_pth=<pth/to/pretrained/model>
```

python3 train.py --data_dir='LJSpeech-1.1'  --ckpt_dir='ckpt' --log_dir='logdir'

python3 train.py --data_dir='LJSpeech-1.1'  --ckpt_dir='ckpt' --log_dir='logdir' --ckpt_pth='ckpt/ckpt_200000'

python3 train.py --data_dir='ne_np_female'  --ckpt_dir='ckpt' --log_dir='logdir'

python3 train.py --data_dir='ne_np_female'  --ckpt_dir='ckpt' --log_dir='logdir/log_jul_21' --ckpt_pth='ckpt/ckpt_nepali'


python3 train.py --data_dir='riri_nepali'  --ckpt_dir='ckpt' --log_dir='logdir/log_riri_final' --ckpt_pth='ckpt/ckpt_riri_final'


python3 train.py --data_dir='riri_nepali'  --ckpt_dir='ckpt' --log_dir='logdir/log_nepali_riri_fine_10000' --ckpt_pth='ckpt/ckpt_nepali_riri_fine_trained_10000'


4. For using Tensorboard (optional), run the following command.
```bash
python3 train.py \
    --data_dir=<dir/to/dataset> \
    --ckpt_dir=<dir/to/models> \
    --log_dir=<dir/to/logs>
```
You can find alinment images and synthesized audio clips during training. The text to synthesize can be set in `hparams.py`.

## Inference
- For synthesizing wav files, run the following command.


    
```bash
python3 inference.py \
    --ckpt_pth='ckpt/ckpt_5' \
    --img_pth='imgdir' \
    --npy_pth='npydir' \
    --wav_pth='wavdir/result' \
    --text='For although the Chinese took impressions from wood blocks engraved in relief for centuries before the woodcutters of the Netherlands.'
```

python3 inference.py --ckpt_pth='ckpt/ckpt_200000' --text='Tacotron is awesome.' --npy_pth='npydir/npydir'

python3 inference.py --ckpt_pth='ckpt/ckpt_nepali' --img_pth='imgdir/result' --text='रेडियो नेपालमा कार्यरत रहँदा मास्टर रत्नदास प्रकाश निकै लोकप्रिय थिए' --npy_pth='npydir/npydir' --wav_pth='wavdir/result_nepali' 


python3 inference.py --ckpt_pth='ckpt/ckpt_riri_final' --img_pth='imgdir/result' --text='तनाबैइ तनाब छ गोजी मा दुइ रुपिया छैन। तनाबैइ तनाब छ गोजी मा दुइ रुपिया छैन तनाबैइ तनाब छ गोजी मा दुइ रुपिया छैन।  ' --npy_pth='npydir/npydir' --wav_pth='wavdir/result_riri_final_test' 


python3 inference.py --ckpt_pth='ckpt/ckpt_riri_final' --img_pth='imgdir/result' --text='रेडियो नेपालमा कार्यरत रहँदा मास्टर रत्नदास प्रकाश निकै लोकप्रिय थिए।  ' --npy_pth='npydir/npydir' --wav_pth='wavdir/ckpt_riri_final' 

python3 inference.py --ckpt_pth='ckpt/ckpt_riri_final' --img_pth='imgdir/result' --text='काठमाडौं : अमेरिकी सहायक विदेशमन्त्री डोनाल्ड लूले आज उच्चस्तरीय राजनीतिक भेटवार्ता गर्ने भएका छन्। ।  ' --npy_pth='npydir/npydir' --wav_pth='wavdir/ckpt_riri_news_test' 


python3 inference.py --ckpt_pth='ckpt/ckpt_riri_24k_16bs_392431' --img_pth='imgdir/result' --text='उनले आज प्रधानमन्त्री शेरबहादुर देउवा र परराष्ट्रमन्त्री नारायण खड्कासँग भेटवार्ता गर्ने कार्यतालिका छ। आज दिउँसो साढे ३ बजे प्रधानमन्त्री शेरबहादुर देउवासँग भेटवार्ता हुने कार्यसूची रहेको प्रधानमन्त्री देउवाका प्रेस सल्लाहकार गोविन्द परियारले जानकारी दिए। त्यसअघि परराष्ट्रमन्त्री खड्कासँग भेटवार्ताको कार्यसूची रहेको परराष्ट्र मन्त्रालयले जनाएको छ।लु गत मंसिरमा पनि नेपाल आएका थिए। नेपाल सरकारले अमेरिकी स्टेट पार्टनरसिप प्रोग्राम (एसपीपी) लाई अघि नबढाउने निर्णय गरेको एक महिनापछि लु काठमाडौं आएका हुन्। सरकारले गत असार ६ मा एसपीपी अघि नबढाउने निर्णय गरे पनि अमेरिकालाई पत्राचार गरेको छैन।' --npy_pth='npydir/npydir' --wav_pth='wavdir/ckpt_riri_news_long_test' 



## Pretrained Model
You can download pretrained models from [Realeases](https://github.com/BogiHsu/Tacotron2-PyTorch/releases). The hyperparameter for training is also in the directory. All the models were trained using 8 GPUs.

## Vocoder
A vocoder is not implemented. But the model is compatible with [WaveGlow](https://github.com/NVIDIA/waveglow) and [Hifi-GAN](https://github.com/jik876/hifi-gan). Check the Colab demo for more information. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BogiHsu/Tacotron2-PyTorch/blob/master/inference.ipynb)

## References
This project is highly based on the works below.
- [Tacotron2 by NVIDIA](https://github.com/NVIDIA/tacotron2)
- [Tacotron by r9y9](https://github.com/r9y9/tacotron_pytorch)
- [Tacotron by keithito](https://github.com/keithito/tacotron)




python inference_glow.py --ckpt_pth="ckpt/ckpt_riri_24k_16bs_421244" --filename="result_t" --text="१७ लाख अष्ट्रेलियालीमा मिर्गौला रोगको प्रारम्भिक लक्षण भएको जनाइएको छ।  अस्ट्रेलियन इन्स्टिच्युट अफ हेल्थ एण्ड वेलफेयर (एआइएचडब्ल्यू) ले सार्वजनिक गरेको तथ्यांकमा मिर्गौला प्रतिस्थापन थेरापी (केटिआर) आवश्यक पर्ने अस्ट्रेलियालीहरूको संख्या विगत २० वर्षमा दोब्बरभन्दा बढीले वृद्धि भएको सरकारी तथ्यांकबाट खुलासा भएको हो।" --output_dir="wavdir/" --waveglow_path="waveglow_ckpt/waveglow_40000" --sigma=0.6 --sampling_rate=22050 


C:\Users\User\AppData\Local\Temp\CUDA