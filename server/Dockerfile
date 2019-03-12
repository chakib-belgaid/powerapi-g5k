FROM chakibmed/powerapi:base
# RUN pip install pandas pymongo 
ADD . . 
RUN pip install --user -r  requirements.txt
ENTRYPOINT ["python","server.py"]
# CMD ["Python", "server.py"]











