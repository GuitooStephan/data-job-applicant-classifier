from hr.preprocess import (
    load_object, predict, 
    TARGET_ENCODER_FILENAME,
)

def make_predictions(predict_data_raw):
    y_pred = predict(predict_data_raw)
    le = load_object(TARGET_ENCODER_FILENAME)
    return le.inverse_transform(y_pred)
