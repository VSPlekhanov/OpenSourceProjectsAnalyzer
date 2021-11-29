FROM openkbs/jdk-mvn-py3
ENV LD_BIND_NOW=1
RUN pip install PyGithub
RUN sudo npm install -g n
RUN sudo n 16.10
RUN sudo npm install -g @angular/cli
WORKDIR /usr/src/OpenSourceProjectsAnalyzer
COPY . .
EXPOSE 4200
EXPOSE 8080
CMD sudo sh wrapper_script.sh
#CMD ls