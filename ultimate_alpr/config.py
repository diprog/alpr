# https://www.doubango.org/SDKs/anpr/docs/Configuration_options.html
JSON_CONFIG = {
    "debug_level": "info",
    "debug_write_input_image_enabled": False,
    "debug_internal_data_path": ".",

    "num_threads": -1,
    "gpgpu_enabled": True,
    "max_latency": -1,

    "klass_vcr_gamma": 1.5,

    "detect_roi": [0, 0, 0, 0],
    "detect_minscore": 0.7,

    "car_noplate_detect_min_score": 0.8,

    "pyramidal_search_enabled": True,
    "pyramidal_search_sensitivity": 1.0,
    "pyramidal_search_minscore": 0.7,
    "pyramidal_search_min_image_size_inpixels": 800,

    "recogn_rectify_enabled": True,
    "recogn_minscore": 0.7,
    "recogn_score_type": "min"
}

# Путь к папке с ресурсами
assets = "assets"

# Определение алфавита распознавания (latin, korean, chinese...)
charset = "latin"

# Вкючение опции определения машин без номерных знаков
car_noplate_detect_enabled = True

# Включение опции улучшения изображения для ночного видения (IENV)
# Подробная информация об IENV на https://www.doubango.org/SDKs/anpr/docs/Features.html#image-enhancement-for-night-vision-ienv.
# По умолчанию значение true для x86-64 и false для ARM.
ienv_enabled = True

# Включение OpenVINO. Если отключено, будет использоваться TensorFlow.
openvino_enabled = False

# Определение устройства OpenVINO, которое будет использоваться (CPU, GPU, FPGA...)
# Подробная информация на https://www.doubango.org/SDKs/anpr/docs/Configuration_options.html#openvino-device
openvino_device = "CPU"

# Включение ускорения NPU (Neural Processing Unit)
npu_enabled = True

# Включение функции определения страны номерного знака (LPCI)
# Подробная информация на https://www.doubango.org/SDKs/anpr/docs/Features.html#license-plate-country-identification-lpci
klass_lpci_enabled = False

# Включение функции определения цвета автомобиля (VCR)
# Подробная информация на https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-color-recognition-vcr
klass_vcr_enabled = False

# Включение функции распознавания марки и модели автомобиля (VMMR)
# Подробная информация на https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-make-model-recognition-vmmr
klass_vmmr_enabled = False

# Включение функции определение типа кузова транспорта (VBSR)
# Подробная информация на https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-body-style-recognition-vbsr
klass_vbsr_enabled = False

# Путь к файлу лицензионного токена
tokenfile = ""

# Данные лицензионного токена в формате Base64
license_token_data = ""

JSON_CONFIG["assets_folder"] = assets
JSON_CONFIG["charset"] = charset
JSON_CONFIG["car_noplate_detect_enabled"] = car_noplate_detect_enabled
JSON_CONFIG["ienv_enabled"] = ienv_enabled
JSON_CONFIG["openvino_enabled"] = openvino_enabled
JSON_CONFIG["openvino_device"] = openvino_device
JSON_CONFIG["npu_enabled"] = npu_enabled
JSON_CONFIG["klass_lpci_enabled"] = klass_lpci_enabled
JSON_CONFIG["klass_vcr_enabled"] = klass_vcr_enabled
JSON_CONFIG["klass_vmmr_enabled"] = klass_vmmr_enabled
JSON_CONFIG["klass_vbsr_enabled"] = klass_vbsr_enabled
# JSON_CONFIG["license_token_data"] = 'ABTPWw8ABQQBBAECAAj/BQQBAAJtgbYOOwQICSUCPDIJJyVyDi4sX2QoOCEyNzQ3IVtpOQJYfHBoKT0dIy5kd3dhegQAAUFi8XNSV1cxPU4BCQUGAAgEBARFazADFEVzHQsDKzlqZklESAQBRG97Yg=='
