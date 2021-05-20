import collections
import logging
import os
from pickle import load
from threading import Thread, current_thread, enumerate as thrd_enum

from base.utils import ErrorCodes, Error, Directory, UploadStatus
from classifier.models import Upload

logger = logging.getLogger('APP')


def get_model_and_transformer():
    model_pickle = os.path.join(Directory.DIR_MODEL_ROOT_PATH,
                                'ss_email_classifier_model.pkl')
    transformer_pickle = os.path.join(Directory.DIR_MODEL_ROOT_PATH,
                                      'ss_email_classifier_data_transformer.pkl')
    label_pickle = os.path.join(Directory.DIR_MODEL_ROOT_PATH,
                                'ss_email_classifier_labels.pkl')

    if os.path.exists(model_pickle) and \
            os.path.exists(transformer_pickle) and os.path.exists(label_pickle):
        model = load(open(model_pickle, 'rb'))
        data_transformer = load(open(transformer_pickle, 'rb'))
        decoded_labels = load(open(label_pickle, 'rb'))
        return model, data_transformer, decoded_labels
    else:
        return None, None, None


def read_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, 'r') as f:
        document = f.read()

    return document


def pop_queue():
    if not os.path.exists(Directory.DIR_Q_PATH):
        os.mkdir(Directory.DIR_Q_PATH)
        return None
    file_map = None
    with os.scandir(Directory.DIR_Q_PATH) as dir_list:
        for entry in dir_list:
            if entry.is_file():
                if not file_map:
                    file_map = collections.defaultdict(str)
                file_map[entry.name] = read_file(entry.path)

    return file_map


def get_file_info(file_entries):
    data, valid_entries, invalid_entries = [], [], []
    for filename, document in file_entries.items():
        try:
            name_components = str(filename).split("_")
            if not name_components or len(name_components) < 3:
                # we need at least the upload obj id and username in the filename
                invalid_entries.append(filename)
            else:
                data.append(document)
                valid_entries.append({
                        "upload_id": int(name_components[0]),
                        "username": name_components[1],
                        "filename": filename
                })
        except BaseException as err:
            logger.debug(f"Exception while parsing file entries - {err}")
            invalid_entries.append(filename)
    return data, valid_entries, invalid_entries


def evaluate(data):
    if not data:
        return None
    model, data_transformer, decoded_labels = get_model_and_transformer()
    if not model:
        return None

    transformed_data = data_transformer.transform(data)
    predictions = model.predict(transformed_data)
    decoded_predictions = [decoded_labels[label] for label in predictions]
    return decoded_predictions


def save_values(predictions, file_entries):
    invalid_entries = []
    try:
        for i, pred in enumerate(predictions):
            file_obj = file_entries[i]
            upload_obj = Upload.objects.all().filter(pk=file_obj["upload_id"]).first()
            if not upload_obj:
                invalid_entries.append(file_obj)
                continue
            upload_obj.prediction = pred
            upload_obj.status = UploadStatus.UP_STATUS_PROCESSED
            upload_obj.save()
    except BaseException as err:
        logger.debug(f"Exception while saving values - {err}")
    return invalid_entries


def move_files(valid_entries, invalid_entries):
    def _move_helper(source_path, destination_path):
        if not os.path.exists(Directory.DIR_SUCCESS_PATH):
            os.mkdir(Directory.DIR_SUCCESS_PATH)
        if not os.path.exists(Directory.DIR_ERROR_PATH):
            os.mkdir(Directory.DIR_ERROR_PATH)
        if not os.path.exists(source_path):
            return False
        try:
            os.rename(source_path, destination_path)
            return True
        except BaseException as err:
            if isinstance(err, FileExistsError):
                os.remove(destination)
                os.rename(source, destination)
            else:
                logger.debug("Exception while moving file - {err}")
        return False

    for entry in valid_entries:
        source = os.path.join(Directory.DIR_Q_PATH, entry["filename"])
        destination = os.path.join(Directory.DIR_SUCCESS_PATH, entry["filename"])
        _move_helper(source, destination)

    for entry in invalid_entries:
        if isinstance(entry, str):
            source = os.path.join(Directory.DIR_Q_PATH, entry)
            destination = os.path.join(Directory.DIR_ERROR_PATH, entry)
        else:
            source = os.path.join(Directory.DIR_Q_PATH, entry["filename"])
            destination = os.path.join(Directory.DIR_ERROR_PATH, entry["filename"])
        _move_helper(source, destination)


def run_classifier():
    if current_thread().getName() is not "model_thread":
        logger.debug("wrong thread")
        logger.debug(Error(ErrorCodes.E_WRONG_THREAD, "Attempting to initiate model classifier on "
                                                      "wrong thread. Aborted!"))

    try:
        while True:
            file_entries = pop_queue()
            if not file_entries:
                break
            data, valid_entries, invalid_entries = get_file_info(file_entries)
            predictions = evaluate(data)
            invalid_entries.extend(save_values(predictions, valid_entries))
            move_files(valid_entries, invalid_entries)
    except BaseException as err:
        logger.debug(f"Exception occurred while running classifier - {err}")


def init_model():
    try:
        thread = Thread(target=run_classifier, name="model_thread", daemon=True)
        start_thread = True
        for th in thrd_enum():
            if th.name == thread.name and th.is_alive():
                start_thread = False
        if start_thread:
            thread.start()
    except BaseException as err:
        logger.debug(f"Exception while initializing model - {err}")


if __name__ == "__main__":
    init_model()
