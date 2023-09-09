### Build the extension
https://github.com/DoubangoTelecom/ultimateALPR-SDK/blob/master/python/README.md
```bash
python ../../../python/setup.py build_ext --inplace -v
```
0F86A701000048B84661696C65642074
### Install python dependencies
```angular2html
pip install Pillow cython opencv-python
```

### Install required linux packages
```bash
sudo apt install ffmpeg libsm6 libxext6 udev -y
```