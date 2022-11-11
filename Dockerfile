FROM opencvcourses/opencv-docker
WORKDIR /home
EXPOSE 8000
COPY ./script ./script
RUN pip install -r ./script/requirements.txt
CMD ["python", "script/server.py"]
