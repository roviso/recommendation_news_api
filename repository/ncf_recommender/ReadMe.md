## To train the model:
    device = [cpu,cuda]
    
## load and save model:
python model_train.py --device cuda --load_model --save_model --epochs 55 --bs 24 --lr 0.001

## save model only
python model_train.py --device cuda --no-load_model --save_model --epochs 55 --bs 24 --lr 0.001

## Load model only
python model_train.py --device cuda --no-save_model --epochs 55 --bs 24 --lr 0.001

## dont save and load model
python model_train.py --device cuda --no-load_model --no-save_model --epochs 55 --bs 24 --lr 0.001



