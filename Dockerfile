FROM python:3.9
WORKDIR /ramen
RUN git clone https://github.com/zangobot/secml_malware
RUN pip install -r /ramen/secml_malware/requirements.txt
RUN pip install torch torchvision
RUN pip install -e /ramen/secml_malware
RUN pip install ipython
